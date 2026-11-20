# PDSP – Pharmacy Duty Scheduling Problem

Progetto fatto with [@Mottyna](https://github.com/Mottyna)

---

## Descrizione del problema

Progetto per il corso di **Metodi di Ottimizzazione** (gruppo da 2 persone; varianti per gruppi da 3).
urnistica delle farmacie: in un territorio diviso in quartieri sono presenti alcune farmacie.
Assimilando ogni quartiere q a un punto, conosciamo la distanza $$t_{qf}$$ da ogni quartiere q e
una farmacia f, e la distanza massima $$\sigma$$ tra una farmacia e un quartiere affinchè gli abitanti
di q si servano da f. Se $$t_{qf}≤\sigma$$ diciamo che f copre q. Conosciamo inoltre la distanza $$\pi_{fg}$$ fra
due farmacie f,g quando sono lontane fra loro meno di $$\delta$$. Si deve decidere per ogni giorno
di un periodo H (es H=1..28) quali farmacie fanno il servizio notturno in modo che ogni
giorno ogni quartiere sia coperti da almeno una farmacia aperta, e che una stessa farmacia
non sia di turno durante H per più di k volte. La qualità di un “turno” (insieme di farmacie
aperte di notte nello stesso giorno) è la somma per ogni coppia di farmacie f,g di ($$\delta - \pi_{fg}$$)
quando sono vicine. Si cerca l’insieme di turni di costo minimo. 

**Variante 1**: risolvere con la generazione di colonne.

**Variante 2**: ogni farmacia non può fare più di k turni ogni s giorni.

---

## Modello matematico

### Rappresentazione

Ogni farmacia è un vettore binario indicizzato sui giorni:

$$x_{fh} \in \{0,1\}, \quad f \in F,\ h \in H$$

Esempio con $|H|=3$: `farmacia1 = [0,1,0]` → è di turno solo il giorno 2.

Questa rappresentazione semplifica i vincoli sui turni (in particolare "$k$ turni ogni $s$ giorni").

### Precalcolo dei dati costanti
Prima del modello si precalcolano tutte le quantità che non dipendono dalle variabili:

- **Copertura**: $C(q) = \{ f \in F : t_{qf} \le \sigma \}$, cioè per ogni quartiere le farmacie che lo coprono
- **Costi di coppia** (solo per $f<g$, per non contare due volte le coppie ordinate):

$$c_{fg} = \begin{cases} \delta - \pi_{fg} & \text{se } \pi_{fg} \text{ è definita } (\pi_{fg} < \delta) \\ 0 & \text{altrimenti} \end{cases}$$

Si considerano solo le coppie con $c_{fg} > 0$.

### Funzione obiettivo (forma quadratica)

$$\min \sum_{h \in H} \sum_{\substack{f<g \\ c_{fg}>0}} c_{fg}\, x_{fh}\, x_{gh}$$

Il prodotto $x_{fh}x_{gh}$ è non lineare, quindi lo linearizziamo.

### Linearizzazione
Introduciamo $y_{fgh} \in [0,1]$ (o binaria), pari a 1 se $f$ e $g$ sono entrambe di turno il giorno $h$:

$$y_{fgh} \ge x_{fh} + x_{gh} - 1 \qquad \forall h,\ \forall f<g \text{ con } c_{fg}>0$$

Poiché $c_{fg} > 0$ e l'obiettivo è di minimo, non servono i vincoli inversi ($y \le x_{fh}$, $y \le x_{gh}$): il solver terrà $y$ al valore più basso consentito.

### Modello lineare completo

$$\min \sum_{h \in H} \sum_{\substack{f<g \\ c_{fg}>0}} c_{fg}\, y_{fgh}$$

soggetto a:

| Vincolo | Formula |
|---|---|
| Copertura | $\sum_{f \in C(q)} x_{fh} \ge 1 \quad \forall q \in Q,\ \forall h \in H$ |
| Max $k$ turni | $\sum_{h \in H} x_{fh} \le k \quad \forall f \in F$ |
| Linearizzazione | $y_{fgh} \ge x_{fh} + x_{gh} - 1$ |
| Dominio | $x_{fh} \in \{0,1\},\ y_{fgh} \ge 0$ |

**Variante 2** – al massimo $k$ turni ogni $s$ giorni (finestra scorrevole):

$$\sum_{h'=h}^{h+s-1} x_{fh'} \le k \qquad \forall f \in F,\ \forall h = 1,\dots,|H|-s+1$$

---

## Struttura del repository

*   **`model.mos`**: Modello principale FICO Xpress Mosel per la formulazione standard del PDSP.
*   **`model-lazy.mos`**: Modello Mosel con implementazione di *lazy constraints* per la gestione efficiente dei vincoli.
*   **`/dati/`**: Contiene i file di input grezzi (farmacie, centroidi dei quartieri) e gli script Python per la generazione delle matrici di distanza.
    *   `farmacie.csv`: Coordinate e dati delle farmacie del comune di Ferrara.
    *   `centroidi_quartieri_ferrara.csv`: Coordinate dei centroidi dei quartieri.
    *   `farmacie_triangolare.dat` e `t_dist.dat`: Matrici delle distanze formattate per Mosel.
*   **`/test/`**: Script Mosel (`test_senza_finestra.mos` e `test_con_finestra.mos`) per eseguire batterie di test parametrici.
*   **`/risultati_senza_finestra/` e `/risultati_finestra/`**: File CSV e file log di testo (`soluzioni_*.txt`) generati dalle esecuzioni del solutore.
*   **`/grafici_pdsp/` e `/grafici_pdsp_finestra/`**: Cartelle in cui vengono salvati i report grafici generati (formato `.png` e `.pdf`).
*   **`turnistica-farmacie.pdf`**: Relazione finale presentata all'esame di Metodi di Ottimizzazione.

---

## Guida all'utilizzo del progetto

Il progetto include cinque script Python principali suddivisi in tre fasi della pipeline di lavoro: **preparazione dati**, **integrazione risultati** e **visualizzazione grafica**.

### 1. Preparazione (`/dati/`)

Questi script trasformano i dati geografici raw (coordinate lat/lon) nelle matrici di distanza utilizzate direttamente dai modelli Mosel (`.dat`).

*   #### `dati/calcola_distanze_farmacie.py`
    *   **Descrizione:** Legge la posizione geografica delle farmacie da `farmacie.csv` e calcola la matrice delle distanze reciproche tra tutte le coppie di farmacie.
    *   **Uso:**
        ```bash
        cd dati
        python calcola_distanze_farmacie.py
        ```
    *   **Output:** Genera/aggiorna la struttura dati triangolare `farmacie_triangolare.dat` in formato leggibile da Xpress.

*   #### `dati/genera_t_qf.py`
    *   **Descrizione:** Calcola le distanze e i tempi stimati di percorrenza tra i centroidi dei quartieri di Ferrara (`centroidi_quartieri_ferrara.csv`) e le singole farmacie (`farmacie.csv`).
    *   **Uso:**
        ```bash
        cd dati
        python genera_t_qf.py
        ```
    *   **Output:** Produce il file `t_dist.dat` contenente le matrici di copertura quartiere-farmacia per il vincolo di accessibilità del servizio.

---

### 2. Elaborazione dei risultati

*   #### `integra_risultati.py`
    *   **Descrizione:** Processa i file di output generati dalle simualzioni con finestre temporali (`risultati_test_finestra.csv` e `soluzioni_test_finestra.txt`) unificando i tempi di calcolo, lo stato di ottimalità, i costi totali e i valori dei parametri per ciascun test.
    *   **Uso:**
        ```bash
        python integra_risultati.py
        ```
    *   **Output:** Genera il file unico `risultati_finestra/risultati_test_finestra_integrati.csv`.

---

### 3. Generazione dei grafici

Requisiti: `matplotlib`, `pandas`, `numpy`, `seaborn`.

*   #### `grafici_pdsp.py`
    *   **Descrizione:** Analizza i risultati del **modello base (senza finestre temporali)** attingendo dai file presenti in `risultati_senza_finestra/`.
    *   **Uso:**
        ```bash
        python grafici_pdsp.py
        ```
    *   **Output (salvati in `grafici_pdsp/`):**
        *   `1_k_minimo_per_sigma.png/.pdf`: Numero minimo del parametro $k$ al variare del parametro di tolleranza $\sigma$.
        *   `2_costo_vs_delta.png/.pdf`: Relazione tra il valore di costo totale e la distanza minima $\delta$.
        *   `3_mappa_soglia_delta.png/.pdf`: Mappa heat-map della fattibilità in base alla soglia $\delta$.
        *   `4_cadenza_aperture.png/.pdf`: Distribuzione delle aperture.
        *   `5_coppie_vicine_delta.png/.pdf`: Analisi dei vincoli di prossimità per farmacie vicine.

*   #### `grafici_pdsp_finestra.py`
    *   **Descrizione:** Genera i grafici per il **modello con finestre temporali** utilizzando il file integrato `risultati_test_finestra_integrati.csv`.
    *   **Uso:**
        ```bash
        python grafici_pdsp_finestra.py
        ```
    *   **Output (salvati in `grafici_pdsp_finestra/`):**
        *   `1_esiti_pdsp.png/.pdf`: Classificazione degli esiti dell'ottimizzazione.
        *   `2_costi_pdsp.png/.pdf`: Confronto della funzione obiettivo nei diversi scenari di test.
        *   `3_successo_pdsp.png/.pdf`: Tasso di successo dell'algoritmo al variare della dimensione della finestra temporale.

---


## Workflow

Se si desidera rigenerare completamente l'analisi da zero (magari a partire da dati diversi), seguire questi passaggi in sequenza:

1. **Generazione dei file di input `.dat`:**
   ```bash
   python dati/calcola_distanze_farmacie.py
   python dati/genera_t_qf.py
   ```

2. **Esecuzione dei modelli:**
   * Aprire FICO Xpress Workbench ed eseguire `model.mos` o `model-lazy.mos`.
   * Oppure eseguire gli script di test batch in `/test/` per generare i risultati.

3. **Integrazione dei dati delle simulazioni:**
   ```bash
   python integra_risultati.py
   ```

4. **Produzione del set di grafici:**
   ```bash
   python grafici_pdsp.py
   python grafici_pdsp_finestra.py
   ```

---

## Requisiti di sistema e librerie Python

* **Python 3.8+**
* Librerie Python consigliate:
  ```bash
  pip install pandas numpy matplotlib seaborn
  ```
* **FICO Xpress Optimizer** (con supporto Mosel) per l'esecuzione dei file `.mos`.
# PDSP – Pharmacy Duty Scheduling Problem

📎 [Presentazione](https://canva.link/dy5vi8qopmeiahs)

Progetto fatto with [@Mottyna](https://github.com/Mottyna)

---

## 1. Descrizione del problema

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

## 2. Modello matematico
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

## 3. Note implementative (Mosel/Xpress)

- Il valore $\sigma$ è un **parametro** in input, non una variabile: si precalcola $C(q)$ una volta sola.
- **Matrice dei costi** vs **dizionario**: le variabili "che costano" (coppie con $c_{fg}>0$) sono poche, quindi conviene un array sparso/dizionario indicizzato solo sulle coppie vicine invece di una matrice $|F|\times|F|$ piena.
- Le variabili $y_{fgh}$ vanno create **solo per le coppie con $c_{fg}>0$**, usando `create(...)` su array dinamici.
- Considerare solo le coppie con $f<g$: le coppie ordinate si contano una volta sola.
- $f$ e $g$ sono entrambe indicizzate su $H$.

---

## 4. COMUNICAZIONE

il modello lazy non genera tutti i vincoli di linearizzazione in una volta all'inizio del programma, li 
genera solo quando si accorge che sono stati violati dalla versione rilassata del problema.
Continua in un loop di minimizzazione, check se violi dei vincoli finche' nessun vincolo e' violato

---

## 5. Test da fare

- doro ha poche farmacie - più costo per le farmacie
- test base con datafile completo + datafile argento
- test con sliding windows sia datafile completo e argento 
- possiamo solo pensare alle colonne non c'è bisogno del test
- test con output grafico con cambio variabili -- possiamo automatizzare

---

## codice test forall

(!
  test_sigma_delta.mos
  --------------------
  Test parametrico: risolve il PDSP per ogni combinazione
  (sigma, delta) e salva costo ottimo + statistiche su CSV.

  Sigma: raggio copertura quartiere-farmacia  (t_qf <= sigma)
  Delta: soglia distanza tra farmacie         (pi_fg < delta → coppia vicina)
!)

model "test_sigma_delta"
  uses "mmxprs", "mmsystem"

  ! --- includi qui il tuo datafile con t_qf, pi_fg, N_Q, N_F, H, k ---
  ! (adatta i nomi alle tue dichiarazioni esistenti)

  declarations
    ! Griglia di test per sigma e delta
    N_SIGMA = 5
    N_DELTA = 5

    SIGMA_VALS : array(1..N_SIGMA) of real
    DELTA_VALS : array(1..N_DELTA) of real

    ! Indici di scorrimento (dichiarati qui, MAI dentro forall)
    si : integer
    di : integer

    ! Variabili per risultati del singolo run
    costo_ottimo : real
    n_coppie     : integer
    n_coperti    : integer

    fo : integer
  end-declarations

  ! Valori della griglia (modifica secondo il tuo dominio)
  SIGMA_VALS(1) := 0.8  ; SIGMA_VALS(2) := 1.0  ; SIGMA_VALS(3) := 1.2
  SIGMA_VALS(4) := 1.5  ; SIGMA_VALS(5) := 2.0

  DELTA_VALS(1) := 0.5  ; DELTA_VALS(2) := 0.8  ; DELTA_VALS(3) := 1.0
  DELTA_VALS(4) := 1.2  ; DELTA_VALS(5) := 1.5

  ! Apri CSV di output
  fo := fopen("risultati_test.csv", F_OUTPUT)
  fwriteln(fo, "sigma,delta,costo_ottimo,n_coppie_vicine,n_quartieri_coperti")

  ! -----------------------------------------------------------------------
  ! DOPPIO LOOP: sigma fisso, delta scorre; poi sigma avanza
  ! -----------------------------------------------------------------------
  forall(si in 1..N_SIGMA) do
    forall(di in 1..N_DELTA) do

      ! 1. Aggiorna parametri globali usati dal modello
      sigma := SIGMA_VALS(si)
      delta := DELTA_VALS(di)

      ! 2. Ricalcola C(q) e costi c_fg con i nuovi sigma/delta
      !    (chiama la tua procedura di precalcolo oppure inline)
      forall(q in 1..N_Q, f in 1..N_F)
        copertura(q,f) := if(t(q,f) <= sigma, 1, 0)

      n_coppie := 0
      forall(f in 1..N_F, g in f+1..N_F) do
        if pi(f,g) < delta then
          c(f,g)   := delta - pi(f,g)
          n_coppie += 1
        else
          c(f,g) := 0
        end-if
      end-do

      ! 3. Ricostruisci variabili y solo per coppie attive
      !    (se usi create() su array dinamici, ricreali qui)

      ! 4. Risolvi
      minimize(obiettivo)
      costo_ottimo := getobjval

      ! 5. Conta quartieri effettivamente coperti
      n_coperti := 0
      forall(q in 1..N_Q) do
        if getsol(sum(f in 1..N_F) copertura(q,f) * x(f,1)) >= 1 then
          n_coperti += 1
        end-if
      end-do

      ! 6. Scrivi riga CSV
      fwriteln(fo,
        string(sigma)       + "," +
        string(delta)       + "," +
        string(costo_ottimo) + "," +
        string(n_coppie)    + "," +
        string(n_coperti)
      )

      writeln("sigma=", sigma, "  delta=", delta,
              "  costo=", costo_ottimo,
              "  coppie=", n_coppie)

    end-do  ! fine loop delta
  end-do    ! fine loop sigma

  fclose(fo)
  writeln("Fine. Risultati in: risultati_test.csv")

end-model



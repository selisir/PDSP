# PDSP
Metodi di Ottimizzazione project - PDSP (Pharmacy Duty Scheduling Problem)

Turnistica delle farmacie: in un territorio diviso in quartieri sono presenti alcune farmacie.
Assimilando ogni quartiere q a un punto, conosciamo la distanza $$t_{qf}$$ da ogni quartiere q e
una farmacia f, e la distanza massima $$\sigma$$ tra una farmacia e un quartiere affinchè gli abitanti
di q si servano da f. Se $$t_{qf}≤\sigma$$ diciamo che f copre q. Conosciamo inoltre la distanza $$\pi_{fg}$$ fra
due farmacie f,g quando sono lontane fra loro meno di $$\delta$$. Si deve decidere per ogni giorno
di un periodo H (es H=1..28) quali farmacie fanno il servizio notturno in modo che ogni
giorno ogni quartiere sia coperti da almeno una farmacia aperta, e che una stessa farmacia
non sia di turno durante H per più di k volte. La qualità di un “turno” (insieme di farmacie
aperte di notte nello stesso giorno) è la somma per ogni coppia di farmacie f,g di ($$\delta - \pi_{fg}$$)
quando sono vicine. Si cerca l’insieme di turni di costo minimo. Per 2 persone. Variante 1
per 3 persone: risolvere con la generazione di colonne. Variante 2 per 3 persone: ogni
farmacia non può fare più di k turni ogni s giorni.


ipotesi modello matematico
- farmacie: variabili [0,1] su vettore H
- es: farmacia1: [0,1,0] - la farmacia è aperta il giorno 2
- questo semplifica il calcolo del vincolo di k turni in s giorni
- per ogni quartiere devo sapere quali sono le righe farmacia, per ogni giorno, sommando i giorni, ho almeno 1 -> quartiere mi mappa delle righe

modello:
- copertura: $$\forall q \forall h \exists f\left[ h \right] = 1 t.c. t_{qf} \le \sigma$$
- $$\sigma$$ variabile da decidere - ci precalcoliamo tutti i costi "costanti" prima del programma
- costo: $$c: c_{fg}=\sigma - \pi_{fg}$$ se $$\exists \pi_{fg}$$, altrimenti 0

- FUNZIONE OBIETTIVO non linearizzata
- fob: $$min\\left(\sum_{h=1}^{H}\left(c_{fg}\right)f\left[h\right]g\left[h\right]\right)$$
- problema: la moltiplicazione f[h]*g[h] è costosa, possiamo usare una variabile $$var_{fg}$$ che se f[h]+g[h]-1>=1 è 1, altrimenti 0. 
- DOMANDA: va bene?

- k turni in s giorni --> k e s sono da decidere
- usare sliding windows --> es facciamo 7 giorni, non deve superare (in 7 giorni) 4 turni 
  

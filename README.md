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

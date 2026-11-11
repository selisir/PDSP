"""
Generatore Grafici Analisi Finestra - Stile PDSP.
Nessuna dipendenza esterna necessaria se non pandas e matplotlib.

Uso:   pip install pandas matplotlib
       python grafici_finestra_pdsp.py
Output: cartella ./grafici_pdsp_finestra con i 3 grafici in PNG e PDF,
        senza sfondo (trasparenti), senza titoli né etichette degli assi:
        solo legenda e numeri sul grafico.
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path("grafici_pdsp_finestra")
OUT.mkdir(exist_ok=True)

BLU, GRIGIO, TESTO = "#2575d4", "#b9b6ad", "#333333"

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#888888",
    "figure.dpi": 200,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
    "savefig.transparent": True,
})

def it(v, nd=None):
    """Formato numerico italiano (virgola decimale)."""
    s = f"{v:.{nd}f}" if nd is not None else f"{v:g}"
    return s.replace(".", ",")

def salva(fig, nome):
    fig.tight_layout()
    fig.savefig(OUT / f"{nome}.png", dpi=200, transparent=True)
    fig.savefig(OUT / f"{nome}.pdf", transparent=True)  # vettoriale
    plt.close(fig)
    print("Creato:", nome)

def genera_dataset():
    """Ricrea il dataset delle 324 combinazioni del test finestra."""
    records = []
    for k in [5, 10]:
        for sg in [3, 5, 7, 10, 15, 20]:
            for st in range(1, 4): 
                for sig in [2.5, 3.0, 3.5]:
                    for delt in [2.5, 3.0, 3.5]:
                        status = 'Infeasible'
                        cost = None
                        if sg == 20: status = 'Infeasible'
                        elif sig == 2.5: status = 'Infeasible'
                        elif k == 5 and sig == 3.0:
                            if delt == 2.5: status, cost = 'Ottimo (2)', 0.0
                            elif delt == 3.0: status, cost = 'Ottimo (2)', 1.5
                            elif delt == 3.5: status, cost = 'Timeout (4)', 8.0
                        elif k == 5 and sig == 3.5: status, cost = 'Ottimo (2)', 0.0
                        elif k == 10 and sg == 3 and sig == 3.0:
                            if delt == 2.5: status, cost = 'Ottimo (2)', 0.0
                            elif delt == 3.0: status, cost = 'Ottimo (2)', 0.0
                            elif delt == 3.5: status, cost = 'Ottimo (2)', 4.66
                        elif k == 10 and sig == 3.0: status = 'Infeasible'
                        elif k == 10 and sig == 3.5: status, cost = 'Ottimo (2)', 0.0
                        
                        records.append({'k_turni': k, 's_giorni': sg, 's_turni': st, 'sigma': sig, 'delta': delt, 'status': status, 'costo': cost})
    return pd.DataFrame(records)

def g1_esiti(df):
    etichette = ["Ottimo", "Limite di tempo", "Non ammissibile"]
    counts = [len(df[df['status'] == 'Ottimo (2)']), 
              len(df[df['status'] == 'Timeout (4)']), 
              len(df[df['status'] == 'Infeasible'])]
    
    colori = [BLU, GRIGIO, GRIGIO]
    tot = sum(counts)
    
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(etichette[::-1], counts[::-1], color=colori[::-1])
    for i, v in enumerate(counts[::-1]):
        ax.text(v + 5, i, f"{v:,} ({it(v / tot * 100, 1)}%)".replace(",", "."),
                va="center", color=TESTO)
    ax.set_xlim(0, max(counts) * 1.3)
    salva(fig, "1_esiti_pdsp")

def g2_costi(df):
    df3 = df[df['sigma'] == 3.0].dropna(subset=['costo'])
    delta_vals = [2.5, 3.0, 3.5]
    medie = [df3[df3['delta']==d]['costo'].mean() for d in delta_vals]
    massimi = [df3[df3['delta']==d]['costo'].max() for d in delta_vals]
    
    x = range(len(delta_vals))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.8))
    b1 = ax.bar([i - w / 2 for i in x], massimi, w, color=GRIGIO, label="Massimo")
    b2 = ax.bar([i + w / 2 for i in x], medie, w, color=BLU, label="Medio")
    
    for barre in (b1, b2):
        for b in barre:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width() / 2, h + 0.2,
                    it(h, 2) if h > 0 else "0", ha="center", fontsize=9)
            
    ax.set_xticks(list(x))
    ax.set_xticklabels([it(d, 1) for d in delta_vals])
    ax.legend(frameon=False)
    salva(fig, "2_costi_pdsp")

def g3_successo(df):
    s_giorni = [3, 5, 7, 10, 15, 20]
    pos = range(len(s_giorni))
    
    y25 = [df[(df['s_giorni']==sg) & (df['sigma']==2.5)]['status'].apply(lambda x: x != 'Infeasible').mean()*100 for sg in s_giorni]
    y30 = [df[(df['s_giorni']==sg) & (df['sigma']==3.0)]['status'].apply(lambda x: x != 'Infeasible').mean()*100 for sg in s_giorni]
    y35 = [df[(df['s_giorni']==sg) & (df['sigma']==3.5)]['status'].apply(lambda x: x != 'Infeasible').mean()*100 for sg in s_giorni]
    
    fig, ax = plt.subplots(figsize=(9, 4.8))
    
    for dati, nome, col, off in ((y35, "σ = 3,5", BLU, 8), 
                                 (y30, "σ = 3,0", "#8a8678", -15),
                                 (y25, "σ = 2,5", GRIGIO, 8)):
        ax.plot(pos, dati, "-o", color=col, lw=2.5, label=nome)
        for i, c in zip(pos, dati):
            if c > 0 or off > 0: 
                ax.annotate(it(c, 0) + "%", (i, c), textcoords="offset points",
                            xytext=(0, off), ha="center", fontsize=9)
        
    ax.set_xticks(list(pos))
    ax.set_xticklabels(s_giorni)
    ax.set_ylim(-10, 115)
    ax.legend(frameon=False, loc="center left")
    salva(fig, "3_successo_pdsp")

if __name__ == "__main__":
    print("Generazione dataset in corso...")
    df = genera_dataset()
    print("Creazione grafici...")
    g1_esiti(df)
    g2_costi(df)
    g3_successo(df)
    print(f"Fatto! I grafici sono stati salvati nella cartella: {OUT.resolve()}")
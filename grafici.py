"""
Generatore Grafici Analisi Finestra - Stile PDSP.

Uso:   pip install pandas matplotlib
       python grafici.py
Output: cartella ./grafici_pdsp_finestra con i 3 grafici in PNG e PDF,
        senza sfondo (trasparenti), senza titoli né etichette degli assi:
        solo legenda e numeri sul grafico.
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

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

def carica_dati(csv_path):
    """Legge e normalizza il dataset dal file CSV reale."""
    path = Path(csv_path)
    if not path.exists():
        print(f"ERRORE: Impossibile trovare il file '{csv_path}'.")
        sys.exit(1)
        
    df = pd.read_csv(path)
    
    # Normalizza le colonne in minuscolo
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Normalizza i valori dello status per i grafici
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str)
        mappatura = {
            '2': 'Ottimo (2)', '2.0': 'Ottimo (2)', 'ottimo': 'Ottimo (2)',
            '4': 'Timeout (4)', '4.0': 'Timeout (4)', 'timeout': 'Timeout (4)'
        }
        df['status'] = df['status'].replace(mappatura)
        df.loc[~df['status'].isin(['Ottimo (2)', 'Timeout (4)']), 'status'] = 'Infeasible'
        
    if 'costo' in df.columns:
        df['costo'] = pd.to_numeric(df['costo'], errors='coerce').fillna(0)
        
    return df

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
    # Solo combinazioni risolte (ottime o in timeout): le infeasible non hanno costo
    df3 = df[(df['sigma'] == 3.0) & (df['status'] != 'Infeasible')].dropna(subset=['costo'])
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
    
    df['status_clean'] = df['status'].astype(str).str.strip().str.lower()

    # 2. Calcoliamo le percentuali in modo più leggibile ed efficiente
    y25 = [df[(df['s_giorni'] == sg) & (df['sigma'] == 2.5)]['status_clean'].ne('infeasible').mean() * 100 for sg in s_giorni]
    y30 = [df[(df['s_giorni'] == sg) & (df['sigma'] == 3.0)]['status_clean'].ne('infeasible').mean() * 100 for sg in s_giorni]
    y35 = [df[(df['s_giorni'] == sg) & (df['sigma'] == 3.5)]['status_clean'].ne('infeasible').mean() * 100 for sg in s_giorni]
    
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
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "risultati_test_finestra_2_integrati.csv"
    print(f"Lettura dati da {csv_file} in corso...")
    df = carica_dati(csv_file)
    print("Creazione grafici...")
    g1_esiti(df)
    g2_costi(df)
    g3_successo(df)
    print(f"Fatto! I grafici sono stati salvati nella cartella: {OUT.resolve()}")
"""
Grafici del report PDSP (test parametrico e test «finestra»).
Tutti i dati vengono dai documenti analizzati.

Uso:   pip install matplotlib
       python grafici_pdsp.py
Output: cartella ./grafici_pdsp con 6 PNG (200 dpi) e 6 PDF (vettoriali).
"""
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path("grafici_pdsp")
OUT.mkdir(exist_ok=True)

BLU, GRIGIO, TESTO = "#2575d4", "#b9b6ad", "#333333"
plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#888888",
    "figure.dpi": 100,
})


def it(v, nd=None):
    """Formato numerico italiano (virgola decimale)."""
    s = f"{v:.{nd}f}" if nd is not None else f"{v:g}"
    return s.replace(".", ",")


def salva(fig, nome):
    fig.tight_layout()
    fig.savefig(OUT / f"{nome}.png", dpi=200)
    fig.savefig(OUT / f"{nome}.pdf")
    plt.close(fig)
    print("creato:", nome)


# 1) Esiti sulle 6.522 combinazioni (k, sigma, delta) ----------------------
def g1_esiti():
    etichette = ["Ottimo", "Limite di tempo",
                 "Non ammissibile: k troppo basso",
                 "Non ammissibile: σ ≤ 1 (copertura)"]
    valori = [4771, 11, 930, 810]
    colori = [BLU, GRIGIO, GRIGIO, GRIGIO]
    tot = sum(valori)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(etichette[::-1], valori[::-1], color=colori[::-1])
    for i, v in enumerate(valori[::-1]):
        ax.text(v + 60, i, f"{v:,} ({it(v / tot * 100, 1)}%)".replace(",", "."),
                va="center", color=TESTO)
    ax.set_xlim(0, 6200)
    ax.set_xlabel("Combinazioni (k, σ, δ)")
    ax.set_title("Il 73,3% delle 6.522 combinazioni ha una soluzione",
                 loc="left", fontweight="bold")
    salva(fig, "1_esiti_combinazioni")


# 2) k minimo ammissibile per sigma ---------------------------------------
def g2_k_minimo():
    sigma = ["1,5", "2,0", "2,5", "3,0", "≥ 3,5"]
    kmin = [30, 15, 10, 5, 2]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    barre = ax.bar(sigma, kmin, color=BLU, width=0.55)
    for b, v in zip(barre, kmin):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, v, ha="center")
    ax.set_xlabel("σ (km)")
    ax.set_ylabel("k minimo ammissibile")
    ax.set_title("Più σ è grande, meno turni k servono: da 30 a 2\n"
                 "(identico per tutti i δ; σ ≤ 1: nessuna soluzione)",
                 loc="left", fontweight="bold", fontsize=12)
    salva(fig, "2_k_minimo_per_sigma")


# 3) Costo medio e massimo per sigma --------------------------------------
def g3_costo_sigma():
    sigma = ["1,5", "2,0", "2,5", "3,0", "3,5", "4,0–7,5"]
    medio = [132.2, 33.4, 27.3, 4.2, 0.24, 0]
    massimo = [397.0, 118.9, 121.7, 84.6, 23.4, 0]
    x = range(len(sigma))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.8))
    b1 = ax.bar([i - w / 2 for i in x], massimo, w, color=GRIGIO, label="Massimo")
    b2 = ax.bar([i + w / 2 for i in x], medio, w, color=BLU, label="Medio")
    for barre in (b1, b2):
        for b in barre:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 4,
                    it(b.get_height()), ha="center", fontsize=9)
    ax.set_xticks(list(x))
    ax.set_xticklabels(sigma)
    ax.set_xlabel("σ (km)")
    ax.set_ylabel("Costo")
    ax.legend(frameon=False)
    ax.set_title("Il costo massimo crolla con σ: 397 a σ = 1,5, zero da σ = 4,0",
                 loc="left", fontweight="bold")
    salva(fig, "3_costo_per_sigma")


# 4) Coppie di farmacie vicine in funzione di delta -----------------------
def g4_coppie():
    delta = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    coppie = [19, 88, 159, 234, 303, 344, 362, 373, 378]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axvspan(2.0, 4.0, color=GRIGIO, alpha=0.25)
    ax.text(2.05, 8, "δ* osservati: 2,0–4,0 km", color="#666666", fontsize=10)
    ax.axhline(378, color="#888888", ls="--", lw=1)
    ax.text(0.5, 384, "378 coppie: tutte (28 × 27 / 2)", color="#666666",
            fontsize=10)
    ax.plot(delta, coppie, "-o", color=BLU, lw=2.5)
    for d, c in zip(delta, coppie):
        ax.annotate(c, (d, c), textcoords="offset points",
                    xytext=(0, 9) if c < 100 else (10, -14), ha="center")
    ax.set_xticks(delta)
    ax.set_xticklabels([it(d, 1) for d in delta])
    ax.set_ylim(0, 410)
    ax.set_xlabel("δ (km)")
    ax.set_ylabel("Coppie a distanza ≤ δ (n_coppie_vicine)")
    ax.set_title("Oltre δ = 4,5 km tutte le 378 coppie di farmacie sono «vicine»",
                 loc="left", fontweight="bold")
    salva(fig, "4_coppie_vicine_delta")


# 5) Costo contro k a delta = 7,5 -----------------------------------------
def g5_costo_k():
    serie = {
        "σ = 2,0": ([15, 30], [118.9, 111.1], GRIGIO),
        "σ = 2,5": ([10, 15, 30], [121.4, 102.6, 94.1], "#8a8678"),
        "σ = 3,0": ([5, 8, 10, 14, 15], [84.6, 47.3, 31.4, 6.3, 0], BLU),
    }
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for nome, (k, c, col) in serie.items():
        ax.plot(k, c, "-o", color=col, lw=2.5, label=nome)
        for kk, cc in zip(k, c):
            ax.annotate(it(cc), (kk, cc), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=9)
        ax.text(k[-1] + 0.5, c[-1], nome, va="center", color=col,
                fontweight="bold")
    ax.set_xlim(0, 34)
    ax.set_ylim(-5, 135)
    ax.set_xlabel("k (turni)")
    ax.set_ylabel("Costo a δ = 7,5")
    ax.set_title("A σ = 3,0 il costo scende molto con k e si annulla da k = 15",
                 loc="left", fontweight="bold")
    fig.text(0.01, 0.005, "σ = 2,5, k = 10: 121,4 nei CSV (l’analisi riporta 121,7)",
             fontsize=8, color="#666666")
    salva(fig, "5_costo_vs_k")


# 6) Test finestra: costo contro s_giorni (sigma = 3, k = 10-15) ----------
def g6_finestra():
    s_giorni = [3, 5, 7, 10, 15]
    pos = range(len(s_giorni))
    d35 = [0, 1.458, 10.728, None, None]
    d30 = [0, 0, 2.524, None, None]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axvspan(2.5, 4.5, color=GRIGIO, alpha=0.25)
    ax.text(3.5, 5.5, "non fattibile con σ = 3", ha="center", color="#666666")
    for dati, nome, col, off in ((d35, "δ = 3,5", BLU, 9), (d30, "δ = 3,0", "#8a8678", -16)):
        p = [i for i, v in zip(pos, dati) if v is not None]
        v = [x for x in dati if x is not None]
        ax.plot(p, v, "-o", color=col, lw=2.5)
        for i, c in zip(p, v):
            ax.annotate(it(c), (i, c), textcoords="offset points",
                        xytext=(0, off), ha="center", fontsize=9)
        ax.text(p[-1] + 0.1, v[-1], nome, color=col, fontweight="bold", va="center")
    ax.set_xticks(list(pos))
    ax.set_xticklabels(s_giorni)
    ax.set_ylim(-1.5, 12)
    ax.set_xlabel("s_giorni (giorni)")
    ax.set_ylabel("Costo")
    ax.set_title("Con σ = 3 il costo sale a 10,7 con s_giorni = 7; oltre non c’è soluzione",
                 loc="left", fontweight="bold", fontsize=12)
    fig.text(0.01, 0.005,
             "k = 10–15 (a s_giorni = 7 e δ = 3,5 solo k = 15). "
             "Fonte: risultati_test_finestra.csv", fontsize=8, color="#666666")
    salva(fig, "6_finestra_costo_vs_s_giorni")


if __name__ == "__main__":
    g1_esiti()
    g2_k_minimo()
    g3_costo_sigma()
    g4_coppie()
    g5_costo_k()
    g6_finestra()
    print("Fatto: grafici in", OUT.resolve())

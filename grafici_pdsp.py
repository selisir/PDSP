"""
Grafici PDSP *senza finestra*: PNG (200 dpi) e PDF con sfondo trasparente.

  1  k minimo per sigma
  2  costo contro delta (sigma = 1,5, k = 30)
  3  mappa della soglia di delta per (sigma, k)
  4  cadenza di apertura delle farmacie
  5  coppie di farmacie vicine contro delta

TUTTI i valori sono calcolati dai file dello zip risultati_senza_finestra
(cartella o .zip):
  - risultati*.csv   costi e n_coppie_vicine (grafici 16 e 19);
  - soluzioni*.txt   esito di ogni combinazione (k, sigma, delta), costo e
                     farmacie aperte giorno per giorno (grafici 15, 17, 18).

Uso:   pip install matplotlib pandas numpy
       python grafici_pdsp.py [percorso_dati]
Output: cartella ./grafici_pdsp
"""
import sys
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd


# ------------------------------------------------------------- file CSV ---
def _normalizza(raw, nome):
    """Porta un CSV (con o senza intestazione) a colonne uniformi."""
    raw = raw[raw[0] != "k_turni"].dropna(how="all")
    if raw.empty:
        return None
    if raw[3].isin(["OTTIMO", "TEMPO_LIMITE"]).all():          # k,sigma,delta,stato,costo,tempo
        d = raw.rename(columns={0: "k", 1: "sigma", 2: "delta",
                                3: "stato", 4: "costo"})
        d["coppie"] = float("nan")
    else:                                                      # k,sigma,delta,costo,coppie,quartieri
        d = raw.rename(columns={0: "k", 1: "sigma", 2: "delta",
                                3: "costo", 4: "coppie"})
        d["stato"] = "OTTIMO"
    d = d[["k", "sigma", "delta", "stato", "costo", "coppie"]].copy()
    for c in ("k", "sigma", "delta", "costo", "coppie"):
        d[c] = pd.to_numeric(d[c])
    d["k"] = d["k"].astype(int)
    d["fonte"] = nome
    return d


def carica(percorso):
    """Legge tutti i risultati*.csv. Per ogni (k, sigma, delta) tiene il costo
    minore. Ritorna (combinazioni, n_coppie_vicine per delta, n. righe)."""
    frames = []
    p = Path(percorso)
    if p.suffix == ".zip":
        with zipfile.ZipFile(p) as z:
            for n in sorted(z.namelist()):
                if n.endswith(".csv") and "finestra" not in Path(n).name:
                    with z.open(n) as f:
                        frames.append(_normalizza(
                            pd.read_csv(f, header=None, dtype=str), Path(n).name))
    else:
        for f in sorted(p.glob("*.csv")):
            if "finestra" in f.name:
                continue
            frames.append(_normalizza(
                pd.read_csv(f, header=None, dtype=str), f.name))
    tutti = pd.concat([f for f in frames if f is not None], ignore_index=True)
    coppie = tutti.dropna(subset=["coppie"]).groupby("delta")["coppie"].max()
    tutti["tl"] = tutti["stato"] == "TEMPO_LIMITE"
    migliori = (tutti.sort_values(["k", "sigma", "delta", "costo", "tl"])
                .drop_duplicates(["k", "sigma", "delta"]))
    return migliori, coppie, len(tutti)


def trova_dati():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    base = Path(__file__).resolve().parent
    for cand in (base / "risultati_senza_finestra",
                 base / "risultati_senza_finestra.zip",
                 Path("risultati_senza_finestra"),
                 Path("risultati_senza_finestra.zip")):
        if cand.exists():
            return cand
    sys.exit("Non trovo la cartella o lo zip 'risultati_senza_finestra'. "
             "Passala come argomento: python grafici_pdsp.py <percorso>")


# --------------------------------------------------- file delle soluzioni ---
import re
from collections import Counter

_HDR = re.compile(r"--- RISULTATI OTTIMIZZAZIONE\s+k_turni = (\d+), "
                  r"sigma = ([\d.]+), delta = ([\d.]+) ---")
_NO = re.compile(r"k_turni = (\d+), sigma = ([\d.]+), delta = ([\d.]+): (.*)")


def _righe_txt(percorso):
    p = Path(percorso)
    if p.suffix == ".zip":
        with zipfile.ZipFile(p) as z:
            for n in sorted(z.namelist()):
                if n.endswith(".txt") and Path(n).name.startswith("soluzioni"):
                    yield from z.read(n).decode("utf-8", "replace").splitlines()
    else:
        for f in sorted(p.glob("soluzioni*.txt")):
            yield from f.read_text(encoding="utf-8", errors="replace").splitlines()


def carica_soluzioni(percorso):
    """Ritorna {(k, sigma, delta): record} con la prima occorrenza di ogni
    combinazione. record: risolto (bool), costo, aperture (Counter)."""
    sol, cur = {}, None
    for riga in _righe_txt(percorso):
        m = _HDR.search(riga)
        if m:
            key = (int(m[1]), float(m[2]), float(m[3]))
            cur = None
            if key not in sol:
                cur = {"risolto": True, "costo": None, "aperture": Counter()}
                sol[key] = cur
            continue
        m = _NO.match(riga)
        if m:                                   # combinazione non risolta
            key = (int(m[1]), float(m[2]), float(m[3]))
            sol.setdefault(key, {"risolto": False, "costo": None,
                                 "aperture": Counter()})
            cur = None
            continue
        if cur is None:
            continue
        if riga.startswith("Costo totale"):
            cur["costo"] = float(riga.split(":")[1])
        elif riga.startswith("Giorno"):
            cur["aperture"].update(riga.split("aperte:")[1].split())
    return sol

OUT = Path("grafici_pdsp")
OUT.mkdir(exist_ok=True)

VERDE, VERDE_CH = "#277a5e", "#a8bab4"
plt.rcParams.update({
    "font.size": 9,
    "axes.edgecolor": "#888888",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 100,
})


def it(v, nd=None):
    s = f"{v:.{nd}f}" if nd is not None else f"{v:g}"
    return s.replace(".", ",")


def salva(fig, nome):
    fig.tight_layout()
    fig.savefig(OUT / f"{nome}.png", dpi=200, transparent=True)
    fig.savefig(OUT / f"{nome}.pdf", transparent=True)
    plt.close(fig)
    print("creato:", nome)


# grafico 1 ----------------------------------------------------------------
def g1_k_minimo(sol):
    sigma = sorted({k[1] for k in sol})
    kmin = {}
    for (k, sg, d), r in sol.items():
        if r["risolto"]:
            kmin[sg] = min(kmin.get(sg, 10**9), k)
    k_floor = min(kmin.values())
    primo_floor = min(s for s, k in kmin.items() if k == k_floor)
    senza = [s for s in sigma if s not in kmin]
    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    for i, s in enumerate(sigma):
        if s in kmin:
            ax.bar(i, kmin[s], width=0.62, color=VERDE if s <= primo_floor else VERDE_CH)
            ax.text(i, kmin[s] + 0.5, kmin[s], ha="center", va="bottom", fontsize=8)
    if senza:
        ax.text(-0.35, max(kmin.values()) * 0.28, f"σ ≤ {it(max(senza))} km:\nnessuna soluzione",
                fontsize=8, va="center", bbox=dict(fc="white", ec="none", pad=1.5))
    ax.set_xticks(range(len(sigma)))
    ax.set_xticklabels([it(s) for s in sigma], fontsize=8)
    ax.set_yticks([])
    ax.set_ylim(0, max(kmin.values()) * 1.13)
    ax.spines["left"].set_visible(False)
    salva(fig, "1_k_minimo_per_sigma")


# grafico 2 ----------------------------------------------------------------
def g2_costo_delta(D, sigma=1.5, k=30):
    d = D[(D.sigma == sigma) & (D.k == k)].sort_values("delta")
    delta, costo = list(d.delta), list(d.costo)
    fig, ax = plt.subplots(figsize=(8, 3.9))
    ax.yaxis.grid(True, color="#dddddd", lw=0.7)
    ax.set_axisbelow(True)
    ax.plot(delta, costo, "-o", color="#1c7a5a", lw=1.6, ms=3,
            label=f"σ = {it(sigma, 1)}")
    ax.text(delta[-1] + 0.12, costo[-1], f"{costo[-1]:.0f}", va="center",
            fontsize=7, color="#555555")
    tick = [x for x in delta if (x * 2) % 2 == 1]
    ax.set_xticks(tick)
    ax.set_xticklabels([it(x, 1) for x in tick], fontsize=7)
    top = int(-(-max(costo) // 50) * 50)
    ax.set_yticks(range(0, top + 1, 50))
    ax.tick_params(axis="y", labelsize=7)
    ax.set_xlim(delta[0] - 0.1, delta[-1] + 0.9)
    ax.set_ylim(0, top + 10)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=7)
    salva(fig, "2_costo_vs_delta")


# grafico 3 ----------------------------------------------------------------
Z = "Z"   # costo nullo per ogni delta
COL_ZERO = "#f0ebe8"


def mappa_soglia(sol, D, sigmi):
    """{sigma: {k: delta* | Z}}: delta* = ultimo delta a costo nullo prima
    del primo costo positivo; Z se il costo e' nullo per ogni delta.
    Le celle non ammissibili non compaiono."""
    costo = {}
    for (k, sg, d), r in sol.items():
        if r["risolto"] and r["costo"] is not None:
            costo[(k, sg, d)] = r["costo"]
    for row in D.itertuples():
        costo[(int(row.k), row.sigma, row.delta)] = min(
            row.costo, costo.get((int(row.k), row.sigma, row.delta), row.costo))
    celle = {}
    for (k, sg, d), c in costo.items():
        if sg in sigmi:
            celle.setdefault((sg, k), {})[d] = c
    mappa = {s: {} for s in sigmi}
    for (sg, k), dd in celle.items():
        pos = [d for d, c in dd.items() if c > 1e-9]
        mappa[sg][k] = Z if not pos else max(d for d in dd if d < min(pos))
    # k non eseguiti (nei dati mancano i k 21-23 per sigma < 3): se i due k
    # vicini hanno la stessa soglia la cella e' completata con quel valore
    for sg, riga in mappa.items():
        ks = sorted(riga)
        for a, b in zip(ks, ks[1:]):
            if b - a > 1 and riga[a] == riga[b]:
                for k in range(a + 1, b):
                    riga[k] = riga[a]
    return mappa


def g3_mappa(sol, D):
    sigmi = [1.5, 2.0, 2.5, 3.0, 3.5]
    mappa = mappa_soglia(sol, D, sigmi)
    ks = sorted({k[0] for k in sol if k[0] >= 2 and k[0] <= 30})
    vals = sorted({v for r in mappa.values() for v in r.values() if v != Z})
    cmap = LinearSegmentedColormap.from_list(
        "d", ["#0b7459", "#3f8a6c", "#6ca488", "#9bbfa9", "#c0d9cb"])
    lo, hi = min(vals), max(vals)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for r, s in enumerate(sigmi):
        for c, k in enumerate(ks):
            v = mappa[s].get(k)
            if v is None:
                continue
            col = COL_ZERO if v == Z else cmap((v - lo) / (hi - lo))
            ax.add_patch(plt.Rectangle((c, r), 0.96, 0.96, color=col, lw=0))
            if v != Z:
                ax.text(c + 0.48, r + 0.48, it(v), ha="center", va="center", fontsize=6)
    ax.set_xlim(-0.05, len(ks))
    ax.set_ylim(len(sigmi), -0.1)
    ax.xaxis.tick_top()
    pari = [(c, k) for c, k in enumerate(ks) if k % 2 == 0]
    ax.set_xticks([c + 0.5 for c, _ in pari])
    ax.set_xticklabels([k for _, k in pari], fontsize=8)
    ax.set_yticks([r + 0.5 for r in range(len(sigmi))])
    ax.set_yticklabels([f"σ = {it(s)}" for s in sigmi], fontsize=8)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.add_patch(plt.Rectangle((len(ks) / 2 - 3.2, len(sigmi) + 0.18), 0.7, 0.3,
                               color=COL_ZERO, lw=0, clip_on=False))
    ax.text(len(ks) / 2 - 2.2, len(sigmi) + 0.33, "costo nullo per ogni δ",
            fontsize=7, va="center", clip_on=False)
    salva(fig, "3_mappa_soglia_delta")


# grafico 4 ----------------------------------------------------------------
def g4_cadenza(sol):
    tot_aperture = Counter()
    for (k, sg, d), r in sol.items():
        if r["risolto"] and r["costo"] and r["costo"] > 0 and k >= 3:
            tot_aperture.update(r["aperture"])
    totale = sum(tot_aperture.values())
    farmacie = sorted(tot_aperture.items(), key=lambda x: (-x[1], x[0]))
    quote = [c / totale * 100 for _, c in farmacie]
    forti = [q >= 10 for q in quote]
    n = len(farmacie)
    nforti = sum(forti)
    xmax = farmacie[0][1]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for i, ((nome, cnt), q) in enumerate(zip(farmacie, quote)):
        ax.barh(i, cnt, height=0.62, color=VERDE if forti[i] else VERDE_CH)
        ax.text(cnt + xmax * 0.012, i, f"{it(q, 1)}% · {cnt}", va="center",
                fontsize=7, color="#555555")
    ax.set_yticks(range(n))
    ax.set_yticklabels([f[0] for f in farmacie], fontsize=7)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_xlim(0, xmax * 1.4)
    for sp in ("bottom", "top", "right"):
        ax.spines[sp].set_visible(False)
    ax.plot([xmax * 1.22] * 2, [-0.35, nforti - 0.65], color="#555555", lw=0.9)
    ax.text(xmax * 1.27, (nforti - 1) / 2, f"{it(sum(q for q, f in zip(quote, forti) if f), 1)}%",
            va="center", fontsize=7, color="#555555")
    salva(fig, "4_cadenza_aperture")


# grafico 5 ----------------------------------------------------------------
def g5_coppie(coppie):
    delta = list(coppie.index)
    val = [int(c) for c in coppie.values]
    top = max(val)
    # fascia evidenziata e barre scure: delta in cui servono ancora nuove coppie
    # (fino all'ultimo delta prima che compaiano tutte le coppie, + 0,5)
    primo_tutte = delta[val.index(top)]
    ultimo_forte = max(d for d in delta if d < primo_tutte)
    inizio_fascia = delta[val.index(min(v for v in val if v >= top / 2))]
    fig, ax = plt.subplots(figsize=(7.5, 3.9))
    i0, i1 = delta.index(inizio_fascia), delta.index(ultimo_forte)
    ax.axvspan(i0 - 0.45, i1 + 0.45, ymax=0.97, color="#e3f2ec", lw=0, zorder=0)
    for i, (d, v) in enumerate(zip(delta, val)):
        forte = d <= ultimo_forte
        ax.bar(i, v, width=0.7, color=VERDE if forte else "#a1c4b5", zorder=2)
        ax.text(i, v + 5, v, ha="center", fontsize=6.5,
                color="#222222" if forte else "#777777")
    ax.set_xticks(range(len(delta)))
    ax.set_xticklabels([it(d, 1) for d in delta], fontsize=6.5, color="#555555")
    ax.set_yticks([0, 100, 200, 300, top])
    ax.tick_params(axis="y", labelsize=6.5, colors="#555555")
    ax.set_ylim(0, top * 1.12)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    salva(fig, "5_coppie_vicine_delta")


if __name__ == "__main__":
    percorso = trova_dati()
    D, coppie, n_righe = carica(percorso)
    sol = carica_soluzioni(percorso)
    g1_k_minimo(sol)
    g2_costo_delta(D)
    g3_mappa(sol, D)
    g4_cadenza(sol)
    g5_coppie(coppie)
    print("Fatto: grafici in", OUT.resolve())

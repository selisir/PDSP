"""
Integra il CSV dei risultati con il log delle soluzioni (.txt) di Xpress-Mosel.

- Il CSV contiene SOLO le combinazioni risolte (ottime o in timeout).
- Il TXT contiene tutte le combinazioni, comprese quelle infeasible.
- Il programma .mos è stato lanciato più volte: gli stessi parametri compaiono
  più volte nel TXT (a volte con esiti diversi). Per ogni combinazione si tiene
  SEMPRE l'ultima occorrenza (quella più in basso nel file = run più recente).

Output: una riga per ogni combinazione di parametri (CSV + infeasible),
con le colonne 'status', 'costo_totale' e 'costo' (alias di costo_ottimo,
letto da grafici.py).
"""
import re
import sys
import pandas as pd

csv_file = "risultati_test_finestra.csv"
txt_file = "soluzioni_test_finestra.txt"
output_file = "risultati_test_finestra_2_integrati.csv"

CHIAVE = ['k_turni', 's_giorni', 's_turni', 'sigma', 'delta']
STATUS = {'2': 'Ottimo (2)', '4': 'Timeout (4)'}

PATTERN = re.compile(
    r'k_turni=(\d+)\s+s_giorni=(\d+)\s+s_turni=(\d+)\s+sigma=([\d.]+)\s+delta=([\d.]+)'
)


def parametri(m):
    return {
        'k_turni': int(m.group(1)),
        's_giorni': int(m.group(2)),
        's_turni': int(m.group(3)),
        'sigma': float(m.group(4)),
        'delta': float(m.group(5)),
    }


def parse_txt(path):
    """Restituisce un DataFrame con un evento per ogni esito trovato nel log,
    nell'ordine in cui compare (l'ordine serve per tenere l'ultimo)."""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            righe = f.read().splitlines()
    except FileNotFoundError:
        sys.exit(f"Errore: file '{path}' non trovato.")

    eventi = []
    corrente = None   # parametri del blocco "RISULTATI OTTIMIZZAZIONE" aperto
    status = None

    for riga in righe:
        riga = riga.strip()
        if not riga:
            continue

        # Combinazione infeasible (per copertura mancante o dal solutore)
        if "Infeasible" in riga:
            m = PATTERN.search(riga)
            if m:
                eventi.append({**parametri(m), 'status': 'Infeasible', 'costo_totale': None})
            corrente, status = None, None
            continue

        # Inizio blocco risultati
        if "--- RISULTATI OTTIMIZZAZIONE" in riga:
            m = PATTERN.search(riga)
            corrente = parametri(m) if m else None
            status = None
            continue

        if corrente is None:
            continue

        if riga.startswith("Status soluzione:"):
            codice = riga.split(":", 1)[1].strip()
            status = STATUS.get(codice, codice)
        elif riga.startswith("Costo totale:"):
            try:
                costo = float(riga.split(":", 1)[1].strip())
            except ValueError:
                costo = None
            eventi.append({**corrente, 'status': status, 'costo_totale': costo})
            corrente, status = None, None

    df = pd.DataFrame(eventi, columns=CHIAVE + ['status', 'costo_totale'])
    n = len(df)
    df = df.drop_duplicates(subset=CHIAVE, keep='last').reset_index(drop=True)
    print(f"TXT: {n} esiti trovati, {len(df)} combinazioni uniche "
          f"({n - len(df)} duplicati scartati, tenuto l'ultimo).")
    return df


def main():
    print(f"Leggo {txt_file}...")
    df_txt = parse_txt(txt_file)

    print(f"Leggo {csv_file}...")
    try:
        df_csv = pd.read_csv(csv_file)
    except FileNotFoundError:
        sys.exit(f"Errore: file '{csv_file}' non trovato.")
    df_csv.columns = [c.strip() for c in df_csv.columns]

    n = len(df_csv)
    df_csv = df_csv.drop_duplicates(subset=CHIAVE, keep='last').reset_index(drop=True)
    print(f"CSV: {n} righe, {len(df_csv)} combinazioni uniche "
          f"({n - len(df_csv)} duplicati scartati, tenuta l'ultima).")

    # Stessi tipi sulle colonne chiave, altrimenti il merge non aggancia.
    for col in ['k_turni', 's_giorni', 's_turni']:
        df_csv[col] = df_csv[col].astype(int)
        df_txt[col] = df_txt[col].astype(int)
    for col in ['sigma', 'delta']:
        df_csv[col] = df_csv[col].astype(float)
        df_txt[col] = df_txt[col].astype(float)

    # OUTER merge: le combinazioni infeasible esistono solo nel TXT e con un
    # left merge sul CSV andrebbero perse (e grafici.py non le conterebbe).
    df = pd.merge(df_csv, df_txt, on=CHIAVE, how='outer', indicator=True)

    solo_csv = (df['_merge'] == 'left_only').sum()
    if solo_csv:
        print(f"Attenzione: {solo_csv} righe del CSV non hanno corrispondenza nel TXT "
              f"(status e costo_totale resteranno vuoti).")
    df = df.drop(columns='_merge')

    # Le combinazioni solo-TXT sono infeasible: il costo non esiste (NaN)
    # Alias letto da grafici.py
    df['costo'] = df['costo_ottimo']

    df = df.sort_values(CHIAVE).reset_index(drop=True)

    # Controllo: chiave unica
    assert not df.duplicated(subset=CHIAVE).any(), "Chiavi duplicate nell'output"

    df.to_csv(output_file, index=False)
    print(f"\nSalvato {output_file}: {len(df)} righe.")
    print(df['status'].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()

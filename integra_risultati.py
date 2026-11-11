import pandas as pd
import re
import sys

# Configurazione nomi file
csv_file = "risultati_test_finestra.csv"
txt_file = "soluzioni_test_finestra.txt"
output_file = "risultati_test_finestra_2_integrati.csv"

def parse_txt_to_df(txt_path):
    estratti = []
    # Espressione regolare per estrarre i parametri esatti dalla riga
    pattern_parametri = re.compile(r'k_turni=(\d+)\s+s_giorni=(\d+)\s+s_turni=(\d+)\s+sigma=([\d.]+)\s+delta=([\d.]+)')
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Errore: Il file {txt_path} non è stato trovato.")
        sys.exit(1)
        
    current_dict = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Cattura configurazioni Infeasible
        if "Infeasible" in line:
            m = pattern_parametri.search(line)
            if m:
                estratti.append({
                    'k_turni': int(m.group(1)),
                    's_giorni': int(m.group(2)),
                    's_turni': int(m.group(3)),
                    'sigma': float(m.group(4)),
                    'delta': float(m.group(5)),
                    'Status_soluzione': 'Infeasible',
                    'Costo_totale': None
                })
            continue
            
        # Cattura configurazioni che hanno prodotto un risultato di ottimizzazione
        if "--- RISULTATI OTTIMIZZAZIONE" in line:
            m = pattern_parametri.search(line)
            if m:
                current_dict = {
                    'k_turni': int(m.group(1)),
                    's_giorni': int(m.group(2)),
                    's_turni': int(m.group(3)),
                    'sigma': float(m.group(4)),
                    'delta': float(m.group(5))
                }
            continue
            
        # Estrai status e costo
        if current_dict and line.startswith("Status soluzione:"):
            current_dict['Status_soluzione'] = line.split(":")[1].strip()
            
        if current_dict and line.startswith("Costo totale:"):
            current_dict['Costo_totale'] = float(line.split(":")[1].strip())
            # Aggiunge alla lista e resetta per il prossimo blocco
            estratti.append(current_dict.copy())
            current_dict = {}
            
    return pd.DataFrame(estratti)

def main():
    print(f"Leggo i dati da {txt_file}...")
    df_soluzioni = parse_txt_to_df(txt_file)
    
    print(f"Leggo il CSV {csv_file}...")
    try:
        df_csv = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Errore: Il file {csv_file} non è stato trovato nella directory corrente.")
        return

    # Normalizzazione delle colonne chiave per il merge
    colonne_chiave = ['k_turni', 's_giorni', 's_turni', 'sigma', 'delta']
    for col in colonne_chiave:
        if col in df_csv.columns:
            # Converte i tipi per evitare errori di mismatch (es: int vs float)
            df_csv[col] = df_csv[col].astype(df_soluzioni[col].dtype)
            
    print("Eseguo l'incrocio (merge) dei dati...")
    # Left join dal CSV per mantenere tutte le righe originali, aggiungendo le due nuove colonne
    df_integrato = pd.merge(df_csv, df_soluzioni, on=colonne_chiave, how='left')
    
    print(f"Salvo il risultato in {output_file}...")
    df_integrato.to_csv(output_file, index=False)
    print("Integrazione completata con successo! Nuove colonne: 'Status_soluzione' e 'Costo_totale'.")

if __name__ == "__main__":
    main()

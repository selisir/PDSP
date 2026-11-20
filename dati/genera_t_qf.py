import pandas as pd
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def genera_t_dist(file_farmacie, file_centroidi, file_output):
    # Carica i due dataset
    df_farm = pd.read_csv(file_farmacie)
    df_quartieri = pd.read_csv(file_centroidi)

    # Escludiamo Q3 (Mizzana) per allinearci a n_quartieri=8 del tuo file Mosel.
    # Assumiamo che i quartieri siano in ordine Q1...Q9. Eliminiamo l'indice 2 (la terza riga).
    if len(df_quartieri) > 8:
        df_quartieri = df_quartieri.drop(index=2).reset_index(drop=True)

    # Scrittura del file in formato Mosel
    with open(file_output, 'w') as f:
        f.write("t_dist: [\n")
        
        # Calcola la distanza tra ogni farmacia e ogni quartiere
        for i in range(len(df_farm)):
            riga_distanze = []
            for j in range(len(df_quartieri)):
                dist = haversine(
                    df_farm.loc[i, "lat"], df_farm.loc[i, "lon"],
                    df_quartieri.loc[j, "Latitudine"], df_quartieri.loc[j, "Longitudine"]
                )
                riga_distanze.append(f"{dist:.4f}")
            
            # Scrive la riga della matrice
            f.write("    " + " ".join(riga_distanze) + "\n")
            
        f.write("]\n")

if __name__ == "__main__":
    genera_t_dist("farmacie.csv", "centroidi_quartieri_ferrara.csv", "t_dist.dat")
    print("File t_dist.dat generato calcolando le distanze esatte con formula di Haversine.")

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

df = pd.read_csv("farmacie.csv")  # colonne: id, nome, lat, lon
n = len(df)
ids = df["id"].tolist()

# Matrice triangolare superiore: valori solo per i < j, resto a 0
matrice = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i < j:
            matrice[i, j] = haversine(
                df.loc[i, "lat"], df.loc[i, "lon"],
                df.loc[j, "lat"], df.loc[j, "lon"]
            )
        # i == j -> resta 0 (diagonale)
        # i > j  -> resta 0 (parte inferiore)

# --- Export .dat in formato matrice (righe/colonne) per Mosel ---
with open("farmacie_triangolare.dat", "w") as f:
    f.write("PHARMACIES: [" + ", ".join(str(i) for i in ids) + "]\n\n")
    f.write("DIST: [\n")
    for i in range(n):
        riga = " ".join(f"{matrice[i, j]:.3f}" for j in range(n))
        f.write(f"\t{riga}\n")
    f.write("]\n")

print("File farmacie_triangolare.dat generato (matrice triangolare superiore, zeri altrove).")
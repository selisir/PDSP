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

# Matrice distanze
matrice = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i != j:
            matrice[i, j] = haversine(
                df.loc[i, "lat"], df.loc[i, "lon"],
                df.loc[j, "lat"], df.loc[j, "lon"]
            )

# Costruzione DataFrame con layout: id, nome, dist1, dist2, ...
colonne_dist = [f"dist{i+1}" for i in range(n)]
df_out = pd.DataFrame(matrice, columns=colonne_dist)
df_out.insert(0, "id", df["id"].values)
df_out.insert(1, "nome", df["nome"].values)

df_out.to_csv("matrice_distanze_farmacie.csv", index=False)
print(df_out.head())
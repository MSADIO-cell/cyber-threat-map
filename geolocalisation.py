import requests
import pandas as pd
import time

df = pd.read_csv("ips.csv")
liste_ips = df["ip"].tolist()

URL = "http://ip-api.com/batch?fields=status,country,countryCode,city,lat,lon,query"

resultats = []

# On envoie les IP par paquets de 100
for i in range(0, len(liste_ips), 100):
    paquet = liste_ips[i:i + 100]
    reponse = requests.post(URL, json=paquet, timeout=30)
    resultats.extend(reponse.json())
    print(f"Paquet {i // 100 + 1} traité")
    time.sleep(5)  # pause pour respecter la limite du service

geo = pd.DataFrame(resultats)

# On garde seulement les adresses localisées avec succès
geo = pd.DataFrame(resultats)
geo = geo[geo["status"] == "success"]
geo = geo.rename(columns={"query": "ip"})
geo = geo.drop(columns=["status"])

geo = geo.merge(df[["ip", "type"]], on="ip")
geo.to_csv("ips_geo.csv", index=False)
print(geo["type"].value_counts())

print(f"{len(geo)} IP géolocalisées")
print(geo.head())
print()
print("Top 5 des pays :")
print(geo["country"].value_counts().head(5))
from urllib.request import urlopen
import csv

BASE = "https://lists.blocklist.de/lists/"
TYPES = {
    "ssh": "Attaque SSH",
    "mail": "Attaque mail",
    "apache": "Attaque site web",
    "ftp": "Attaque FTP",
    "bots": "Bots",
}

lignes = []
for fichier, nom in TYPES.items():
    with urlopen(f"{BASE}{fichier}.txt", timeout=30) as r:
        texte = r.read().decode("utf-8")
    ips = [ip for ip in texte.strip().split("\n") if ":" not in ip][:100]
    for ip in ips:
        lignes.append({"ip": ip, "type": nom})
    print(f"{nom} : {len(ips)} IP")

uniques = []
ips_vues = set()
for ligne in lignes:
    if ligne["ip"] not in ips_vues:
        uniques.append(ligne)
        ips_vues.add(ligne["ip"])

with open("ips.csv", "w", newline="", encoding="utf-8") as fichier_csv:
    writer = csv.DictWriter(fichier_csv, fieldnames=["ip", "type"])
    writer.writeheader()
    writer.writerows(uniques)

print(f"Total : {len(uniques)} IP")

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

BASE_URL = "https://onepiece.fandom.com"
START_URL = "https://onepiece.fandom.com/fr/wiki/Liste_des_Personnages_Canon"

# Créer le dossier pour les images
os.makedirs("images", exist_ok=True)

# 1. Récupérer tous les liens depuis les tableaux
response = requests.get(START_URL)
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.select("table.wikitable")
links = []

# Liste des mots à exclure
exclude_keywords = ["Catégorie", "Liste", "One_Piece", "#", "Special", "chapitre", "episode"]

for table in tables:
    for a_tag in table.select("a[href^='/fr/wiki/']"):
        href = a_tag.get("href")
        full_url = BASE_URL + href
        # Filtrer les liens contenant les mots interdits
        if not any(word.lower() in href.lower() for word in exclude_keywords):
            links.append(full_url)

links = list(set(links))  # Suppression doublons
print(f"Nombre de personnages trouvés : {len(links)}")

# 2. Scraper la page personnage
def scrape_character(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        infobox = soup.select_one("aside.portable-infobox")
        if not infobox:
            return None

        # Nom du personnage
        name_tag = infobox.select_one("h2.pi-title")
        name = name_tag.get_text(strip=True) if name_tag else "Inconnu"

        # Image
        img_tag = infobox.select_one("img")
        image_url = img_tag["src"] if img_tag else None

        # Télécharger l'image
        image_path = None
        if image_url:
            try:
                img_data = requests.get(image_url).content
                img_name = os.path.basename(urlparse(image_url).path)
                image_path = os.path.join("images", img_name)
                with open(image_path, "wb") as f:
                    f.write(img_data)
            except:
                image_path = None

        # Fonction utilitaire pour récupérer une info
        def get_info(source):
            tag = infobox.select_one(f"div[data-source='{source}'] div.pi-data-value")
            return tag.get_text(strip=True) if tag else "Inconnu"

        # Récupération des infos
        affiliation = get_info("affiliation")
        prime = get_info("prime")
        fruit = get_info("fruit")
        genre = get_info("gender")
        taille = get_info("taille")
        origine = get_info("origine")
        chapitre = get_info("apparition")

        return {
            "Nom": name,
            "Image": image_path if image_path else "Inconnu",
            "Affiliation": affiliation,
            "Prime": prime,
            "Fruit": fruit,
            "Genre": genre,
            "Taille": taille,
            "Origine": origine,
            "Chapitre": chapitre,
            "Lien": url
        }
    except Exception as e:
        print(f"Erreur pour {url}: {e}")
        return None

# 3. Multi-thread scraping pour accélérer
characters = []
with ThreadPoolExecutor(max_workers=10) as executor:
    for i, data in enumerate(executor.map(scrape_character, links)):
        if data:
            characters.append(data)
        print(f"[{i+1}/{len(links)}] OK")

# 4. Sauvegarde JSON
with open("personnages_onepiece.json", "w", encoding="utf-8") as f:
    json.dump(characters, f, ensure_ascii=False, indent=4)

# 5. Sauvegarde CSV
df = pd.DataFrame(characters)
df.to_csv("personnages_onepiece.csv", index=False, encoding="utf-8")

print(f"Scraping terminé ! {len(characters)} personnages extraits.")

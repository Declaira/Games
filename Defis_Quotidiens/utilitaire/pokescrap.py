import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_french_url(english_name):
    """Retourne l'URL de la page Bulbapedia en français pour un Pokémon anglais"""
    url = f"https://bulbapedia.bulbagarden.net/wiki/{english_name}_(Pokémon)"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur pour {english_name} : {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    fr_link = soup.find("a", {"lang": "fr"})
    if fr_link and "href" in fr_link.attrs:
        return fr_link["href"]
    
    return None


def process_csv(input_csv, output_csv):
    # Charger le CSV
    df = pd.read_csv(input_csv)
    
    # On suppose que la première colonne contient le nom anglais
    english_names = df.iloc[:, 1].tolist()
    
    urls = []
    for name in english_names:
        print(f"Traitement de {name}...")
        url = get_french_url(name)
        urls.append(url)
        #time.sleep(0.05)  # petite pause pour éviter de surcharger le site
    
    # Ajouter la nouvelle colonne
    df["French_URL"] = urls
    
    # Sauvegarder dans un nouveau CSV
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Fichier sauvegardé : {output_csv}")


# Exemple d'utilisation
process_csv(r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemon.csv", r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons_with_french_urls.csv")


#%%

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper Poképedia (page Pokémon individuelle)
Extrait : nom, type1, type2, couleur, évolution, génération, taille (m), poids (kg)
Télécharge l'image principale dans ./imagepokemon/<nom>.png et met le chemin dans le CSV.

Usage:
  - Modifie la liste URLS ci-dessous (ou fournis un fichier avec une URL par ligne)
  - Lance: python scrape_pokepedia_pokemon.py
"""

import os
import re
import time
import csv
import requests
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokéScraper/1.0)"}
BASE = "https://www.pokepedia.fr/"
# Charger le CSV avec les URLs
df = pd.read_csv(r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons_with_french_urls.csv")

# On suppose que la 5ème colonne contient les URLs (index 4 car Python commence à 0)
urls = df.iloc[:, 4].dropna().tolist()

# Modifier ici les URLs que tu veux scraper ou utilise la variable urls ci-dessous.
URLS = urls #[urls[i][34:] for i in range(len(urls))]
#print(urls)
# Si tu préfères lire depuis un fichier texte (1 URL par ligne), laisse ça sur None
urls_from_file = None  

OUT_CSV = r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons.csv"
IMG_DIR = r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\imagepokemon"

os.makedirs(IMG_DIR, exist_ok=True)


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def get_soup(url: str, max_retries=3, timeout=15) -> Optional[BeautifulSoup]:
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"[get_soup] Erreur requête {url} (tentative {attempt+1}/{max_retries}): {e}")
            time.sleep(1 + attempt)
    return None


def sanitize_filename(name: str) -> str:
    # enlève caractères non-fichiers et remplace espaces par underscore
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if c.isalnum() or c in " _-")
    name = name.strip().replace(" ", "_")
    return name or "pokemon"


def find_infobox(soup: BeautifulSoup):
    # Cherche des tables connues (roundy, infobox, floatright) ou une table contenant une image
    selectors = [
        "table.roundy",
        "table.infobox",
        "table.floatright",
        "table.wikitable",  # fallback
        "div.infobulle",    # improbable mais on essaie
    ]
    for sel in selectors:
        box = soup.select_one(sel)
        if box:
            return box

    # fallback: première table contenant une image et plusieurs lignes
    for table in soup.find_all("table"):
        if table.find("img") and len(table.find_all("tr")) >= 2:
            return table

    # fallback autre: section contenant "infobox" en class
    box = soup.find(lambda tag: tag.name in ("div", "table") and tag.get("class") and any("info" in c.lower() or "box" in c.lower() for c in tag.get("class")))
    return box


def extract_number_from_text(txt: str, unit: str) -> Optional[float]:
    if not txt:
        return None
    txt = txt.replace("\u00A0", " ")
    # cherche x.yy m ou x,y m ou cm
    m = re.search(r"([\d\.,]+)\s*m", txt)
    if m:
        val = m.group(1).replace(",", ".")
        try:
            return float(val)
        except:
            return None
    # si kg
    m = re.search(r"([\d\.,]+)\s*kg", txt)
    if m:
        val = m.group(1).replace(",", ".")
        try:
            return float(val)
        except:
            return None
    # si just a number
    m = re.search(r"([\d\.,]+)", txt)
    if m:
        val = m.group(1).replace(",", ".")
        try:
            return float(val)
        except:
            return None
    return None


def download_image(img_url: str, dest_path: str) -> bool:
    try:
        r = requests.get(img_url, headers=HEADERS, stream=True, timeout=20)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[download_image] Erreur téléchargement {img_url}: {e}")
        return False


def parse_infobox_fields(infobox) -> dict:
    # Initialise valeurs vides
    data = {
        "type1": "",
        "type2": "",
        "couleur": "",
        "evolution": "",
        "generation": "",
        "taille": None,
        "poids": None,
        "image_url": "",
    }

    if infobox is None:
        return data

    # 1) extraire l'image principale (si possible)
    # Cherche <a class="image"> <img ...>
    img_tag = infobox.find("a", class_="image")
    if img_tag and img_tag.find("img"):
        src = img_tag.find("img").get("src") or ""
        data["image_url"] = src
    else:
        # fallback: première image dans l'infobox
        img = infobox.find("img")
        if img:
            data["image_url"] = img.get("src") or ""

    # 2) parcourir les lignes tr pour extraire clés/valeurs
    for tr in infobox.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not td:
            continue
        key = th.get_text(" ", strip=True) if th else ""
        key_norm = normalize_text(key)

        val_text = td.get_text(" ", strip=True)
        # si on a des images dans td (souvent pour types), récupérer alt
        imgs_alt = [img.get("alt", "").strip() for img in td.find_all("img") if img.get("alt")]
        # Nettoyage
        val_text_clean = val_text.strip()

        # détection des champs par mots-clé (francais)
        if "type" in key_norm:
            # types / imgs_alt
            if imgs_alt:
                data["type1"] = imgs_alt[0]
                if len(imgs_alt) > 1:
                    data["type2"] = imgs_alt[1]
            else:
                # parfois texte "Plante / Poison"
                parts = re.split(r"[\/,;]+", val_text_clean)
                if len(parts) >= 1:
                    data["type1"] = parts[0].strip()
                if len(parts) >= 2:
                    data["type2"] = parts[1].strip()
        elif "couleur" in key_norm:
            data["couleur"] = val_text_clean
        elif "évolution" in key_norm or "evolution" in key_norm:
            data["evolution"] = val_text_clean
        elif "génération" in key_norm or "generation" in key_norm:
            data["generation"] = val_text_clean
        elif "taille" in key_norm:
            n = extract_number_from_text(val_text_clean, "m")
            data["taille"] = n
        elif "poids" in key_norm or "masse" in key_norm:
            n = extract_number_from_text(val_text_clean, "kg")
            data["poids"] = n
        elif "habitat" in key_norm:
            # habitat parfois listé sous forme de liens
            data["habitat"] = val_text_clean

    # 3) si type non trouvé via lignes, tente récupérer premier/second images alt plausibles
    if not data["type1"]:
        imgs_alt_all = [img.get("alt", "").strip() for img in infobox.find_all("img") if img.get("alt")]
        # essayer de prendre les deux premiers textes courts
        candidates = [x for x in imgs_alt_all if x and len(x) <= 20]
        if candidates:
            data["type1"] = candidates[0]
            if len(candidates) > 1:
                data["type2"] = candidates[1]

    # normaliser image_url en url absolue si nécessaire sera fait plus bas
    return data


def scrape_pokemon_page(url: str) -> dict:
    soup = get_soup(url)
    if not soup:
        raise RuntimeError(f"Impossible d'ouvrir {url}")

    # nom de la page (titre)
    nom_tag = soup.find(id="firstHeading")
    nom = nom_tag.get_text(strip=True) if nom_tag else soup.title.get_text(strip=True)

    infobox = find_infobox(soup)
    fields = parse_infobox_fields(infobox)

    # si image_url relative, rendre absolue
    img_url = fields.get("image_url") or ""
    if img_url and img_url.startswith("//"):
        img_url = "https:" + img_url
    elif img_url and img_url.startswith("/"):
        img_url = urljoin(BASE, img_url)
    fields["image_url"] = img_url

    # tenter récupération détaillée d'autres infos si encore manquantes :
    # parfois génération/taille/poids sont dans des listes <li> de l'infobox
    # on fait un scan plus large pour trouver "Taille" "Poids" si non trouvés
    if (fields.get("taille") is None) or (fields.get("poids") is None) or (not fields.get("generation")):
        # cherche occurrences partout dans la page
        text = soup.get_text(" ", strip=True)
        # chercher taille 'x.x m'
        if fields.get("taille") is None:
            m = re.search(r"taille[:\s]*([\d\.,]+)\s*m", text, flags=re.IGNORECASE)
            if m:
                try:
                    fields["taille"] = float(m.group(1).replace(",", "."))
                except:
                    pass
        if fields.get("poids") is None:
            m = re.search(r"poids[:\s]*([\d\.,]+)\s*kg", text, flags=re.IGNORECASE)
            if m:
                try:
                    fields["poids"] = float(m.group(1).replace(",", "."))
                except:
                    pass
        if not fields.get("generation"):
            m = re.search(r"génération[:\s]*([0-9]+)", text, flags=re.IGNORECASE)
            if m:
                fields["generation"] = m.group(1)

    # compose résultat
    result = {
        "nom": nom,
        "type1": fields.get("type1", ""),
        "type2": fields.get("type2", ""),
        "couleur": fields.get("couleur", ""),
        "evolution": fields.get("evolution", ""),
        "generation": fields.get("generation", ""),
        "taille": fields.get("taille"),
        "poids": fields.get("poids"),
        "image_url": fields.get("image_url"),
    }
    return result


def main(url_list):
    results = []
    for idx, url in enumerate(url_list, start=0):  # start=1 → 1er Pokémon = #1
        print(f"\n--- Scraping {url}")
        idx = idx +1
        try:
            data = scrape_pokemon_page(url)
        except Exception as e:
            print(f"[ERREUR] impossible de scraper {url}: {e}")
            continue

        # download image if present
        img_path = ""
        if data.get("image_url"):
            # Nom du fichier = numéro de Pokédex avec extension correcte
            ext = os.path.splitext(data["image_url"].split("?")[0])[-1]
            if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                ext = ".png"
            filename = f"{idx}{ext}"
            
            dest = os.path.join(IMG_DIR, filename)
            ok = download_image(data["image_url"], dest)
            if ok:
                img_path = dest
            else:
                img_path = ""
        else:
            print(f"  (aucune image détectée pour {data['nom']})")

        # ajout du numéro de pokedex
        data["numero"] = idx
        data["image_path"] = img_path

        # enlever l'url de l'image du dict pour éviter doublons
        data.pop("image_url", None)
        results.append(data)

        # pause légère
        time.sleep(0.01)

    # Réorganiser les colonnes (numero en premier)
    df = pd.DataFrame(results, columns=["numero", "nom", "type1", "type2", "couleur", 
                                        "evolution", "generation", "taille", "poids", "image_path"])
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nTerminé. {len(results)} Pokémon écrits dans {OUT_CSV}. Images dans {IMG_DIR}/")



if __name__ == "__main__":
    # construire la liste finale d'URLs
    url_list = []
    if urls_from_file and os.path.exists(urls_from_file):
        with open(urls_from_file, "r", encoding="utf-8") as f:
            url_list = [line.strip() for line in f if line.strip()]
    else:
        url_list = URLS[:]

    if not url_list:
        print("Aucune URL fournie. Modifie la variable URLS ou fournis un fichier.")
    else:
        main(url_list)
#%%
# Dossier contenant tes images
IMG_DIR = r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\imagepokemon"

# Décalage (par exemple -1 pour descendre chaque numéro d'une place)
OFFSET = -1  

# Extensions autorisées
valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")

files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(valid_exts)]

# Trier par numéro (en supposant que les fichiers sont nommés "X.png" avec X un entier)
files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

for fname in files:
    num, ext = os.path.splitext(fname)
    try:
        new_num = int(num) + OFFSET
        if new_num <= 0:
            print(f"⚠️ Ignoré : {fname} (résultat {new_num})")
            continue
        new_name = f"{new_num}{ext}"
        old_path = os.path.join(IMG_DIR, fname)
        new_path = os.path.join(IMG_DIR, new_name)
        print(f"Renomme {fname} -> {new_name}")
        os.rename(old_path, new_path)
    except ValueError:
        print(f"⚠️ Ignoré (nom non numérique) : {fname}")


#%%

import re
import os
import requests
import pandas as pd
from urllib.parse import urlparse
import time

API_URL = "https://www.pokepedia.fr/api.php"
IMG_DIR = r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\imagepokemon"
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {"User-Agent": "PokepediaScraper/1.0"}

def get_wikitext(pokemon_name):
    params = {
        "action": "parse",
        "page": pokemon_name,
        "prop": "wikitext",
        "format": "json"
    }
    r = requests.get(API_URL, params=params, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    return data["parse"]["wikitext"]["*"]

def parse_pokemon_template(wikitext):
    """
    Extrait les infos du modèle {{Pokémon|...}}
    """
    infos = {}
    for line in wikitext.splitlines():
        m = re.match(r"\|\s*(\w+)\s*=\s*(.*)", line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            infos[key] = val
    return infos

def get_image_url(filename):
    """
    Récupère l'URL complète d'une image à partir de son nom de fichier (ex: 'Fichier:Bulbizarre-RFVF.png')
    """
    params = {
        "action": "query",
        "titles": filename,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    r = requests.get(API_URL, params=params, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    pages = data["query"]["pages"]
    for p in pages.values():
        if "imageinfo" in p:
            return p["imageinfo"][0]["url"]
    return None

def download_image(url, name):
    if not url:
        return ""
    ext = os.path.splitext(url)[1]
    if not ext:
        ext = ".png"
    safe_name = re.sub(r"[^\w\-_.]", "_", name) + ext
    path = os.path.join(IMG_DIR, safe_name)
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    return path

def scrape_pokemon(name):
    print(f"Scraping {name}...")
    wikitext = get_wikitext(name)
    infos = parse_pokemon_template(wikitext)

    # nom
    nom = name

    # types
    type1 = infos.get("type1", "")
    type2 = infos.get("type2", "")

    # couleur, taille, poids
    couleur = infos.get("couleur", "")
    taille = infos.get("taille", "")
    poids = infos.get("poids", "")

    # génération
    generation = infos.get("génération", infos.get("generation", ""))

    # niveau d’évolution
    evo_stage = infos.get("stade", infos.get("stade évolution", ""))

    # image (souvent "image" ou "sprite" dans le modèle)
    image_field = infos.get("image", "") or infos.get("sprite", "")
    img_url = None
    img_path = ""
    if image_field:
        if not image_field.startswith("Fichier:"):
            image_field = "Fichier:" + image_field
        img_url = get_image_url(image_field)
        img_path = download_image(img_url, nom)

    return {
        "nom": nom,
        "type1": type1,
        "type2": type2,
        "couleur": couleur,
        "taille": taille,
        "poids": poids,
        "generation": generation,
        "evolution_stage": evo_stage,
        "image_path": img_path
    }

if __name__ == "__main__":
    # Charger les URLs depuis la 5e colonne du CSV
    df = pd.read_csv(r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons_with_french_urls.csv")
    urls = df.iloc[:, 4].dropna().tolist()

    # Extraire uniquement le nom de la page (ex: "Bulbizarre" depuis "https://www.pokepedia.fr/Bulbizarre")
    pokemon_list = [urlparse(u).path.split("/")[-1] for u in urls]

    results = []
    for p in pokemon_list:
        try:
            data = scrape_pokemon(p)
            results.append(data)
        except Exception as e:
            print(f"Erreur pour {p} : {e}")
        #time.sleep(0.05)  # éviter de surcharger Poképédia

    df_out = pd.DataFrame(results)
    df_out.to_csv(r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons.csv", index=False, encoding="utf-8-sig")
    print("CSV généré : pokemons.csv")

#%%
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import os

# === CONFIG ===
CSV_PATH = r"C:\Users\ADRIEN\Documents\Scripts\Site\OPdle\pokemons.csv"

# Charger le CSV
df = pd.read_csv(CSV_PATH)

# Vérifier qu'il existe une colonne 'evolution'
if "evolution" not in df.columns:
    df["evolution"] = ""


index = 0  # Pokémon courant

# === Fonctions ===
def show_pokemon():
    global img_label, index, img_tk

    row = df.iloc[index]
    nom_label.config(text=f"{row['nom']} (#{index+1})")

    # Charger l'image
    img_path = str(row["image_path"])
    if os.path.exists(img_path):
        img = Image.open(img_path).resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.config(text="")  # enlever texte si image dispo
    else:
        img_label.config(image="", text="(Pas d'image)")

    # Charger valeur existante si déjà remplie
    evo_var.set(str(row["evolution"]) if pd.notna(row["evolution"]) else "")

    # Donner le focus au champ et sélectionner son contenu
    evo_entry.focus_set()
    evo_entry.selection_range(0, tk.END)

def save_and_next(event=None):  # event=None pour accepter l'appel depuis Entrée
    global index

    # Sauver valeur saisie
    df.at[index, "evolution"] = evo_var.get()

    # Passer au suivant
    if index < len(df) - 1:
        index += 1
        show_pokemon()
    else:
        df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        status_label.config(text="✅ Tout est terminé, CSV sauvegardé !")
        next_btn.config(state="disabled")
        evo_entry.config(state="disabled")

# === Interface ===
root = tk.Tk()
root.title("Annotateur de Pokémon - Evolution")

nom_label = tk.Label(root, font=("Arial", 16))
nom_label.pack(pady=10)

img_label = tk.Label(root)
img_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Stade d’évolution :").grid(row=0, column=0, padx=5)
evo_var = tk.StringVar()
evo_entry = ttk.Entry(frame, textvariable=evo_var, width=20)
evo_entry.grid(row=0, column=1, padx=5)

next_btn = ttk.Button(root, text="Valider et suivant", command=save_and_next)
next_btn.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

# Associer la touche Entrée à la validation
root.bind("<Return>", save_and_next)

# Lancer avec le premier Pokémon
show_pokemon()

root.mainloop()

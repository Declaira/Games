import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# === Mémoire pour stocker les corrections ===
corrections = {}

# === Fonctions ===
def load_csv():
    filepath = filedialog.askopenfilename(title="Choisir un fichier CSV", filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    file_path_var.set(filepath)

def start_process():
    filepath = file_path_var.get()
    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV valide.")
        return
    
    target_col = column_var.get().strip()
    if not target_col:
        messagebox.showerror("Erreur", "Veuillez entrer le nom de la colonne à modifier.")
        return
    
    # Lire le CSV
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        if target_col not in reader[0]:
            messagebox.showerror("Erreur", f"La colonne '{target_col}' n'existe pas.")
            return
        
        process_lines(reader, target_col, filepath)

def process_lines(data, column, filepath):
    current_index = 0
    def show_next():
        nonlocal current_index
        while current_index < len(data):
            current_value = data[current_index][column].strip()
            
            # === Ignore les cases vides ===
            if current_value == "":
                current_index += 1
                continue

            # Si correction déjà connue → appliquer directement
            if current_value in corrections:
                data[current_index][column] = corrections[current_value]
                current_index += 1
                continue

            # Affiche la valeur pour correction
            value_label.config(text=f"Valeur actuelle : {current_value}")
            entry.delete(0, tk.END)
            root.update_idletasks()
            return

    def apply_correction():
        nonlocal current_index
        new_value = entry.get().strip()
        if new_value:
            old_value = data[current_index][column]
            corrections[old_value] = new_value
            data[current_index][column] = new_value
        current_index += 1
        show_next()

    btn_apply.config(command=apply_correction)
    show_next()

def save_csv(data, original_path):
    output_path = original_path.replace(".csv", "_updated.csv")
    with open(output_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    messagebox.showinfo("Terminé", f"Fichier modifié enregistré sous : {output_path}")

# === Interface ===
root = tk.Tk()
root.title("Correction des Affiliations CSV")

file_path_var = tk.StringVar()
column_var = tk.StringVar()

tk.Label(root, text="Fichier CSV :").pack(pady=5)
tk.Entry(root, textvariable=file_path_var, width=50).pack()
tk.Button(root, text="Parcourir", command=load_csv).pack(pady=5)

tk.Label(root, text="Nom de la colonne à modifier :").pack(pady=5)
tk.Entry(root, textvariable=column_var, width=30).pack(pady=5)

tk.Button(root, text="Démarrer", command=start_process).pack(pady=10)

value_label = tk.Label(root, text="", font=("Arial", 14))
value_label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=5)

btn_apply = tk.Button(root, text="Appliquer", bg="green", fg="white")
btn_apply.pack(pady=10)

root.mainloop()

#%%

import csv
import json
from tkinter import filedialog, messagebox
import tkinter as tk
import os

def select_csv():
    filepath = filedialog.askopenfilename(title="Choisir un fichier CSV", filetypes=[("CSV files", "*.csv")])
    if filepath:
        csv_path.set(filepath)

def convert_to_json():
    csv_file = csv_path.get()
    if not csv_file or not os.path.exists(csv_file):
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV valide.")
        return
    
    json_file = csv_file.replace(".csv", ".json")

    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        # Conversion en JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Succès", f"Conversion terminée !\nFichier JSON créé : {json_file}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

# === Interface graphique ===
root = tk.Tk()
root.title("Convertisseur CSV → JSON")

csv_path = tk.StringVar()

tk.Label(root, text="Sélectionnez un fichier CSV :").pack(pady=5)
tk.Entry(root, textvariable=csv_path, width=50).pack(pady=5)
tk.Button(root, text="Parcourir", command=select_csv).pack(pady=5)

tk.Button(root, text="Convertir en JSON", command=convert_to_json, bg="green", fg="white").pack(pady=15)

root.mainloop()

#%%
import csv
import os
import requests
from bs4 import BeautifulSoup
import time

# === CORRECTION : chemins absolus ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "chars_modifie.csv")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "characters_updated.csv")
IMAGES_FOLDER = os.path.join(SCRIPT_DIR, "images")

os.makedirs(IMAGES_FOLDER, exist_ok=True)

BASE_URL = "https://onepiece.fandom.com/fr/wiki/"

# Crée le dossier images s'il n'existe pas
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# === LIRE LE CSV ===
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

# Vérifie si la colonne 'image' existe, sinon l'ajoute
if 'image' not in reader.fieldnames:
    fieldnames = reader.fieldnames + ['image']
else:
    fieldnames = reader.fieldnames

# === SCRAPING & TÉLÉCHARGEMENT ===
for row in rows:
    name = row['name'].strip()
    wiki_name = name.replace(" ", "_")  # Format URL
    url = BASE_URL + wiki_name

    try:
        print(f"🔍 Recherche image pour : {name} -> {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Trouver l'image principale
        image_tag = soup.select_one("figure.pi-item img")
        if image_tag and 'src' in image_tag.attrs:
            image_url = image_tag['src']
            # Certaines images sont en format webp -> on force .png
            image_name = name.replace(" ", "_") + ".png"
            image_path = os.path.join(IMAGES_FOLDER, image_name)

            # Télécharger l'image
            img_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(img_data)

            print(f"✅ Image téléchargée : {image_path}")

            # Ajoute le chemin au CSV
            row['image'] = image_path
        else:
            print(f"❌ Image non trouvée pour {name}")
            row['image'] = ""
    except Exception as e:
        print(f"⚠️ Erreur pour {name} : {e}")
        row['image'] = ""

    # Pause pour éviter le bannissement (politesse)
    time.sleep(1)

# === SAUVEGARDE DU NOUVEAU CSV ===
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Fichier mis à jour : {OUTPUT_CSV}")

#%%
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def choisir_fichier():
    filepath = filedialog.askopenfilename(
        title="Choisir un fichier CSV",
        filetypes=[("Fichiers CSV", "*.csv")]
    )
    if filepath:
        file_path_var.set(filepath)

def remplacer_cases_vides():
    fichier_csv = file_path_var.get()
    colonne_cible = column_var.get().strip()

    if not fichier_csv or not os.path.exists(fichier_csv):
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV valide.")
        return

    if not colonne_cible:
        messagebox.showerror("Erreur", "Veuillez entrer le nom de la colonne à modifier.")
        return

    try:
        # Lecture du CSV
        with open(fichier_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        # Vérifier si la colonne existe
        if colonne_cible not in data[0]:
            messagebox.showerror("Erreur", f"La colonne '{colonne_cible}' n'existe pas dans le fichier.")
            return

        # Remplacer les cases vides par "Inconnue"
        for row in data:
            if row[colonne_cible].strip() == "":
                row[colonne_cible] = "Inconnue"

        # Sauvegarde du fichier mis à jour
        output_path = fichier_csv
        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        messagebox.showinfo("Succès", f"Les cases vides ont été remplacées.\nFichier enregistré :\n{output_path}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

# === Interface Tkinter ===
root = tk.Tk()
root.title("Remplacer les cases vides dans un CSV")

file_path_var = tk.StringVar()
column_var = tk.StringVar()

tk.Label(root, text="Fichier CSV :").pack(pady=5)
tk.Entry(root, textvariable=file_path_var, width=50).pack()
tk.Button(root, text="Parcourir", command=choisir_fichier).pack(pady=5)

tk.Label(root, text="Nom de la colonne à modifier :").pack(pady=5)
tk.Entry(root, textvariable=column_var, width=30).pack(pady=5)

tk.Button(root, text="Remplacer les cases vides", command=remplacer_cases_vides, bg="green", fg="white").pack(pady=10)

root.mainloop()




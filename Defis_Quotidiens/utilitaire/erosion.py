import cv2
import numpy as np
from PIL import Image

# Paramètres
image_path = "mon_image.png"   # <-- Mets ton image ici
output_path = "dessin_style_bd.png"
epaisseur_liseret = 15  # épaisseur du contour noir (extérieur)

# Charger en niveaux de gris pour créer un masque
img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Charger en couleur (et corriger BGR → RGB)
img_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# --- Étape 1 : Masque du dessin ---
# Seuil automatique Otsu
_, masque = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Nettoyage (fermeture pour combler les petits trous)
kernel3 = np.ones((3, 3), np.uint8)
masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, kernel3, iterations=2)

# --- Étape 2 : Créer le contour externe avec un disque ---
kernel_disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*epaisseur_liseret+1, 2*epaisseur_liseret+1))
dilate = cv2.dilate(masque, kernel_disk, iterations=1)

# Le liseré = dilatation - masque original
liseret = cv2.subtract(dilate, masque)

# --- Étape 3 : Construire l’image finale ---
h, w = img_rgb.shape[:2]
img_rgba = np.zeros((h, w, 4), dtype=np.uint8)

# Dessin original avec transparence
img_rgba[:, :, :3] = img_rgb
img_rgba[:, :, 3] = masque  # alpha = dessin

# Ajouter le liseré noir externe (contour façon BD)
img_rgba[liseret > 0] = [0, 0, 0, 255]

# Sauvegarde
Image.fromarray(img_rgba).save(output_path)

print(f"✅ Image sauvegardée sous {output_path}")

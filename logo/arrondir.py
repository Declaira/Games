from PIL import Image, ImageDraw



def rond(image_path,output_path="image_arrondie.png"):
    # Charger l'image carrée (ex: 500x500)
    img = Image.open(image_path).convert("RGBA")
    size = img.size[0]  # suppose que l'image est carrée
    
    # Créer un masque circulaire
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Appliquer le masque à l'image pour ne garder que le cercle
    circular_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # fond transparent
    circular_img.paste(img, (0, 0), mask=mask)
    
    # Sauvegarder
    circular_img.save(output_path)
    
def arrondir_bords(image_path, rayon, output_path="image_arrondie.png"):
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    # Masque avec coins arrondis
    masque = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(masque)
    draw.rounded_rectangle((0, 0, w, h), radius=rayon, fill=255)

    # Image de sortie avec transparence
    img_arrondie = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img_arrondie.paste(img, (0, 0), mask=masque)

    img_arrondie.save(output_path)

# Exemple d’utilisation
arrondir_bords("logo_carre.png", rayon=150, output_path="logo4.png")


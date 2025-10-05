from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Config
text = "éclaira"
font_size = 128  # Les polices pixel n’aiment pas les trop grosses tailles
width, height = 400, 200
colors = ["#ffe5b4", "#ffd1d1"]
font_path = "pixel_font.ttf"  # Mets ici le nom exact de ta police pixel
#FFF6E5
# Dégradé horizontal
def create_gradient(width, height, colors):
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    steps = len(colors) - 1
    for i in range(width):
        ratio = i / (width - 1)
        idx = min(int(ratio * steps), steps - 1)
        c1 = tuple(int(colors[idx].lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
        c2 = tuple(int(colors[idx+1].lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
        local_ratio = (ratio * steps) - idx
        r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)
        arr[:, i] = (r, g, b)
    return Image.fromarray(arr, mode='RGB')

# Image et masque texte
img = Image.new("RGB", (width, height), "white")
font = ImageFont.truetype(font_path, font_size)
text_img = Image.new("L", (width, height))
draw = ImageDraw.Draw(text_img)
w, h = draw.textsize(text, font=font)
draw.text(((width - w) / 2, (height - h) / 2), text, font=font, fill=255)

# Appliquer le dégradé au texte
gradient = create_gradient(width, height, colors)
img.paste(gradient, (0, 0), text_img)

# Sauvegarde
img.save("eclair_pixel_gradient.png")

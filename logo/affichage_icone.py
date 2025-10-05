import os
import ctypes
import win32gui
import win32api
import win32con
import tkinter as tk
from PIL import Image, ImageTk

# Structure BITMAP pour ctypes
class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType", ctypes.c_long),
        ("bmWidth", ctypes.c_long),
        ("bmHeight", ctypes.c_long),
        ("bmWidthBytes", ctypes.c_long),
        ("bmPlanes", ctypes.c_uint16),
        ("bmBitsPixel", ctypes.c_uint16),
        ("bmBits", ctypes.c_void_p),
    ]

def extract_icons(dll_path, max_icons=400):
    """Extrait les handles d’icônes d’une DLL Windows"""
    icons = []
    for i in range(max_icons):
        try:
            hicon_large, _ = win32gui.ExtractIconEx(dll_path, i, 1)
            if hicon_large:
                icons.append((i, hicon_large[0]))
        except Exception:
            break
    return icons

def hicon_to_image(hicon):
    """Convertit un handle d’icône Windows en image PIL (essaie plusieurs tailles)"""
    if not hicon or hicon == 0:
        raise ValueError("Handle d’icône invalide")

    for size in (16, 32, 48):  # on teste plusieurs tailles standards
        ico_x, ico_y = size, size
        hdc = win32gui.GetDC(0)
        hdc_mem = win32gui.CreateCompatibleDC(hdc)
        hbm = win32gui.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        old_obj = win32gui.SelectObject(hdc_mem, hbm)

        try:
            success = win32gui.DrawIconEx(hdc_mem, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
            if not success:
                continue  # essaie une autre taille

            bmp = BITMAP()
            ctypes.windll.gdi32.GetObjectW(hbm, ctypes.sizeof(BITMAP), ctypes.byref(bmp))
            total_bytes = bmp.bmWidth * bmp.bmHeight * 4
            buffer = ctypes.create_string_buffer(total_bytes)
            ctypes.windll.gdi32.GetBitmapBits(hbm, total_bytes, buffer)

            img = Image.frombuffer(
                "RGBA",
                (bmp.bmWidth, bmp.bmHeight),
                buffer, "raw", "BGRA", 0, 1
            )
            return img
        finally:
            win32gui.SelectObject(hdc_mem, old_obj)
            win32gui.DeleteObject(hbm)
            win32gui.DeleteDC(hdc_mem)
            win32gui.ReleaseDC(0, hdc)
            win32gui.DestroyIcon(hicon)

    raise ValueError("Impossible de dessiner l’icône (toutes tailles échouées)")

def show_icons(dll_path, max_icons=400):
    """Affiche uniquement les icônes valides d’un fichier DLL"""
    root = tk.Tk()
    root.title(f"Icônes valides de {os.path.basename(dll_path)}")

    canvas = tk.Canvas(root, width=800, height=600, scrollregion=(0,0,2000,2000))
    vbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    canvas.config(yscrollcommand=vbar.set)

    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    frame = tk.Frame(canvas)
    canvas.create_window((0,0), window=frame, anchor="nw")

    icons = extract_icons(dll_path, max_icons)
    valid_count = 0

    for idx, hicon in icons:
        try:
            img = hicon_to_image(hicon)
            img = img.resize((32, 32), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            item_frame = tk.Frame(frame, padx=5, pady=2)
            item_frame.pack(side=tk.TOP, anchor="w")

            label_icon = tk.Label(item_frame, image=photo)
            label_icon.image = photo
            label_icon.pack(side=tk.LEFT)

            label_text = tk.Label(item_frame, text=f"Index : {idx}")
            label_text.pack(side=tk.LEFT)

            valid_count += 1
        except Exception:
            continue  # ignore les icônes invalides

    info = tk.Label(frame, text=f"\nTotal d’icônes valides : {valid_count}", font=("Arial", 12, "bold"))
    info.pack(anchor="w", pady=10)

    root.mainloop()

if __name__ == "__main__":
    system32 = os.path.join(os.environ["SystemRoot"], "System32")
    dll_path = os.path.join(system32, "shell32.dll")

    show_icons(dll_path, max_icons=400)

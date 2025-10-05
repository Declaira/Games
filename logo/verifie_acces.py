import socket
import subprocess

PORT = 8000

# Obtenir l'adresse IP locale
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Envoie fictif vers une IP externe pour récupérer l'IP locale utilisée
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# Vérifie si un port est ouvert sur cette machine
def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(("127.0.0.1", port))
        return result == 0

# Ouvre le navigateur sur le serveur local si disponible
def open_browser(url):
    try:
        subprocess.run(["start", url], shell=True)
    except Exception as e:
        print(f"Impossible d'ouvrir le navigateur : {e}")

# --- Exécution ---
ip = get_local_ip()
local_url = f"http://localhost:{PORT}"
network_url = f"http://{ip}:{PORT}"

print("🔍 Vérification de l'accès local au serveur Python...")
if is_port_open(PORT):
    print(f"✅ Le port {PORT} est OUVERT.")
    print(f"📍 Accès depuis ce PC : {local_url}")
    print(f"📱 Accès depuis le téléphone (même Wi-Fi) : {network_url}")
    print("🌐 Ouverture du navigateur...")
    open_browser(f"{local_url}/index.html")
else:
    print(f"❌ Le port {PORT} semble FERMÉ.")
    print("💡 Vérifie que ton serveur est bien lancé avec : python serveur_local.py")

import http.server
import socketserver
import socket

PORT = 8000

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"✅ Serveur local lancé !")
print(f"📍 Sur ce PC        : http://localhost:{PORT}")
print(f"📱 Depuis réseau Wi-Fi : http://{local_ip}:{PORT}")
print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()

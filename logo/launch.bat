@echo off
title Serveur Local Déclaira

REM Lancer le serveur Python
start python serveur_local.py

REM Attendre que le serveur soit bien lancé
timeout /t 3 /nobreak

REM Obtenir l'adresse IP locale de l'ordinateur
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do set IP_LOCAL=%%i

REM Enlever les espaces inutiles
set IP_LOCAL=%IP_LOCAL: =%

REM Vérifier si le port 8000 est ouvert (avec telnet)
echo Test de l'ouverture du port 8000...
telnet %IP_LOCAL% 8000 >nul 2>&1

REM Si le port est ouvert, ouvrir le navigateur et afficher l'URL
if %errorlevel% equ 0 (
    echo ✅ Le port 8000 est OUVERT.
    echo 📍 Accédez à l'URL suivante : http://%IP_LOCAL%:8000
    start http://%IP_LOCAL%:8000/accueil.html
) else (
    echo ❌ Le port 8000 est FERMÉ. Vérifiez que le serveur est bien lancé.
)

pause

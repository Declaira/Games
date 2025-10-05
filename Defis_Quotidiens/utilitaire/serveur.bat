@echo off
echo Démarrage du serveur local sur le port 8000...

REM Ouvre le navigateur sur index.html
start "" "http://localhost:8000/index.html"

REM Lancer un mini serveur local avec PowerShell
powershell -NoExit -Command ^
"$listener = [System.Net.HttpListener]::new(); ^
$listener.Prefixes.Add('http://localhost:8000/'); ^
$listener.Start(); ^
Write-Host 'Serveur lancé sur http://localhost:8000'; ^
while ($true) { ^
    $ctx = $listener.GetContext(); ^
    $path = $ctx.Request.Url.AbsolutePath.TrimStart('/'); ^
    if ($path -eq '') { $path = 'index.html' }; ^
    $file = Join-Path (Get-Location) $path; ^
    if (Test-Path $file) { ^
        $bytes = [System.IO.File]::ReadAllBytes($file); ^
        $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length) ^
    }; ^
    $ctx.Response.Close() ^
}"
pause

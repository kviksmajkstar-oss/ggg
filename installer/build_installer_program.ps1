Param(
  [string]$Version = "1.0.2"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$installerDir = Join-Path $root "installer"
$payload = Join-Path $installerDir "payload"
$output = Join-Path $root "dist\installer-program"

if (Test-Path $payload) { Remove-Item $payload -Recurse -Force }
if (Test-Path $output) { Remove-Item $output -Recurse -Force }
New-Item -Type Directory -Path $payload | Out-Null
New-Item -Type Directory -Path $output | Out-Null

Write-Host "[1/5] Build frontend"
Push-Location (Join-Path $root "frontend")
npm install
npm run build
Pop-Location

Write-Host "[2/5] Prepare backend venv"
Push-Location (Join-Path $root "backend")
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
Pop-Location

Write-Host "[3/5] Build payload"
Copy-Item (Join-Path $root "backend") (Join-Path $payload "backend") -Recurse
Copy-Item (Join-Path $root "frontend\dist") (Join-Path $payload "frontend-dist") -Recurse
Copy-Item (Join-Path $root "README.md") (Join-Path $payload "README.md")

Write-Host "[4/5] Build installer program exe"
python -m pip install pyinstaller
Push-Location $installerDir
pyinstaller --noconfirm --onefile --windowed --name OneMusicInstaller --add-data "payload;payload" installer_app.py
Pop-Location

Write-Host "[5/5] Copy outputs"
Copy-Item (Join-Path $installerDir "dist\OneMusicInstaller.exe") (Join-Path $output ("OneMusicInstaller-" + $Version + ".exe"))

Write-Host "Done: dist\installer-program\OneMusicInstaller-$Version.exe"

Param(
  [string]$AppVersion = "1.0.1"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist"
$bundle = Join-Path $dist "OneMusicAI"

if (Test-Path $bundle) {
  Remove-Item $bundle -Recurse -Force
}
New-Item -ItemType Directory -Path $bundle | Out-Null

Write-Host "[1/4] Building frontend..."
Push-Location (Join-Path $root "frontend")
npm install
npm run build
Pop-Location

Write-Host "[2/4] Preparing backend virtual env..."
Push-Location (Join-Path $root "backend")
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
Pop-Location

Write-Host "[3/4] Assembling bundle..."
Copy-Item (Join-Path $root "README.md") $bundle
Copy-Item (Join-Path $root "backend") (Join-Path $bundle "backend") -Recurse
Copy-Item (Join-Path $root "frontend\dist") (Join-Path $bundle "frontend-dist") -Recurse
Copy-Item (Join-Path $root "scripts\run_onemusic.bat") (Join-Path $bundle "run_onemusic.bat")

Write-Host "[4/4] Building setup.exe with Inno Setup..."
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
  throw "ISCC.exe not found. Install Inno Setup 6 first: https://jrsoftware.org/isdl.php"
}

& $iscc "/DAppVersion=$AppVersion" (Join-Path $root "installer\OneMusicAI.iss")

Write-Host "Done. setup.exe is in dist\\installer\\OneMusicAI-Setup-$AppVersion.exe"

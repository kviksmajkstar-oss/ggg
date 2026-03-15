Param(
  [string]$AppVersion = "1.0.2",
  [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist"
$bundle = Join-Path $dist "OneMusicAI"
$frontendDist = Join-Path $root "frontend\dist"

function Resolve-CommandPath([string]$Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -ne $cmd) { return $cmd.Source }
  return $null
}

function Get-NpmCommand {
  $npmCmd = Resolve-CommandPath "npm.cmd"
  if ($npmCmd) { return $npmCmd }

  $npm = Resolve-CommandPath "npm"
  if ($npm) { return $npm }

  return $null
}

function Ensure-NodeTooling {
  $node = Resolve-CommandPath "node"
  $npm = Get-NpmCommand

  if (-not $node -or -not $npm) {
    throw @"
Node.js/npm not found in PATH.
Install Node.js LTS and reopen PowerShell, then retry.
Quick install examples:
  winget install OpenJS.NodeJS.LTS
  choco install nodejs-lts
If frontend/dist already exists, run with -SkipFrontendBuild.
"@
  }

  return $npm
}

if (Test-Path $bundle) {
  Remove-Item $bundle -Recurse -Force
}
New-Item -ItemType Directory -Path $bundle | Out-Null

if (-not $SkipFrontendBuild) {
  Write-Host "[1/4] Building frontend..."
  $npmCmd = Ensure-NodeTooling
  Push-Location (Join-Path $root "frontend")
  & $npmCmd install
  & $npmCmd run build
  Pop-Location
} else {
  Write-Host "[1/4] Skip frontend build (requested)"
  if (-not (Test-Path $frontendDist)) {
    throw "frontend/dist not found. Remove -SkipFrontendBuild or build frontend first."
  }
}

Write-Host "[2/4] Preparing backend virtual env..."
Push-Location (Join-Path $root "backend")
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
Pop-Location

Write-Host "[3/4] Assembling bundle..."
Copy-Item (Join-Path $root "README.md") $bundle
Copy-Item (Join-Path $root "backend") (Join-Path $bundle "backend") -Recurse
Copy-Item $frontendDist (Join-Path $bundle "frontend-dist") -Recurse
Copy-Item (Join-Path $root "scripts\run_onemusic.bat") (Join-Path $bundle "run_onemusic.bat")

Write-Host "[4/4] Building setup.exe with Inno Setup..."
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
  throw "ISCC.exe not found. Install Inno Setup 6 first: https://jrsoftware.org/isdl.php"
}

& $iscc "/DAppVersion=$AppVersion" (Join-Path $root "installer\OneMusicAI.iss")

Write-Host "Done. setup.exe is in dist\\installer\\OneMusicAI-Setup-$AppVersion.exe"

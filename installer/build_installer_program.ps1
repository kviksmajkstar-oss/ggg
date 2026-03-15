Param(
  [string]$Version = "1.0.4",
  [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$installerDir = Join-Path $root "installer"
$payload = Join-Path $installerDir "payload"
$output = Join-Path $root "dist\installer-program"
$frontendDist = Join-Path $root "frontend\dist"

function Resolve-CommandPath([string]$Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -ne $cmd) { return $cmd.Source }
  return $null
}

function Get-PythonInvoker {
  $python = Resolve-CommandPath "python"
  if ($python) {
    return @{ Command = $python; PrefixArgs = @() }
  }

  $py = Resolve-CommandPath "py"
  if ($py) {
    return @{ Command = $py; PrefixArgs = @("-3") }
  }

  throw @"
Python not found in PATH.
Install Python 3.10+ and reopen PowerShell.
Quick install examples:
  winget install Python.Python.3.12
  choco install python
"@
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
If you already built frontend earlier, run with -SkipFrontendBuild.
"@
  }

  return $npm
}

function Ensure-VenvPython([string]$BackendDir, $PythonInvoker) {
  & $PythonInvoker.Command @($PythonInvoker.PrefixArgs + @("-m", "venv", ".venv"))
  $venvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
  if (-not (Test-Path $venvPython)) {
    throw "Virtual env python not found at $venvPython. Venv creation failed."
  }
  return $venvPython
}

if (Test-Path $payload) { Remove-Item $payload -Recurse -Force }
if (Test-Path $output) { Remove-Item $output -Recurse -Force }
New-Item -Type Directory -Path $payload | Out-Null
New-Item -Type Directory -Path $output | Out-Null

if (-not $SkipFrontendBuild) {
  Write-Host "[1/5] Build frontend"
  $npmCmd = Ensure-NodeTooling
  Push-Location (Join-Path $root "frontend")
  & $npmCmd install
  & $npmCmd run build
  Pop-Location
} else {
  Write-Host "[1/5] Skip frontend build (requested)"
  if (-not (Test-Path $frontendDist)) {
    throw "frontend/dist not found. Remove -SkipFrontendBuild or build frontend first."
  }
}

Write-Host "[2/5] Prepare backend venv"
$backendDir = Join-Path $root "backend"
$pythonInvoker = Get-PythonInvoker
Push-Location $backendDir
$venvPython = Ensure-VenvPython -BackendDir $backendDir -PythonInvoker $pythonInvoker
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
Pop-Location

Write-Host "[3/5] Build payload"
Copy-Item (Join-Path $root "backend") (Join-Path $payload "backend") -Recurse
Copy-Item $frontendDist (Join-Path $payload "frontend-dist") -Recurse
Copy-Item (Join-Path $root "README.md") (Join-Path $payload "README.md")

Write-Host "[4/5] Build installer program exe"
& $pythonInvoker.Command @($pythonInvoker.PrefixArgs + @("-m", "pip", "install", "pyinstaller"))
Push-Location $installerDir
pyinstaller --noconfirm --onefile --windowed --name OneMusicInstaller --add-data "payload;payload" installer_app.py
Pop-Location

Write-Host "[5/5] Copy outputs"
Copy-Item (Join-Path $installerDir "dist\OneMusicInstaller.exe") (Join-Path $output ("OneMusicInstaller-" + $Version + ".exe"))

Write-Host "Done: dist\installer-program\OneMusicInstaller-$Version.exe"

@echo off
setlocal
cd /d %~dp0\..
if "%~1"=="" (
  python installer\pyinstaller_builder.py --from-scratch --mode onefile --version 1.1.1
) else (
  python installer\pyinstaller_builder.py %*
)

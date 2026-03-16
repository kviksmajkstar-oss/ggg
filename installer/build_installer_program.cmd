@echo off
setlocal

cd /d %~dp0\..
if "%~1"=="" (
  python installer\build_installer_program.py --version 1.0.9
) else (
  python installer\build_installer_program.py %*
)

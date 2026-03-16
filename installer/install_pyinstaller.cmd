@echo off
setlocal
cd /d %~dp0\..
python installer\install_pyinstaller.py

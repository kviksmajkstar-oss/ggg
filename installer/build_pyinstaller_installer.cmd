@echo off
setlocal
cd /d %~dp0\..
python installer\pyinstaller_builder.py %*

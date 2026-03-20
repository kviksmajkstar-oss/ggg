@echo off
setlocal

cd /d "%~dp0"
title NOMERCY local launcher

if "%PORT%"=="" set "PORT=8000"
set "NOMERCY_URL=http://127.0.0.1:%PORT%"

echo ==========================================
echo              NOMERCY launcher
echo ==========================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js not found.
  echo.
  echo Install Node.js from https://nodejs.org/
  echo Then reopen this file: start-nomercy.bat
  echo.
  pause
  exit /b 1
)

if not exist "server.js" (
  echo [ERROR] server.js not found in:
  echo %cd%
  echo.
  pause
  exit /b 1
)

call :ensure_firewall_rule

echo Starting server from:
echo %cd%
echo.
echo Local URL:
echo %NOMERCY_URL%
echo.
echo If you want to open the site from another device in the same network,
echo use this computer's local IP and the same port:
echo http://YOUR-LOCAL-IP:%PORT%
echo.

where powershell >nul 2>nul
if not errorlevel 1 (
  start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2; Start-Process '%NOMERCY_URL%'"
) else (
  start "" "%NOMERCY_URL%"
)

echo Server logs will appear below.
echo To stop NOMERCY, press Ctrl+C in this window.
echo.

node server.js
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if not "%EXIT_CODE%"=="0" (
  echo [ERROR] NOMERCY stopped with code %EXIT_CODE%.
  echo Check the messages above.
) else (
  echo NOMERCY server stopped.
)
echo.
pause
exit /b

:ensure_firewall_rule
set "NOMERCY_FIREWALL_RULE=NOMERCY %PORT%"

net session >nul 2>nul
if errorlevel 1 (
  echo [WARNING] This window is not running as Administrator.
  echo If the site opens on this PC but not on your phone, rerun start-nomercy.bat as Administrator once
  echo so Windows Firewall can allow incoming TCP connections on port %PORT%.
  echo.
  goto :eof
)

netsh advfirewall firewall show rule name="%NOMERCY_FIREWALL_RULE%" >nul 2>nul
if errorlevel 1 (
  echo Adding Windows Firewall rule for TCP port %PORT%...
  netsh advfirewall firewall add rule name="%NOMERCY_FIREWALL_RULE%" dir=in action=allow protocol=TCP localport=%PORT% >nul
  if errorlevel 1 (
    echo [WARNING] Failed to add the firewall rule automatically.
  ) else (
    echo [OK] Windows Firewall now allows TCP port %PORT%.
  )
  echo.
  goto :eof
)

echo [OK] Windows Firewall already allows TCP port %PORT%.
echo.
goto :eof

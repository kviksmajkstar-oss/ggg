# Installer program (`OneMusicInstaller.exe`)

Этот вариант делает **инсталлер как отдельную программу** (GUI), а не только setup-скрипт.

## Что делает программа

- показывает окно установки
- копирует payload (backend + frontend build + README) в выбранную папку
- создаёт launcher (`run_onemusic.bat` / `run_onemusic.sh`)
- на Windows умеет создать ярлыки на Desktop и в Start Menu

## Сборка EXE (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\build_installer_program.ps1 -Version 1.0.2
```

Выходной файл:

- `dist\installer-program\OneMusicInstaller-1.0.2.exe`

## Важно

В Linux-контейнере нельзя собрать нативный Windows `.exe` без Windows runtime/tooling,
поэтому репозиторий содержит готовый сборочный pipeline для Windows.

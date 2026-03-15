# Installer program (`OneMusicInstaller.exe`)

Этот вариант делает **инсталлер как отдельную программу** (GUI), а не только setup-скрипт.

## Что делает программа

- показывает окно установки
- копирует payload (backend + frontend build + README) в выбранную папку
- создаёт launcher (`run_onemusic.bat` / `run_onemusic.sh`)
- на Windows умеет создать ярлыки на Desktop и в Start Menu

## Сборка EXE (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\build_installer_program.ps1 -Version 1.0.5
```

Выходной файл:

- `dist\installer-program\OneMusicInstaller-1.0.5.exe`

## Важно

В Linux-контейнере нельзя собрать нативный Windows `.exe` без Windows runtime/tooling,
поэтому репозиторий содержит готовый сборочный pipeline для Windows.


Если Node.js/npm не установлен, скрипт теперь завершится с понятной подсказкой (winget/choco).
Если `frontend/dist` уже собран, можно использовать `-SkipFrontendBuild`.


Если ошибка связана с `.venv\Scripts\python`, в новых скриптах добавлена проверка создания venv и fallback через `py -3`.


Если создание venv прошло нестандартно, скрипт проверяет пути: `Scripts/python.exe`, `Scripts/python`, `bin/python`, `bin/python3`.

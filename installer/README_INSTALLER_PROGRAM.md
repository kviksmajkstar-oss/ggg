# Installer program (`OneMusicInstaller.exe`)

Этот вариант делает **инсталлер как отдельную программу** (GUI), а не только setup-скрипт.

## Что делает программа

- показывает окно установки
- копирует payload (backend + frontend build + README) в выбранную папку
- создаёт launcher (`run_onemusic.bat` / `run_onemusic.sh`)
- на Windows умеет создать ярлыки на Desktop и в Start Menu

## Сборка EXE (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\build_installer_program.ps1 -Version 1.0.7
```

Выходной файл:

- `dist\installer-program\OneMusicInstaller-1.0.7.exe`

## Важно

В Linux-контейнере нельзя собрать нативный Windows `.exe` без Windows runtime/tooling,
поэтому репозиторий содержит готовый сборочный pipeline для Windows.


Если Node.js/npm не установлен, скрипт теперь завершится с понятной подсказкой (winget/choco).
Если `frontend/dist` уже собран, можно использовать `-SkipFrontendBuild`.


Если ошибка связана с `.venv\Scripts\python`, в новых скриптах добавлена проверка создания venv и fallback через `py -3`.


Если создание venv прошло нестандартно, скрипт проверяет пути: `Scripts/python.exe`, `Scripts/python`, `bin/python`, `bin/python3`.


Если видите `Python exited with code 9009`, это обычно сломанный python launcher/alias.
Отключите App Execution Alias для `python.exe`/`python3.exe` или установите Python 3.10+ из официального дистрибутива.


Скрипт запускает сборку через `python -m PyInstaller`, поэтому не требуется отдельная команда `pyinstaller` в PATH.


Если PyInstaller завершился без файла на ожидаемом пути, скрипт теперь проверяет несколько путей (`installer/dist` и `dist`) и выводит список проверенных путей в ошибке.


Если `--onefile` режим PyInstaller падает, скрипт автоматически делает retry с `--onedir` и забирает exe оттуда.
Также payload очищается от тяжёлых директорий (`.venv`, `__pycache__`, `.pytest_cache`) перед упаковкой.


## Python-скрипт сборки (рекомендуется)

Вместо PowerShell можно использовать прямой билд на Python + PyInstaller:

```bash
python installer/build_installer_program.py --version 1.0.9
```

Если frontend уже собран:

```bash
python installer/build_installer_program.py --version 1.0.9 --skip-frontend-build
```


Сборка идет через spec-файл `installer/OneMusicInstaller.spec` (стабильнее для PyInstaller).
Для удобства на Windows есть ярлык-команда: `installer\build_installer_program.cmd`.


## Чистая сборка инсталлера только через PyInstaller

Если payload уже подготовлен, можно собрать только сам exe-инсталлер:

```bash
python installer/pyinstaller_builder.py --version 1.1.1 --mode auto
```

Windows shortcut:

```bat
installer\build_pyinstaller_installer.cmd --version 1.1.1
```


## Сборка с нуля в один файл (.exe)

Рекомендуемая команда:

```bash
python installer/pyinstaller_builder.py --from-scratch --mode onefile --version 1.1.1
```

Что делает команда:
- собирает frontend
- готовит payload
- запускает PyInstaller в onefile режиме
- сохраняет лог в `installer/pyinstaller-build.log`

Если нужно пропустить пересборку frontend:

```bash
python installer/pyinstaller_builder.py --from-scratch --skip-frontend-build --mode onefile --version 1.1.1
```

Windows one-click:

```bat
installer\build_pyinstaller_installer.cmd
```

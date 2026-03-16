# setup.exe build

В этом репозитории добавлен пайплайн для сборки `setup.exe` на Windows.

## Что нужно на Windows

- Node.js 20+
- Python 3.10+
- Inno Setup 6

## Команда

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows_setup.ps1 -AppVersion 1.0.1
```

После успешной сборки появится файл:

- `dist\installer\OneMusicAI-Setup-1.0.1.exe`

> В текущем Linux-контейнере собрать настоящий Windows `setup.exe` нельзя, поэтому подготовлены скрипты/конфиг, которые генерируют его на Windows-машине.

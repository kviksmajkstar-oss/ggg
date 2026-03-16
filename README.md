# OneMusic AI

OneMusic AI — пример полнофункционального музыкального приложения, которое объединяет каталоги Spotify, SoundCloud и YouTube Music в одном интерфейсе, поддерживает перенос плейлистов, изменение скорости треков (slowed / speed up), офлайн-кэш и AI-рекомендации.

> ⚠️ Важно: интеграции с музыкальными сервисами работают только через официальные API и в рамках их ToS. "Скачивание" реализовано как офлайн-кэширование разрешённых preview/stream URL, а не обход DRM.

## Возможности

- Единый поиск и каталог по Spotify / SoundCloud / YouTube Music.
- AI-рекомендации на основе истории прослушивания, лайков и контентных признаков.
- Slowed / Speed Up (изменение playback rate 0.5x–2.0x) на клиенте.
- Перенос плейлистов между сервисами (по метаданным и fuzzy matching).
- Офлайн режим (кэш избранных разрешённых треков).
- Современный UI без рекламных блоков.
- API-first архитектура (FastAPI + SQLite + React).

## Стек

- **Backend:** FastAPI, SQLAlchemy, Pydantic, httpx
- **Frontend:** React + Vite
- **DB:** SQLite (для демо), легко заменить на Postgres
- **AI RecSys:** гибрид content-based + implicit feedback

## Быстрый старт

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173  
Backend: http://localhost:8000

## Переменные окружения

См. `backend/.env.example`.

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SOUNDCLOUD_CLIENT_ID`
- `YTMUSIC_API_KEY` (или прокси к YouTube Data API)
- `DATABASE_URL`

## Тесты

```bash
cd backend
pytest
```

## Ограничения/что нужно для production

- OAuth-потоки для каждого сервиса, refresh token storage.
- Очередь задач (Celery/RQ) для фоновой синхронизации библиотек.
- CDN и encrypted offline storage.
- Полноценные права на офлайн прослушивание у правообладателей.
- Модерация контента и юридический compliance.

## Сборка setup.exe (Windows)

Добавлен инсталляторный пайплайн через Inno Setup.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows_setup.ps1 -AppVersion 1.0.5
```

Результат: `dist\\installer\\OneMusicAI-Setup-1.0.5.exe`.

## Инсталлер как программа (OneMusicInstaller.exe)

Добавлен отдельный GUI-инсталлер как приложение (`OneMusicInstaller.exe`).

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\build_installer_program.ps1 -Version 1.0.7
```

Результат: `dist\\installer-program\\OneMusicInstaller-1.0.7.exe`.


> Если в PowerShell ошибка `npm is not recognized`, установите Node.js LTS и перезапустите терминал,
> либо запускайте скрипты с `-SkipFrontendBuild`, если `frontend/dist` уже существует.

> Если в PowerShell ошибка `python is not recognized` или `.venv\Scripts\python` не найден,
> установите Python 3.10+ и перезапустите терминал (либо используйте `py -3`, скрипт это учитывает автоматически).

> Если venv не создаётся, скрипт теперь проверяет несколько путей к python в окружении
> (`Scripts/python.exe`, `Scripts/python`, `bin/python`, `bin/python3`) и покажет, что именно проверялось.

> Для ошибки `Python exited with code 9009` отключите App Execution Alias для `python.exe/python3.exe`
> (Windows Settings → Apps → App execution aliases), либо установите обычный Python из python.org/winget.

> Если в PowerShell ошибка `pyinstaller is not recognized`, используйте актуальный скрипт: он вызывает `python -m PyInstaller` автоматически.

> Если после сборки появляется ошибка `Installer binary not found after PyInstaller run`,
> проверьте вывод шага PyInstaller выше: скрипт теперь явно покажет все проверенные пути к exe.

> При ошибке `PyInstaller failed with exit code 1` скрипт автоматически пробует fallback сборку `--onedir`,
> а затем ищет exe в обоих вариантах output (`dist/OneMusicInstaller.exe` и `dist/OneMusicInstaller/OneMusicInstaller.exe`).


> Если PowerShell окружение нестабильно, используйте `python installer/build_installer_program.py` — этот путь не зависит от shell-резолвинга `pyinstaller` команды.

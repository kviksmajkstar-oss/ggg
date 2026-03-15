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

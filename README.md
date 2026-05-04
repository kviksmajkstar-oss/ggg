# Telegram AI bot “Mia”

Самая дружелюбная ИИ-подруга «Мия» 🐱✨: поддерживает, хвалит, мягко кокетничает, распознаёт фото и присылает красивые картинки.

## Что от тебя требуется
Подготовь **2 обязательных** значения:
1. `TELEGRAM_BOT_TOKEN` — токен бота из @BotFather в Telegram.
2. `OPENAI_API_KEY` — ключ OpenAI API.

## Быстрый запуск локально
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполни .env
export $(grep -v '^#' .env | xargs)
python bot.py
```

## Что делать в Render (пошагово)
Так как у тебя нет Worker, делаем через **Web Service**.

### 1) Создай Web Service
- Render → **New** → **Web Service**
- Подключи GitHub-репозиторий с этим кодом
- Branch: нужная ветка (обычно `main`)

### 2) Проверь основные настройки
- Runtime: `Python`
- Build Command:
  ```bash
  pip install -r requirements.txt
  ```
- Start Command:
  ```bash
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```

### 3) Добавь Environment Variables
В разделе **Environment** добавь минимум:
- `TELEGRAM_BOT_TOKEN` = твой токен от BotFather
- `OPENAI_API_KEY` = твой API ключ OpenAI

Рекомендуемые дополнительные:
- `OPENAI_MODEL=gpt-4.1-mini`
- `OPENAI_FALLBACK_MODEL=gpt-4o-mini`
- `OPENAI_VISION_MODEL=gpt-4.1-mini`
- `OPENAI_IMAGE_MODEL=gpt-image-1`
- `AUTO_PHOTO_PROB=0.25`
- `AUTONOMOUS_INTERVAL_SEC=14400`
- `MAX_CONTEXT_MSGS=16`
- `BOT_DB_PATH=memory.db`

### 4) Нажми Deploy
После деплоя в логах должно быть:
- установка зависимостей без ошибок,
- запуск `uvicorn app:app ...`,
- и endpoint `/` должен отвечать JSON-ом `{"ok": true, "service": "mia-bot"}`.

### 5) Если бот не отвечает в Telegram
Проверь по порядку:
1. Точно ли задан `TELEGRAM_BOT_TOKEN` (без пробелов)?
2. Точно ли задан `OPENAI_API_KEY`?
3. Есть ли в логах строки `[ERROR] OpenAI ...`?
4. Напиши боту `/start` после деплоя.
5. Убедись, что это **Web Service** (раз Worker недоступен).

## Команды в Telegram
- `/start`
- `/gender <мужской/женский/другое>`
- `/img <описание>`
- `/reset`


## Ошибка `Incorrect API key provided (401)`
Это значит, что `OPENAI_API_KEY` неверный или просроченный.
Сделай так:
1. Открой Render → твой сервис → **Environment**.
2. Замени `OPENAI_API_KEY` на актуальный ключ из https://platform.openai.com/api-keys
3. Нажми **Save Changes** и затем **Manual Deploy**.
4. Проверь логи: ошибка 401 должна исчезнуть.

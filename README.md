# Telegram AI bot “Mia”

Самая дружелюбная ИИ-подруга «Мия» 🐱✨: поддерживает, хвалит, мягко кокетничает, распознаёт фото и присылает красивые картинки.

## Что от тебя требуется
Подготовь **2 обязательных** значения:
1. `TELEGRAM_BOT_TOKEN` — токен бота из @BotFather в Telegram.
2. `OPENAI_API_KEY` — ключ OpenAI API.

Опционально можешь настроить:
- `OPENAI_MODEL` (по умолчанию `gpt-4.1-mini`)
- `OPENAI_VISION_MODEL`
- `OPENAI_IMAGE_MODEL`
- `AUTO_PHOTO_PROB` (как часто Мия сама шлёт фото)
- `AUTONOMOUS_INTERVAL_SEC` (как часто Мия сама пишет первой)

## Куда вставлять
1. Скопируй шаблон:
```bash
cp .env.example .env
```
2. Открой файл `.env` и вставь туда значения:
```env
TELEGRAM_BOT_TOKEN=вставь_сюда_токен_из_BotFather
OPENAI_API_KEY=вставь_сюда_openai_api_key
```
3. Сохрани `.env`.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
python bot.py
```

## Команды в Telegram
- `/start`
- `/gender <мужской/женский/другое>`
- `/img <описание>`
- `/reset`

## Важно
Чтобы бот писал сам и был всегда на связи, держи процесс запущенным 24/7 (например, Railway/Render/VPS).

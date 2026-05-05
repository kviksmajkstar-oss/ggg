# Telegram AI bot “Mia”

## Настройка под Cerebras
Обязательные переменные в Render Environment:
- TELEGRAM_BOT_TOKEN
- CEREBRAS_API_KEY
- CEREBRAS_BASE_URL=https://api.cerebras.ai/v1
- CEREBRAS_MODEL=llama-4-scout-17b-16e-instruct
- CEREBRAS_FALLBACK_MODEL=llama3.1-8b

Если видишь ошибку по ключу, замени CEREBRAS_API_KEY и сделай redeploy.

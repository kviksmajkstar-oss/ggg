import asyncio
import os
import random
import sqlite3
import contextlib
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import AsyncOpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_BASE_URL = os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
MODEL = os.getenv("CEREBRAS_MODEL", "llama-4-scout-17b-16e-instruct")
FALLBACK_MODEL = os.getenv("CEREBRAS_FALLBACK_MODEL", "llama3.1-8b")
VISION_MODEL = os.getenv("CEREBRAS_VISION_MODEL", MODEL)
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")
MAX_CONTEXT_MSGS = int(os.getenv("MAX_CONTEXT_MSGS", "16"))
DB_PATH = os.getenv("BOT_DB_PATH", "memory.db")
AUTO_PHOTO_PROB = float(os.getenv("AUTO_PHOTO_PROB", "0.25"))
AUTONOMOUS_INTERVAL_SEC = int(os.getenv("AUTONOMOUS_INTERVAL_SEC", "14400"))

SYSTEM_PROMPT = "Ты Мия: дружелюбная, поддерживающая, краткая (1-5 предложений), со смайликами."
BLOCKED_WORDS = ["убий", "kill", "murder", "суиц", "самоуб", "зареж", "застрел"]


@dataclass
class ChatStore:
    path: str

    def __post_init__(self):
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS profiles (chat_id INTEGER PRIMARY KEY, user_gender TEXT, bot_gender TEXT DEFAULT 'женский', last_seen INTEGER DEFAULT 0)")
        self.conn.commit()

    def add(self, chat_id: int, role: str, content: str):
        self.conn.execute("INSERT INTO messages(chat_id, role, content) VALUES(?, ?, ?)", (chat_id, role, content))
        self.conn.execute("INSERT INTO profiles(chat_id, last_seen) VALUES(?, ?) ON CONFLICT(chat_id) DO UPDATE SET last_seen=excluded.last_seen", (chat_id, int(time.time())))
        self.conn.commit()

    def history(self, chat_id: int, limit: int) -> List[Dict[str, str]]:
        rows = self.conn.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit)).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def set_gender(self, chat_id: int, user_gender: Optional[str] = None):
        row = self.conn.execute("SELECT chat_id FROM profiles WHERE chat_id=?", (chat_id,)).fetchone()
        if not row:
            self.conn.execute("INSERT INTO profiles(chat_id, user_gender, bot_gender, last_seen) VALUES(?, ?, 'женский', ?)", (chat_id, user_gender, int(time.time())))
        elif user_gender:
            self.conn.execute("UPDATE profiles SET user_gender=?, last_seen=? WHERE chat_id=?", (user_gender, int(time.time()), chat_id))
        self.conn.commit()

    def get_profile_context(self, chat_id: int) -> str:
        row = self.conn.execute("SELECT user_gender, bot_gender FROM profiles WHERE chat_id=?", (chat_id,)).fetchone()
        if not row:
            self.set_gender(chat_id)
            row = (None, "женский")
        return f"Профиль: пол пользователя={row[0] or 'не указан'}; пол Мии={row[1] or 'женский'}."

    def active_chats(self) -> List[int]:
        cutoff = int(time.time()) - AUTONOMOUS_INTERVAL_SEC
        rows = self.conn.execute("SELECT chat_id FROM profiles WHERE last_seen >= ?", (cutoff,)).fetchall()
        return [r[0] for r in rows]


store = ChatStore(DB_PATH)
client = AsyncOpenAI(api_key=CEREBRAS_API_KEY, base_url=CEREBRAS_BASE_URL)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_invalid_api_key_error(err: Exception) -> bool:
    text = str(err)
    return ("invalid_api_key" in text) or ("Incorrect API key" in text) or ("401" in text and "API key" in text)


async def ensure_provider_auth() -> None:
    try:
        await client.models.list()
    except Exception as e:
        if is_invalid_api_key_error(e):
            raise RuntimeError("CEREBRAS_API_KEY invalid. Set valid key in Render Environment and redeploy.") from e
        raise


def enforce_emoji(text: str) -> str:
    return text if any(s in text for s in ["🙂", "😊", "💛", "🐾", "✨", "😿"]) else text + " 🐾"


async def analyze_user_message(chat_id: int, user_text: str) -> str:
    store.add(chat_id, "user", user_text)
    prompt = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "system", "content": store.get_profile_context(chat_id)}] + store.history(chat_id, MAX_CONTEXT_MSGS)
    text = None
    last_error = None
    for model_name in [MODEL, FALLBACK_MODEL]:
        try:
            resp = await client.chat.completions.create(model=model_name, messages=prompt, temperature=0.8, max_tokens=220)
            text = (resp.choices[0].message.content or "").strip() or "Я рядом с тобой 💛"
            break
        except Exception as e:
            last_error = e
            print(f"[ERROR] Cerebras text failed ({model_name}): {e}", flush=True)
    if text is None:
        if last_error and is_invalid_api_key_error(last_error):
            text = "Ошибка ключа Cerebras 🔐 Проверь CEREBRAS_API_KEY в Render → Environment."
        else:
            text = "Я рядом 💛 Временно нет связи с ИИ-сервисом."
    text = enforce_emoji(text)
    store.add(chat_id, "assistant", text)
    return text


async def generate_text(chat_id: int, user_text: str) -> str:
    if any(w in user_text.lower() for w in BLOCKED_WORDS):
        safe = "Не помогу с причинением вреда 😿 Но поддержу безопасно 💛"
        store.add(chat_id, "user", user_text)
        store.add(chat_id, "assistant", safe)
        return safe
    return await analyze_user_message(chat_id, user_text)


@dp.message(CommandStart())
async def start_cmd(message: Message):
    store.set_gender(message.chat.id)
    await message.answer("Привет! Я Мия 🐱✨ Пиши мне, я отвечу и поддержу 💛")


@dp.message(F.text)
async def chat_msg(message: Message):
    try:
        await message.answer(await generate_text(message.chat.id, message.text or ""))
    except Exception as e:
        print(f"[ERROR] chat handler failed: {e}", flush=True)
        await message.answer("Тех. ошибка 😿 Проверь CEREBRAS_API_KEY и модель.")


async def autonomous_ping_loop():
    while True:
        await asyncio.sleep(AUTONOMOUS_INTERVAL_SEC)
        for chat_id in store.active_chats():
            with contextlib.suppress(Exception):
                await bot.send_message(chat_id, "Я о тебе помню 🌙 Как ты? 💛")


async def main():
    if not BOT_TOKEN or not CEREBRAS_API_KEY:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and CEREBRAS_API_KEY")
    await ensure_provider_auth()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

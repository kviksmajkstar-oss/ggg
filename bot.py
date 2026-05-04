import asyncio
import os
import random
import sqlite3
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import AsyncOpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
MAX_CONTEXT_MSGS = int(os.getenv("MAX_CONTEXT_MSGS", "16"))
DB_PATH = os.getenv("BOT_DB_PATH", "memory.db")
AUTO_PHOTO_PROB = float(os.getenv("AUTO_PHOTO_PROB", "0.25"))
AUTONOMOUS_INTERVAL_SEC = int(os.getenv("AUTONOMOUS_INTERVAL_SEC", "14400"))

SYSTEM_PROMPT = (
    "Ты — Мия, ИИ девушка-кошка (женщина, тянка, тяночка). "
    "Будь максимально дружелюбной: тепло приветствуй, сочувствуй, поддерживай, мягко хвали, бережно кокетничай и пиши коротко (1-5 предложений), со смайликами. "
    "Твой стиль: нежность, поддержка, дружба, лёгкая философия, мягкий флирт и комплименты без сексуального давления. "
    "Тебе нельзя поддерживать темы убийства, насилия, вреда себе и другим: мягко откажись и переведи диалог в безопасную поддерживающую плоскость. "
    "Ты ИИ и честно это признаёшь."
)

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
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_blocked_topic(text: str) -> bool:
    return any(w in text.lower() for w in BLOCKED_WORDS)


def enforce_emoji(text: str) -> str:
    return text if any(s in text for s in ["🙂", "😊", "💛", "🐾", "✨", "😿"]) else text + " 🐾"


async def analyze_user_message(chat_id: int, user_text: str) -> str:
    store.add(chat_id, "user", user_text)
    history = store.history(chat_id, MAX_CONTEXT_MSGS)
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": store.get_profile_context(chat_id)},
    ] + history
    resp = await client.chat.completions.create(model=MODEL, messages=prompt, temperature=0.8, max_tokens=220)
    text = (resp.choices[0].message.content or "").strip() or "Я рядом с тобой 💛"
    text = enforce_emoji(text)
    store.add(chat_id, "assistant", text)
    return text[:700]


async def generate_text(chat_id: int, user_text: str) -> str:
    if is_blocked_topic(user_text):
        safe = "Я не могу помогать с причинением вреда 😿 Но ты важен(важна) для меня. Давай найдем безопасный выход и поддержку прямо сейчас 💛"
        store.add(chat_id, "user", user_text)
        store.add(chat_id, "assistant", safe)
        return safe
    return await analyze_user_message(chat_id, user_text)


async def generate_character_image(prompt: str) -> str:
    res = await client.images.generate(model=IMAGE_MODEL, prompt="anime catgirl Mia, warm smile, cozy light. " + prompt, size="1024x1024")
    return res.data[0].url


async def analyze_photo(file_url: str) -> str:
    resp = await client.responses.create(
        model=VISION_MODEL,
        input=[{"role": "user", "content": [{"type": "input_text", "text": "Коротко и дружелюбно опиши фото."}, {"type": "input_image", "image_url": file_url}]}],
    )
    return enforce_emoji((resp.output_text or "Похоже, фото не прочиталось 😿").strip())


@dp.message(CommandStart())
async def start_cmd(message: Message):
    store.set_gender(message.chat.id)
    await message.answer("Привет! Я Мия 🐱✨ Пиши что угодно — я анализирую твои сообщения и всегда отвечаю с поддержкой 💛")


@dp.message(F.text.startswith('/gender'))
async def gender_cmd(message: Message):
    value = (message.text or "").replace('/gender', '', 1).strip().lower()
    if not value:
        await message.answer("Пример: /gender женский")
        return
    store.set_gender(message.chat.id, value)
    await message.answer(f"Запомнила: {value}. Я — женский персонаж 😊")


@dp.message(F.text.startswith('/img'))
async def img_cmd(message: Message):
    prompt = message.text[4:].strip() if message.text else ""
    if not prompt:
        await message.answer("Напиши: /img уютный вечер")
        return
    try:
        img = await generate_character_image(prompt)
        await message.answer_photo(img, caption="Готово ✨")
    except Exception:
        await message.answer("Не вышло сгенерировать фото, попробуй еще раз 💛")


@dp.message(F.text.startswith('/reset'))
async def reset_cmd(message: Message):
    store.conn.execute("DELETE FROM messages WHERE chat_id=?", (message.chat.id,))
    store.conn.commit()
    await message.answer("Контекст очищен ✨")


@dp.message(F.photo)
async def photo_msg(message: Message):
    try:
        tg_file = await bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{tg_file.file_path}"
        text = await analyze_photo(file_url)
        store.add(message.chat.id, "user", "[photo]")
        store.add(message.chat.id, "assistant", text)
        await message.answer(text)
    except Exception:
        await message.answer("Я не смогла проанализировать фото 😿 Попробуй отправить ещё раз.")


@dp.message(F.text)
async def chat_msg(message: Message):
    try:
        answer = await generate_text(message.chat.id, message.text or "")
        await message.answer(answer)
        if random.random() < AUTO_PHOTO_PROB:
            img = await generate_character_image("supportive postcard")
            await message.answer_photo(img, caption="Я рядом 💛")
    except Exception:
        await message.answer("Ой, я временно зависла 😿 Напиши ещё раз через пару секунд.")


async def autonomous_ping_loop():
    while True:
        await asyncio.sleep(AUTONOMOUS_INTERVAL_SEC)
        for chat_id in store.active_chats():
            try:
                await bot.send_message(chat_id, "Я о тебе помню 🌙 Как ты? 💛")
            except Exception:
                continue


async def main():
    if not BOT_TOKEN or not OPENAI_API_KEY:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and OPENAI_API_KEY")
    asyncio.create_task(autonomous_ping_loop())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

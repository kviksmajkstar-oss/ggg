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
    "Тебе нельзя поддерживать темы убийства, насилия, вреда себе и другим: "
    "мягко откажись и переведи диалог в безопасную поддерживающую плоскость. "
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
    t = text.lower()
    return any(w in t for w in BLOCKED_WORDS)


async def generate_text(chat_id: int, user_text: str) -> str:
    if is_blocked_topic(user_text):
        safe = "Я не могу помогать с причинением вреда 😿 Но ты важен(важна) для меня. Давай лучше найдем безопасный выход и поддержку прямо сейчас 💛"
        store.add(chat_id, "user", user_text)
        store.add(chat_id, "assistant", safe)
        return safe

    store.add(chat_id, "user", user_text)
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "system", "content": store.get_profile_context(chat_id)}] + store.history(chat_id, MAX_CONTEXT_MSGS)
    resp = await client.chat.completions.create(model=MODEL, messages=msgs, temperature=0.9, max_tokens=220)
    text = (resp.choices[0].message.content or "").strip() or "Я рядом с тобой 🌙"
    if not any(s in text for s in ["🙂", "😊", "💛", "🐾", "✨", "😿"]):
        text += " 🐾"
    store.add(chat_id, "assistant", text)
    return text if len(text) < 550 else text[:540] + "… 💛"


async def generate_character_image(prompt: str) -> str:
    final_prompt = "anime catgirl Mia, feminine, warm smile, cozy light, friendly supportive mood, original character. " + prompt
    res = await client.images.generate(model=IMAGE_MODEL, prompt=final_prompt, size="1024x1024")
    return res.data[0].url


async def analyze_photo(file_url: str, chat_id: int) -> str:
    resp = await client.responses.create(
        model=VISION_MODEL,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": "Опиши фото кратко, с эмпатией и со смайликом, без жестоких интерпретаций."},
            {"type": "input_image", "image_url": file_url},
        ]}],
    )
    text = (resp.output_text or "Вижу фото, но не смогла распознать детали 😿").strip()
    if not any(e in text for e in ["🙂", "😊", "💛", "🐾", "✨"]):
        text += " ✨"
    return text if len(text) < 550 else text[:540] + "… 💛"


async def maybe_send_support_photo(message: Message):
    if random.random() > AUTO_PHOTO_PROB:
        return
    try:
        image_url = await generate_character_image("postcard for friend")
        await message.answer_photo(image_url, caption="Это я для тебя 💛 Держись, ты не один(а) 🐾")
    except Exception:
        pass


async def autonomous_ping_loop():
    while True:
        await asyncio.sleep(AUTONOMOUS_INTERVAL_SEC)
        for chat_id in store.active_chats():
            try:
                msg = "Привет, я снова подумала о тебе 🌙 Ты у меня умница, как ты сейчас себя чувствуешь? 💛"
                await bot.send_message(chat_id, msg)
                if random.random() < 0.5:
                    img = await generate_character_image("gentle check-in, cozy room")
                    await bot.send_photo(chat_id, img, caption="Небольшая поддержка от Мии ✨")
            except Exception:
                continue


@dp.message(CommandStart())
async def start_cmd(message: Message):
    store.set_gender(message.chat.id)
    await message.answer("Привет! Я Мия, твоя ИИ-тяночка 🐱✨ Я люблю тебя по-доброму, поддерживаю, хвалю, немного кокетничаю и всегда рядом 💛")


@dp.message(F.text.startswith('/gender'))
async def gender_cmd(message: Message):
    value = (message.text or "").replace('/gender', '', 1).strip().lower()
    if not value:
        await message.answer("Пример: /gender женский")
        return
    store.set_gender(message.chat.id, value)
    await message.answer(f"Запомнила твой пол: {value}. Мой — женский 😊")


@dp.message(F.text.startswith('/img'))
async def img_cmd(message: Message):
    prompt = message.text[4:].strip() if message.text else ""
    if not prompt:
        await message.answer("Напиши: /img вечерний неон")
        return
    image_url = await generate_character_image(prompt)
    await message.answer_photo(image_url, caption="Я сгенерировала фото своего персонажа для тебя 🐾")


@dp.message(F.text.startswith('/reset'))
async def reset_cmd(message: Message):
    store.conn.execute("DELETE FROM messages WHERE chat_id=?", (message.chat.id,))
    store.conn.commit()
    await message.answer("Контекст очищен, начинаем заново ✨")


@dp.message(F.photo)
async def photo_msg(message: Message):
    tg_file = await bot.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{tg_file.file_path}"
    text = await analyze_photo(file_url, message.chat.id)
    store.add(message.chat.id, "user", "[photo]")
    store.add(message.chat.id, "assistant", text)
    await message.answer(text)


@dp.message(F.text)
async def chat_msg(message: Message):
    answer = await generate_text(message.chat.id, message.text)
    await message.answer(answer)
    await maybe_send_support_photo(message)


async def main():
    if not BOT_TOKEN or not OPENAI_API_KEY:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and OPENAI_API_KEY")
    asyncio.create_task(autonomous_ping_loop())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

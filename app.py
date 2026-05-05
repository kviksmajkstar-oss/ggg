import asyncio
import os
from contextlib import suppress

from fastapi import FastAPI

from bot import dp, bot, BOT_TOKEN, CEREBRAS_API_KEY, autonomous_ping_loop, ensure_provider_auth

app = FastAPI(title="Mia Bot Service")
_polling_task: asyncio.Task | None = None
_ping_task: asyncio.Task | None = None


@app.on_event("startup")
async def on_startup():
    global _polling_task, _ping_task
    if not BOT_TOKEN or not CEREBRAS_API_KEY:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and CEREBRAS_API_KEY")
    await ensure_provider_auth()

    async def _run_polling():
        await dp.start_polling(bot)

    _ping_task = asyncio.create_task(autonomous_ping_loop())
    _polling_task = asyncio.create_task(_run_polling())


@app.on_event("shutdown")
async def on_shutdown():
    global _polling_task, _ping_task
    if _polling_task:
        _polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await _polling_task
    if _ping_task:
        _ping_task.cancel()
        with suppress(asyncio.CancelledError):
            await _ping_task


@app.get("/")
async def health():
    return {"ok": True, "service": "mia-bot"}

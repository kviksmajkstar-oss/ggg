from __future__ import annotations

import argparse
import asyncio
import contextlib
import sys
from dataclasses import dataclass

from messenger.protocol import ProtocolError, encode, decode


@dataclass(slots=True)
class ParsedInput:
    action: str | None
    payload: dict
    room: str
    local_message: str | None = None


def parse_user_input(line: str, current_room: str) -> ParsedInput:
    text = line.strip()
    if not text:
        return ParsedInput(None, {}, current_room)

    if not text.startswith("/"):
        return ParsedInput("send_room", {"room": current_room, "text": text}, current_room)

    parts = text.split(maxsplit=2)
    command = parts[0].lower()

    if command in {"/quit", "/exit"}:
        return ParsedInput("leave", {}, current_room)
    if command == "/help":
        return ParsedInput(
            None,
            {},
            current_room,
            "Команды: /join <room>, /leave <room>, /room <room> <text>, /dm <user> <text>, /users, /rooms, /history room <room>, /history dm <user>, /quit",
        )
    if command == "/join" and len(parts) >= 2:
        room = parts[1]
        return ParsedInput("join_room", {"room": room}, room)
    if command == "/leave" and len(parts) >= 2:
        return ParsedInput("leave_room", {"room": parts[1]}, current_room)
    if command == "/room" and len(parts) >= 3:
        room = parts[1]
        return ParsedInput("send_room", {"room": room, "text": parts[2]}, room)
    if command == "/dm" and len(parts) >= 3:
        return ParsedInput("send_dm", {"to": parts[1], "text": parts[2]}, current_room)
    if command == "/users":
        return ParsedInput("list_users", {}, current_room)
    if command == "/rooms":
        return ParsedInput("list_rooms", {}, current_room)
    if command == "/history" and len(parts) >= 3:
        kind = parts[1]
        target = parts[2]
        return ParsedInput("history", {"kind": kind, "target": target}, current_room)

    return ParsedInput(None, {}, current_room, "Неизвестная команда. Введите /help")


async def read_stdin(queue: asyncio.Queue[str]) -> None:
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            await queue.put("/quit")
            return
        await queue.put(line.rstrip("\n"))


def print_packet(action: str, payload: dict) -> None:
    if action == "room_message":
        print(f"[{payload.get('room')}] [{payload.get('timestamp')}] {payload.get('sender')}: {payload.get('text')}")
    elif action == "dm_message":
        print(f"[DM] [{payload.get('timestamp')}] {payload.get('sender')} -> {payload.get('to')}: {payload.get('text')}")
    elif action == "history":
        print(f"[history:{payload.get('kind')}:{payload.get('target')}] ")
        for item in payload.get("messages", []):
            print(f"  - [{item.get('timestamp')}] {item.get('sender')}: {item.get('text')}")
    elif action == "users":
        print("[users] " + ", ".join(payload.get("users", [])))
    elif action == "rooms":
        print("[rooms] " + ", ".join(payload.get("rooms", [])))
    elif action == "system":
        print(f"[system] {payload.get('message', payload.get('text', ''))}")
    elif action == "error":
        print(f"[error] {payload.get('message')}")
    else:
        print(f"[{action}] {payload}")


async def receiver(reader: asyncio.StreamReader) -> None:
    while not reader.at_eof():
        line = await reader.readline()
        if not line:
            return
        try:
            packet = decode(line)
        except ProtocolError as exc:
            print(f"[error] broken packet from server: {exc}")
            continue
        print_packet(packet.action, packet.payload)


async def sender(writer: asyncio.StreamWriter, start_room: str) -> None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    stdin_task = asyncio.create_task(read_stdin(queue))
    room = start_room
    try:
        while True:
            raw = await queue.get()
            parsed = parse_user_input(raw, room)
            room = parsed.room

            if parsed.local_message:
                print(f"[local] {parsed.local_message}")
            if parsed.action is None:
                continue

            writer.write(encode(parsed.action, parsed.payload))
            await writer.drain()
            if parsed.action == "leave":
                return
    finally:
        stdin_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stdin_task


async def run_client(host: str, port: int, name: str) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(encode("join", {"name": name}))
    await writer.drain()

    recv_task = asyncio.create_task(receiver(reader))
    send_task = asyncio.create_task(sender(writer, "main"))

    done, pending = await asyncio.wait({recv_task, send_task}, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    for task in done:
        with contextlib.suppress(asyncio.CancelledError):
            await task

    writer.close()
    await writer.wait_closed()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telegram-like terminal messenger client")
    parser.add_argument("name", help="Display name")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=9000, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(run_client(args.host, args.port, args.name))
    except KeyboardInterrupt:
        print("\n[client] disconnected")

from __future__ import annotations

import argparse
import asyncio
import contextlib
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, Dict, Tuple

from messenger.protocol import ProtocolError, encode, decode

HISTORY_LIMIT = 100


@dataclass(slots=True)
class Message:
    timestamp: str
    sender: str
    text: str


@dataclass(slots=True)
class Client:
    name: str
    writer: asyncio.StreamWriter


class TelegramLikeServer:
    def __init__(self) -> None:
        self._clients_by_writer: Dict[asyncio.StreamWriter, Client] = {}
        self._clients_by_name: Dict[str, asyncio.StreamWriter] = {}
        self._rooms: Dict[str, set[asyncio.StreamWriter]] = defaultdict(set)
        self._room_history: Dict[str, Deque[Message]] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))
        self._dm_history: Dict[Tuple[str, str], Deque[Message]] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))

    async def run(self, host: str, port: int) -> None:
        server = await asyncio.start_server(self._handle_client, host, port)
        addresses = ", ".join(str(sock.getsockname()) for sock in (server.sockets or []))
        print(f"[server] Telegram-like messenger listening on {addresses}")
        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            join_packet = decode(await reader.readline())
            if join_packet.action != "join":
                await self._send(writer, "error", {"message": "first packet must be join"})
                return

            name = str(join_packet.payload.get("name", "")).strip()
            if not name:
                await self._send(writer, "error", {"message": "name is required"})
                return
            if name in self._clients_by_name:
                await self._send(writer, "error", {"message": "name is already online"})
                return

            client = Client(name=name, writer=writer)
            self._clients_by_writer[writer] = client
            self._clients_by_name[name] = writer

            await self._join_room(writer, "main")
            await self._send(writer, "system", {"message": f"Привет, {name}! Добро пожаловать в main."})
            await self._send(writer, "system", {"message": "Команды: /join /leave /room /dm /users /rooms /history /help"})
            await self._broadcast_room("main", "system", f"{name} вошёл в чат", exclude=writer)

            while not reader.at_eof():
                line = await reader.readline()
                if not line:
                    break
                try:
                    packet = decode(line)
                except ProtocolError as exc:
                    await self._send(writer, "error", {"message": str(exc)})
                    continue
                await self._process_packet(writer, packet.action, packet.payload)
        except ProtocolError:
            pass
        finally:
            await self._disconnect(writer)

    async def _process_packet(self, writer: asyncio.StreamWriter, action: str, payload: dict) -> None:
        client = self._clients_by_writer.get(writer)
        if client is None:
            return

        if action == "send_room":
            room = str(payload.get("room", "main")).strip() or "main"
            text = str(payload.get("text", "")).strip()
            if not text:
                return
            if writer not in self._rooms.get(room, set()):
                await self._send(writer, "error", {"message": f"Вы не состоите в комнате '{room}'"})
                return
            msg = Message(timestamp=self._now(), sender=client.name, text=text)
            self._room_history[room].append(msg)
            await self._broadcast_room(room, "room_message", text, sender=client.name, timestamp=msg.timestamp)
        elif action == "join_room":
            room = str(payload.get("room", "")).strip()
            if not room:
                await self._send(writer, "error", {"message": "room is required"})
                return
            await self._join_room(writer, room)
            await self._send_room_history(writer, room)
        elif action == "leave_room":
            room = str(payload.get("room", "")).strip()
            await self._leave_room(writer, room)
        elif action == "send_dm":
            recipient = str(payload.get("to", "")).strip()
            text = str(payload.get("text", "")).strip()
            if not recipient or not text:
                await self._send(writer, "error", {"message": "to and text are required"})
                return
            await self._send_dm(client.name, recipient, text)
        elif action == "list_users":
            await self._send(writer, "users", {"users": sorted(self._clients_by_name.keys())})
        elif action == "list_rooms":
            await self._send(writer, "rooms", {"rooms": sorted(self._rooms.keys())})
        elif action == "history":
            kind = str(payload.get("kind", "")).strip()
            target = str(payload.get("target", "")).strip()
            if kind == "room":
                await self._send_room_history(writer, target or "main")
            elif kind == "dm" and target:
                await self._send_dm_history(writer, client.name, target)
            else:
                await self._send(writer, "error", {"message": "history requires kind=room|dm and target"})
        elif action == "leave":
            await self._disconnect(writer)
        else:
            await self._send(writer, "error", {"message": f"unknown action: {action}"})

    async def _join_room(self, writer: asyncio.StreamWriter, room: str) -> None:
        client = self._clients_by_writer[writer]
        room_set = self._rooms[room]
        if writer in room_set:
            await self._send(writer, "system", {"message": f"Вы уже в комнате '{room}'"})
            return
        room_set.add(writer)
        await self._send(writer, "system", {"message": f"Вы вошли в комнату '{room}'"})
        await self._broadcast_room(room, "system", f"{client.name} присоединился", exclude=writer)

    async def _leave_room(self, writer: asyncio.StreamWriter, room: str) -> None:
        client = self._clients_by_writer.get(writer)
        if client is None or not room:
            return
        room_set = self._rooms.get(room)
        if not room_set or writer not in room_set:
            await self._send(writer, "error", {"message": f"Вы не состоите в комнате '{room}'"})
            return
        room_set.discard(writer)
        await self._send(writer, "system", {"message": f"Вы вышли из комнаты '{room}'"})
        await self._broadcast_room(room, "system", f"{client.name} покинул комнату", exclude=writer)
        if not room_set:
            self._rooms.pop(room, None)

    async def _send_room_history(self, writer: asyncio.StreamWriter, room: str) -> None:
        history = [msg.__dict__ for msg in self._room_history.get(room, [])]
        await self._send(writer, "history", {"kind": "room", "target": room, "messages": history})

    async def _send_dm_history(self, writer: asyncio.StreamWriter, user_a: str, user_b: str) -> None:
        key = tuple(sorted((user_a, user_b)))
        history = [msg.__dict__ for msg in self._dm_history.get(key, [])]
        await self._send(writer, "history", {"kind": "dm", "target": user_b, "messages": history})

    async def _send_dm(self, sender: str, recipient: str, text: str) -> None:
        timestamp = self._now()
        message = Message(timestamp=timestamp, sender=sender, text=text)
        key = tuple(sorted((sender, recipient)))
        self._dm_history[key].append(message)

        sender_writer = self._clients_by_name.get(sender)
        recipient_writer = self._clients_by_name.get(recipient)
        payload = {"sender": sender, "to": recipient, "text": text, "timestamp": timestamp}
        if sender_writer:
            await self._send(sender_writer, "dm_message", payload)
        if recipient_writer and recipient_writer is not sender_writer:
            await self._send(recipient_writer, "dm_message", payload)

    async def _broadcast_room(
        self,
        room: str,
        action: str,
        text: str,
        *,
        sender: str | None = None,
        timestamp: str | None = None,
        exclude: asyncio.StreamWriter | None = None,
    ) -> None:
        dead: list[asyncio.StreamWriter] = []
        payload = {"room": room, "text": text, "timestamp": timestamp or self._now()}
        if sender:
            payload["sender"] = sender

        for peer_writer in self._rooms.get(room, set()):
            if peer_writer is exclude:
                continue
            try:
                await self._send(peer_writer, action, payload)
            except ConnectionError:
                dead.append(peer_writer)

        for dead_writer in dead:
            await self._disconnect(dead_writer)

    async def _send(self, writer: asyncio.StreamWriter, action: str, payload: dict) -> None:
        writer.write(encode(action, payload))
        await writer.drain()

    async def _disconnect(self, writer: asyncio.StreamWriter) -> None:
        client = self._clients_by_writer.pop(writer, None)
        if client is None:
            with contextlib.suppress(Exception):
                writer.close()
                await writer.wait_closed()
            return

        self._clients_by_name.pop(client.name, None)

        for room, room_members in list(self._rooms.items()):
            if writer in room_members:
                room_members.discard(writer)
                await self._broadcast_room(room, "system", f"{client.name} вышел из сети", exclude=writer)
                if not room_members:
                    self._rooms.pop(room, None)

        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telegram-like messenger server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=9000, type=int)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await TelegramLikeServer().run(args.host, args.port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[server] stopped")

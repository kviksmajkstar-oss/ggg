from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict


class ProtocolError(ValueError):
    """Raised when a packet is invalid."""


@dataclass(slots=True)
class Packet:
    action: str
    payload: Dict[str, Any]

    def to_bytes(self) -> bytes:
        return (json.dumps({"action": self.action, "payload": self.payload}, ensure_ascii=False) + "\n").encode("utf-8")


def encode(action: str, payload: Dict[str, Any]) -> bytes:
    return Packet(action=action, payload=payload).to_bytes()


def decode(line: bytes) -> Packet:
    try:
        raw = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("invalid JSON payload") from exc

    if not isinstance(raw, dict):
        raise ProtocolError("packet must be an object")

    action = raw.get("action")
    payload = raw.get("payload")
    if not isinstance(action, str) or not action:
        raise ProtocolError("action must be a non-empty string")
    if not isinstance(payload, dict):
        raise ProtocolError("payload must be an object")

    return Packet(action=action, payload=payload)

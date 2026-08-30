"""
Session — one client connection.

Mirrors src/network/Session.hpp/cpp: owns the socket (here: an asyncio
StreamReader/StreamWriter pair), tracks the logged-in username once
`login` succeeds, and exposes `deliver()` so other sessions (via
Handlers) can push a message to this client out-of-band (e.g. a live
"new_message" push when the recipient is online).
"""
from __future__ import annotations

import asyncio
from typing import Optional

from . import protocol


# сесия пользователя
class Session:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self.reader = reader
        self.writer = writer
        self.username: Optional[str] = None
        self._send_lock = asyncio.Lock()

    def peer(self) -> str:
        try:
            addr = self.writer.get_extra_info("peername")
            return f"{addr[0]}:{addr[1]}" if addr else "unknown"
        except Exception:
            return "unknown"

    def set_username(self, username: str) -> None:
        self.username = username

    async def deliver(self, message: dict) -> bool:
        """Push a message to this client. Returns False if the send failed."""
        try:
            async with self._send_lock:
                await protocol.send_message(self.writer, message)
            return True
        except (ConnectionError, OSError):
            return False

    async def send(self, message: dict) -> None:
        async with self._send_lock:
            await protocol.send_message(self.writer, message)

    async def close(self) -> None:
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except (ConnectionError, OSError):
            pass

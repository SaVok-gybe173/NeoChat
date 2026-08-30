"""
Server — asyncio TCP server accepting connections and running the
request/response loop for each one.

Mirrors src/network/Server.hpp/cpp + the read loop in Session::run():
the C++ version spawns one OS thread per connection; this version spawns
one asyncio task per connection instead, which scales further and needs
no manual mutexes around shared state (see rate_limiter.py / database.py
docstrings for why).
"""
from __future__ import annotations

import asyncio
import logging

from . import protocol
from .router import Router
from .session import Session

logger = logging.getLogger("neochat")


class Server:
    def __init__(self, host: str, port: int, router: Router) -> None:
        self.host = host
        self.port = port
        self.router = router
        self._server: asyncio.AbstractServer | None = None
        self._sessions: set[Session] = set()

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        logger.info(f"Server listening on {self.host}:{self.port}")

    async def serve_forever(self) -> None:
        assert self._server is not None
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

        sessions = list(self._sessions)
        self._sessions.clear()
        for session in sessions:
            await session.close()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        session = Session(reader, writer)
        self._sessions.add(session)
        peer = session.peer()
        logger.debug(f"Client connected: {peer}")

        try:
            while True:
                try:
                    request = await protocol.read_message(reader)
                except protocol.ConnectionClosed:
                    break
                except ValueError as exc:
                    # Malformed JSON: reply with an error, keep the connection open.
                    await session.send({"status": "error", "message": str(exc)})
                    continue

                response = await self.router.route(request, session)
                try:
                    await session.send(response)
                except (ConnectionError, OSError):
                    break
        finally:
            self._sessions.discard(session)
            await session.close()
            if session.username:
                self.router.on_user_disconnected(session.username)
            logger.debug(f"Client disconnected: {peer}")

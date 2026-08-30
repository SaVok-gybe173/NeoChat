#!/usr/bin/env python3
"""
NeoChat server entry point.

Mirrors src/main.cpp: load config.ini (or a path passed as argv[1]),
open the JSON database, wire up Handlers -> Router -> Server, and run
until SIGINT/SIGTERM.

Usage:
    python main.py [config.ini]
"""
from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

from neochat_server.config import Config
from neochat_server.database import JsonDatabase
from neochat_server.handlers import Handlers
from neochat_server.logger import setup_logger
from neochat_server.router import Router
from neochat_server.server import Server


async def run(config_file: str) -> int:
    logger = setup_logger("server.log")
    logger.info("Server starting...")

    config = Config()
    if not config.load(config_file):
        logger.error(f"Failed to load config: {config_file}")
        return 1

    host = config.get_string("server", "host", "0.0.0.0")
    port = config.get_int("server", "port", 8080)

    users_file = config.get_string("database", "users_file", "data/users.json")
    messages_file = config.get_string("database", "messages_file", "data/messages.json")

    Path(users_file).parent.mkdir(parents=True, exist_ok=True)
    Path(messages_file).parent.mkdir(parents=True, exist_ok=True)

    db = JsonDatabase(users_file, messages_file)
    if not await db.init():
        logger.error("Failed to init database")
        return 1

    handlers = Handlers(db)
    router = Router(handlers)
    server = Server(host, port, router)

    if not await _try_start(server, logger):
        await db.close()
        return 1

    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # add_signal_handler isn't available on Windows; fall back to
            # the default KeyboardInterrupt behaviour for SIGINT there.
            pass

    serve_task = asyncio.create_task(server.serve_forever())
    await stop_event.wait()

    await server.stop()
    serve_task.cancel()
    try:
        await serve_task
    except asyncio.CancelledError:
        pass

    await db.close()
    logger.info("Server stopped")
    return 0


async def _try_start(server: Server, logger) -> bool:
    try:
        await server.start()
        return True
    except OSError as exc:
        logger.error(f"Failed to start server: {exc}")
        return False


def main() -> int:
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
    try:
        return asyncio.run(run(config_file))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""
protocol — wire format shared with the original C++ server.

Each message (request or response) is framed as:

    [4 bytes: big-endian uint32 length] [N bytes: UTF-8 JSON payload]

This matches Session.cpp exactly (htonl/ntohl == network byte order ==
big-endian), so this Python server is wire-compatible with any existing
client written against the original protocol.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 MiB, matches Session.cpp


class ConnectionClosed(Exception):
    """Raised when the peer closes the connection or sends a malformed frame."""


async def read_message(reader: asyncio.StreamReader) -> dict:
    """Read one length-prefixed JSON message. Raises ConnectionClosed on EOF/bad frame."""
    header = await _read_exact(reader, 4)
    length = int.from_bytes(header, byteorder="big", signed=False)
    if length == 0 or length > MAX_MESSAGE_SIZE:
        raise ConnectionClosed(f"invalid frame length: {length}")

    payload = await _read_exact(reader, length)
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Parse error: {exc}") from exc


async def send_message(writer: asyncio.StreamWriter, obj: dict) -> None:
    """Write one length-prefixed JSON message."""
    payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    header = len(payload).to_bytes(4, byteorder="big", signed=False)
    writer.write(header + payload)
    await writer.drain()


async def _read_exact(reader: asyncio.StreamReader, n: int) -> bytes:
    try:
        data = await reader.readexactly(n)
    except (asyncio.IncompleteReadError, ConnectionResetError) as exc:
        raise ConnectionClosed(str(exc)) from exc
    return data

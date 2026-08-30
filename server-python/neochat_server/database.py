"""
database — JSON-file-backed storage for users and messages.

Mirrors src/database/IDatabase.hpp and src/database/JsonDatabase.hpp/cpp:
two flat JSON files (users.json, messages.json), an in-memory cache kept
in sync, dirty flags, and a periodic background flush (every 5s) plus a
flush on shutdown. Writes go through a temp file + atomic rename, same
as the original (std::filesystem::rename after writing a ".tmp" file).

As with rate_limiter.py, no locks are used: everything here runs
synchronously within a single asyncio event loop thread, so dict/list
mutations are already atomic with respect to other coroutines.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class User:
    username: str
    password_hash: str
    salt: str
    email: str = ""
    public_key: Optional[str] = None


@dataclass
class Message:
    id: int
    from_: str
    to: str
    content: str
    timestamp: int
    encrypted: bool = False
    ephemeral_key: str = ""
    nonce: str = ""
    salt: str = ""


def _read_json(path: Path, default: dict) -> dict:
    if not path.is_file():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def _write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


class JsonDatabase:
    def __init__(self, users_file: str, messages_file: str) -> None:
        self.users_file = Path(users_file)
        self.messages_file = Path(messages_file)

        self._users: List[dict] = []
        self._messages: List[dict] = []
        self._next_msg_id = 1

        self._dirty_users = False
        self._dirty_messages = False
        self._flush_task: Optional[asyncio.Task] = None

    # -- lifecycle ---------------------------------------------------

    async def init(self) -> bool:
        self._load_users()
        self._load_messages()
        self._flush_task = asyncio.create_task(self._flush_loop())
        return True

    async def close(self) -> None:
        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        self.flush()

    async def _flush_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(5)
                self.flush()
        except asyncio.CancelledError:
            raise

    def flush(self) -> None:
        if self._dirty_users:
            self._dirty_users = False
            self._save_users()
        if self._dirty_messages:
            self._dirty_messages = False
            self._save_messages()

    # -- persistence ---------------------------------------------------

    def _load_users(self) -> None:
        data = _read_json(self.users_file, {"users": []})
        self._users = data.get("users", [])

    def _save_users(self) -> None:
        _write_json_atomic(self.users_file, {"users": self._users})

    def _load_messages(self) -> None:
        data = _read_json(self.messages_file, {"messages": []})
        self._messages = data.get("messages", [])
        self._next_msg_id = 1
        for m in self._messages:
            mid = int(m.get("id", 0))
            if mid >= self._next_msg_id:
                self._next_msg_id = mid + 1

    def _save_messages(self) -> None:
        _write_json_atomic(self.messages_file, {"messages": self._messages})

    # -- users ---------------------------------------------------

    def add_user(self, user: User) -> bool:
        for u in self._users:
            if u.get("username") == user.username:
                return False
        self._users.append(
            {
                "username": user.username,
                "passwordHash": user.password_hash,
                "salt": user.salt,
                "email": user.email,
            }
        )
        self._dirty_users = True
        return True

    def get_user(self, username: str) -> Optional[User]:
        for u in self._users:
            if u.get("username") == username:
                return User(
                    username=u.get("username", ""),
                    password_hash=u.get("passwordHash", ""),
                    salt=u.get("salt", ""),
                    email=u.get("email", ""),
                    public_key=u.get("public_key"),
                )
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        for u in self._users:
            if u.get("email") == email:
                return User(
                    username=u.get("username", ""),
                    password_hash=u.get("passwordHash", ""),
                    salt=u.get("salt", ""),
                    email=u.get("email", ""),
                    public_key=u.get("public_key"),
                )
        return None

    def update_user_public_key(self, username: str, public_key: str) -> bool:
        for u in self._users:
            if u.get("username") == username:
                u["public_key"] = public_key
                self._dirty_users = True
                return True
        return False

    def get_user_public_key(self, username: str) -> Optional[str]:
        for u in self._users:
            if u.get("username") == username:
                return u.get("public_key")
        return None

    def get_all_users(self) -> List[str]:
        return [u.get("username", "") for u in self._users]

    # -- messages ---------------------------------------------------

    def add_message(self, msg: Message) -> int:
        msg_id = self._next_msg_id
        self._next_msg_id += 1
        self._messages.append(
            {
                "id": msg_id,
                "from": msg.from_,
                "to": msg.to,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "encrypted": msg.encrypted,
                "ephemeral_key": msg.ephemeral_key,
                "nonce": msg.nonce,
                "salt": msg.salt,
            }
        )
        self._dirty_messages = True
        return msg_id

    def get_messages(
        self, user1: str, user2: str, limit: int = 0, offset: int = 0
    ) -> List[dict]:
        result = [
            m
            for m in self._messages
            if (m.get("from") == user1 and m.get("to") == user2)
            or (m.get("from") == user2 and m.get("to") == user1)
        ]
        result.sort(key=lambda m: m.get("timestamp", 0))

        if offset > 0:
            result = result[offset:] if offset < len(result) else []
        if limit > 0:
            result = result[:limit]
        return result

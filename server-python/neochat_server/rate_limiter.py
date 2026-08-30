"""
RateLimiter — simple brute-force lockout tracker.

Mirrors src/utils/RateLimiter.hpp/cpp: after MAX_ATTEMPTS consecutive
failures for a given key (e.g. a username), that key is banned for
BAN_MINUTES. A success resets the counter.

No lock is needed here (unlike the C++ version's std::mutex): the server
runs a single-threaded asyncio event loop, and none of these methods
awaits mid-operation, so each call runs atomically with respect to every
other coroutine.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


MAX_ATTEMPTS = 5
BAN_MINUTES = 5


@dataclass
class _Entry:
    failed_attempts: int = 0
    ban_until: float = 0.0
    banned: bool = False


class RateLimiter:
    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}

    def is_allowed(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return True
        if entry.banned:
            if time.monotonic() >= entry.ban_until:
                entry.banned = False
                entry.failed_attempts = 0
                return True
            return False
        return True

    def record_failure(self, key: str) -> None:
        entry = self._entries.setdefault(key, _Entry())
        entry.failed_attempts += 1
        if entry.failed_attempts >= MAX_ATTEMPTS:
            entry.banned = True
            entry.ban_until = time.monotonic() + BAN_MINUTES * 60

    def record_success(self, key: str) -> None:
        entry = self._entries.get(key)
        if entry is not None:
            entry.failed_attempts = 0
            entry.banned = False

    def cleanup(self) -> None:
        now = time.monotonic()
        stale = [
            k
            for k, e in self._entries.items()
            if (not e.banned and e.failed_attempts == 0)
            or (e.banned and now >= e.ban_until)
        ]
        for k in stale:
            del self._entries[k]

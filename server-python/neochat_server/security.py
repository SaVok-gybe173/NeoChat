"""
security — password hashing and token generation.

The original server hand-rolled SHA-256 (src/crypto/Sha256Hasher.cpp).
Python's stdlib `hashlib` already provides a verified SHA-256
implementation, so we use that directly instead of reimplementing it —
the observable behaviour (hash(password + salt) -> hex digest) is
identical.

NOTE (carried over from the original): salted SHA-256 is what the
original server used for password storage. It is fast to brute-force
compared to a dedicated password hash (bcrypt/scrypt/argon2). If you
want to harden this, swap `hash_password` for `hashlib.scrypt` or the
`bcrypt` package — the rest of the codebase only depends on the
function signature below.
"""
from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str, salt: str) -> str:
    """Equivalent to the original Sha256Hasher::hash(password + salt)."""
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def generate_token() -> str:
    """
    32 hex chars (128 bits) of cryptographically secure randomness.

    The original server concatenated four 32-bit std::random_device draws
    into an 8-hex-digit-each string. secrets.token_hex(16) produces the
    same shape (32 hex chars) from a CSPRNG, which is a strictly stronger
    source of randomness.
    """
    return secrets.token_hex(16)

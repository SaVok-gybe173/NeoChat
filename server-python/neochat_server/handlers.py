"""
Handlers — business logic for every `action` the router dispatches.

Mirrors src/routing/Handlers.hpp/cpp: registration/login, sending and
fetching messages, listing users, logout, and public-key upload/lookup
(for E2E encryption bootstrapping). Validation limits (lengths etc.) and
error `reason` codes match the original 1:1 so existing clients keep
working unmodified.
"""
from __future__ import annotations

import time
from typing import Optional

from .database import JsonDatabase, User, Message
from .logger import setup_logger
from .rate_limiter import RateLimiter
from .security import generate_token, hash_password
from .session import Session

logger = setup_logger()


def _error(reason: str, message: str) -> dict:
    return {"status": "error", "reason": reason, "message": message}


def _validate_username(username: str) -> Optional[dict]:
    if not username or len(username) > 32:
        return _error("invalid_username", "Username must be 1-32 characters")
    return None


def _validate_content(content: str) -> Optional[dict]:
    if not content or len(content) > 4096:
        return _error("invalid_content", "Content must be 1-4096 characters")
    return None


def _validate_public_key(key: str) -> Optional[dict]:
    if not key or len(key) > 256:
        return _error("invalid_key", "Public key too large (max 256 chars)")
    return None


def _validate_email(email: str) -> Optional[dict]:
    # Basic format check without external libraries, ported from the
    # original C++ (single '@', non-empty domain containing a '.', not
    # leading/trailing with '.').
    if not email or len(email) > 254:
        return _error("invalid_email", "Email must be 1-254 characters")
    at = email.find("@")
    if at <= 0 or at == len(email) - 1:
        return _error("invalid_email", "Invalid email format")
    if email.find("@", at + 1) != -1:
        return _error("invalid_email", "Invalid email format")
    domain = email[at + 1 :]
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return _error("invalid_email", "Invalid email format")
    return None


class Handlers:
    def __init__(self, db: JsonDatabase) -> None:
        self.db = db
        self.auth_tokens: dict[str, str] = {}  # token -> username
        self.active_users: dict[str, Session] = {}  # username -> session
        self.rate_limiter = RateLimiter()

    # -- session bookkeeping ---------------------------------------------------

    def user_connected(self, username: str, session: Session) -> None:
        self.active_users[username] = session

    def user_disconnected(self, username: str) -> None:
        self.active_users.pop(username, None)
        logger.info(f"User disconnected: {username}")

    def _resolve_token(self, token: str) -> Optional[str]:
        return self.auth_tokens.get(token)

    # -- actions ---------------------------------------------------

    async def handle_register(self, req: dict) -> dict:
        if not all(k in req for k in ("username", "password", "email")):
            return _error("missing_fields", "Missing username, password or email")

        username = str(req["username"])
        password = str(req["password"])
        email = str(req["email"])

        if err := _validate_username(username):
            return err
        if err := _validate_email(email):
            return err
        if not self.rate_limiter.is_allowed(username):
            logger.warning(f"Rate limit hit for register: {username}")
            return _error("rate_limited", "Too many attempts. Try again in 5 minutes.")
        if not password or len(password) > 128:
            return _error("invalid_password", "Password must be 1-128 characters")

        if self.db.get_user_by_email(email):
            logger.warning(f"Registration failed (email exists): {email}")
            return _error("email_taken", "Email already registered")

        salt = generate_token()
        user = User(
            username=username,
            password_hash=hash_password(password, salt),
            salt=salt,
            email=email,
        )
        if self.db.add_user(user):
            logger.info(f"User registered: {username}")
            return {"status": "ok", "message": "User registered"}

        logger.warning(f"Registration failed (exists): {username}")
        return _error("username_taken", "Username already exists")

    async def handle_login(self, req: dict, session: Optional[Session]) -> dict:
        if not all(k in req for k in ("username", "password")):
            return _error("missing_fields", "Missing username or password")

        username = str(req["username"])
        password = str(req["password"])

        if err := _validate_username(username):
            return err
        if not self.rate_limiter.is_allowed(username):
            logger.warning(f"Rate limit hit for login: {username}")
            return _error("rate_limited", "Too many attempts. Try again in 5 minutes.")

        user = self.db.get_user(username)
        if not user:
            self.rate_limiter.record_failure(username)
            return _error("invalid_credentials", "Invalid credentials")

        if hash_password(password, user.salt) == user.password_hash:
            self.rate_limiter.record_success(username)
            token = generate_token()
            self.auth_tokens[token] = username
            if session is not None:
                session.set_username(username)
                self.user_connected(username, session)
            logger.info(f"User logged in: {username}")
            return {"status": "ok", "token": token, "username": username}

        self.rate_limiter.record_failure(username)
        logger.warning(f"Failed login for user: {username}")
        return _error("invalid_credentials", "Invalid credentials")

    async def handle_send_message(self, req: dict) -> dict:
        if not all(k in req for k in ("token", "to", "content")):
            return _error("missing_fields", "Missing fields")

        token = str(req["token"])
        to = str(req["to"])
        content = str(req["content"])

        from_user = self._resolve_token(token)
        if from_user is None:
            return _error("invalid_token", "Invalid token")

        if not self.rate_limiter.is_allowed(from_user):  # rate limit by username, not token
            return _error("rate_limited", "Rate limited")
        if err := _validate_username(to):
            return err
        if err := _validate_content(content):
            return err
        if not self.db.get_user(to):
            return _error("user_not_found", "Recipient not found")

        msg = Message(
            id=0,  # assigned by db.add_message
            from_=from_user,
            to=to,
            content=content,
            timestamp=int(time.time()),
            encrypted=bool(req.get("encrypted", False)),
            ephemeral_key=str(req.get("ephemeral_key", "")),
            nonce=str(req.get("nonce", "")),
            salt=str(req.get("salt", "")),
        )

        target_session = self.active_users.get(to)
        delivered_online = False
        if target_session is not None:
            push = {
                "type": "push",
                "action": "new_message",
                "from": from_user,
                "content": content,
                "timestamp": msg.timestamp,
                "encrypted": msg.encrypted,
                "ephemeral_key": msg.ephemeral_key,
                "nonce": msg.nonce,
                "salt": msg.salt,
            }
            delivered_online = await target_session.deliver(push)

        self.db.add_message(msg)
        logger.info(
            f"Message from {from_user} to {to} (online={'yes' if delivered_online else 'no'})"
        )
        return {"status": "ok", "message": "Message sent", "delivered_online": delivered_online}

    async def handle_get_messages(self, req: dict) -> dict:
        if not all(k in req for k in ("token", "peer")):
            return _error("missing_fields", "Missing fields")

        token = str(req["token"])
        peer = str(req["peer"])

        username = self._resolve_token(token)
        if username is None:
            return _error("invalid_token", "Invalid token")
        if not self.rate_limiter.is_allowed(username):
            return _error("rate_limited", "Rate limited")
        if err := _validate_username(peer):
            return err

        limit = int(req.get("limit", 100))
        offset = int(req.get("offset", 0))
        if limit < 0:
            limit = 0
        if offset < 0:
            offset = 0

        messages = self.db.get_messages(username, peer, limit, offset)
        arr = [
            {
                "id": m.get("id"),
                "from": m.get("from"),
                "to": m.get("to"),
                "content": m.get("content"),
                "timestamp": m.get("timestamp"),
                "encrypted": m.get("encrypted", False),
                "ephemeral_key": m.get("ephemeral_key", ""),
                "nonce": m.get("nonce", ""),
                "salt": m.get("salt", ""),
            }
            for m in messages
        ]
        return {"status": "ok", "messages": arr}

    async def handle_get_users(self, req: dict) -> dict:
        if "token" not in req:
            return _error("missing_fields", "Missing token")

        token = str(req["token"])
        username = self._resolve_token(token)
        if username is None:
            return _error("invalid_token", "Invalid token")
        if not self.rate_limiter.is_allowed(username):
            return _error("rate_limited", "Rate limited")

        return {"status": "ok", "users": self.db.get_all_users()}

    async def handle_logout(self, req: dict, session: Optional[Session]) -> dict:
        if "token" not in req:
            return _error("missing_fields", "Missing token")

        token = str(req["token"])
        username = self.auth_tokens.pop(token, None)

        if username:
            self.user_disconnected(username)

        logger.info(f"User logged out: {username or 'unknown'}")
        return {"status": "ok", "message": "Logged out"}

    async def handle_upload_key(self, req: dict) -> dict:
        if not all(k in req for k in ("token", "key_data")):
            return _error("missing_fields", "Missing token or key_data")

        token = str(req["token"])
        key_data = str(req["key_data"])

        if err := _validate_public_key(key_data):
            return err

        username = self._resolve_token(token)
        if username is None:
            return _error("invalid_token", "Invalid token")
        if not self.rate_limiter.is_allowed(username):
            return _error("rate_limited", "Rate limited")

        if self.db.update_user_public_key(username, key_data):
            logger.info(f"Public key uploaded for: {username}")
            return {"status": "ok", "message": "Public key uploaded"}

        return _error("user_not_found", "User not found")

    async def handle_get_key(self, req: dict) -> dict:
        # Require a token so usernames can't be enumerated by guessing.
        if "token" not in req:
            return _error("missing_fields", "Missing token")

        token = str(req["token"])
        requester = self._resolve_token(token)
        if requester is None:
            return _error("invalid_token", "Invalid token")
        if not self.rate_limiter.is_allowed(requester):
            return _error("rate_limited", "Rate limited")

        if "username" not in req:
            return _error("missing_fields", "Missing username")

        username = str(req["username"])
        if err := _validate_username(username):
            return err

        key = self.db.get_user_public_key(username)
        if key is not None:
            return {"status": "ok", "key_data": key}

        return _error("key_not_found", "Public key not found")

"""
Router — dispatches a parsed request to the right Handlers method.

Mirrors src/routing/Router.hpp/cpp: looks at request["action"], calls the
matching handler, and echoes back request["req_id"] if the client sent
one (so clients can match async responses to requests).
"""
from __future__ import annotations

from typing import Optional

from .handlers import Handlers
from .session import Session

_NO_SESSION_ACTIONS = {"register", "send_message", "get_messages", "get_users", "upload_key", "get_key"}


class Router:
    def __init__(self, handlers: Handlers) -> None:
        self.handlers = handlers

    async def route(self, request: dict, session: Optional[Session]) -> dict:
        if "action" not in request:
            res = {"status": "error", "message": "Missing action"}
            if "req_id" in request:
                res["req_id"] = request["req_id"]
            return res

        action = str(request["action"])
        h = self.handlers

        if action == "register":
            res = await h.handle_register(request)
        elif action == "login":
            res = await h.handle_login(request, session)
        elif action == "send_message":
            res = await h.handle_send_message(request)
        elif action == "get_messages":
            res = await h.handle_get_messages(request)
        elif action == "get_users":
            res = await h.handle_get_users(request)
        elif action == "logout":
            res = await h.handle_logout(request, session)
        elif action == "upload_key":
            res = await h.handle_upload_key(request)
        elif action == "get_key":
            res = await h.handle_get_key(request)
        else:
            res = {"status": "error", "message": f"Unknown action: {action}"}

        if "req_id" in request:
            res["req_id"] = request["req_id"]
        return res

    def on_user_disconnected(self, username: str) -> None:
        self.handlers.user_disconnected(username)

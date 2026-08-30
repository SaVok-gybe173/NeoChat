"""
Config — simple INI file loader.

Mirrors the original src/config/Config.hpp / Config.cpp: sections in
[brackets], key=value pairs, ';' and '#' comment lines, ints parsed with
a safe fallback to the default value.
"""
from __future__ import annotations

import configparser
from pathlib import Path
from typing import Dict


class Config:
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, str]] = {}

    def load(self, filename: str) -> bool:
        path = Path(filename)
        if not path.is_file():
            return False

        parser = configparser.ConfigParser()
        # Preserve key case exactly like the original (which does not
        # lowercase keys), and allow ';' as an additional comment prefix.
        parser.optionxform = str  # type: ignore[assignment]
        try:
            with path.open("r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return False

        # configparser only treats '#' as a comment prefix by default when
        # inline_comment_prefixes isn't set on whole-line comments starting
        # with ';' or '#' — both are supported out of the box for full-line
        # comments, so we can read directly.
        try:
            parser.read_string(text)
        except configparser.Error:
            return False

        self._data = {
            section: dict(parser.items(section)) for section in parser.sections()
        }
        return True

    def get_string(self, section: str, key: str, default: str = "") -> str:
        return self._data.get(section, {}).get(key, default)

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        raw = self.get_string(section, key, "")
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

"""
Logger — thin wrapper around the stdlib `logging` module.

Mirrors src/utils/Logger.hpp/cpp: writes timestamped, leveled lines to both
a log file and the console.
"""
from __future__ import annotations

import logging
import sys


def setup_logger(filename: str = "server.log") -> logging.Logger:
    logger = logging.getLogger("neochat")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    try:
        file_handler = logging.FileHandler(filename, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Warning: File logger failed, logging to console only")

    return logger

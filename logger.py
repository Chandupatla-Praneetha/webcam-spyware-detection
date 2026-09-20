"""
Common logger. Everyone imports this instead of writing their own.
Writes to logs/app.log AND records structured rows into the activity_logs /
security_logs tables so the dashboard can query them.
"""
import logging
import os

import config

_LOG_FILE = os.path.join(config.LOGS_FOLDER, "app.log")

_logger = logging.getLogger("webcam_security")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    _handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    _logger.addHandler(_handler)


def log_activity(username: str, action: str) -> None:
    """Record a normal activity event (login, logout, camera toggle, etc.)."""
    _logger.info(f"ACTIVITY | user={username} | action={action}")
    # Local import avoids a circular import (database imports nothing from here).
    from database.logs import insert_activity_log
    insert_activity_log(username, action)


def log_security_event(message: str, level: str = "warning") -> None:
    """Record a security-relevant event (failed login, face mismatch, etc.)."""
    getattr(_logger, level.lower(), _logger.warning)(f"SECURITY | {message}")

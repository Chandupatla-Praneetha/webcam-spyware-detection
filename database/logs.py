"""
Read/write helpers for activity_logs, security_logs, intruder_logs.
Used by logger.py (writes) and gui/dashboard.py (reads).
"""
from typing import List, Dict, Any

from database.database import get_connection


def insert_activity_log(username: str, action: str) -> None:
    conn = get_connection()
    conn.execute("INSERT INTO activity_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()


def insert_security_log(message: str, level: str = "warning") -> None:
    conn = get_connection()
    conn.execute("INSERT INTO security_logs (message, level) VALUES (?, ?)", (message, level))
    conn.commit()
    conn.close()


def log_intruder(image_path: str, reason: str, username: str = "") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO intruder_logs (image_path, reason, username) VALUES (?, ?, ?)",
        (image_path, reason, username),
    )
    conn.commit()
    conn.close()


def get_recent_activity(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_intruder_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM intruder_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_failed_login_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT SUM(failed_attempts) AS total FROM users").fetchone()
    conn.close()
    return row["total"] or 0


def get_intruder_alert_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS total FROM intruder_logs").fetchone()
    conn.close()
    return row["total"] or 0

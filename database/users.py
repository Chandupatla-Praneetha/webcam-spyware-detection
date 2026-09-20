"""
All user-table CRUD. Used by auth/* and gui/users_window.py.
"""
from typing import Optional, List, Dict, Any

from database.database import get_connection
import config


def create_user(username: str, password_hash: str, email: str, role: str = "user") -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, role),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_users() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT id, username, email, role, face_registered, failed_attempts, locked FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(username: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def update_password(username: str, new_password_hash: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_password_hash, username))
    conn.commit()
    conn.close()


def set_face_registered(username: str, registered: bool = True) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET face_registered = ? WHERE username = ?", (1 if registered else 0, username))
    conn.commit()
    conn.close()


def increment_failed_attempts(username: str) -> int:
    conn = get_connection()
    conn.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username = ?", (username,))
    conn.commit()
    row = conn.execute("SELECT failed_attempts FROM users WHERE username = ?", (username,)).fetchone()
    count = row["failed_attempts"] if row else 0
    if row and count >= config.MAX_FAILED_ATTEMPTS_BEFORE_LOCK:
        conn.execute("UPDATE users SET locked = 1 WHERE username = ?", (username,))
        conn.commit()
    conn.close()
    return count


def reset_failed_attempts(username: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET failed_attempts = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def is_locked(username: str) -> bool:
    user = get_user_by_username(username)
    return bool(user and user["locked"])


def unlock_user(username: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET locked = 0, failed_attempts = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

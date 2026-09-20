"""
CRUD for the schedules table (Admin -> "Create Schedules").

Each schedule row is a time RANGE, e.g. "5:00 PM to 6:00 PM": the camera is
enabled at start_time and disabled at end_time -- one row = one on/off pair,
instead of two separate raw actions.
"""
from typing import List, Dict, Any

from database.database import get_connection


def add_schedule(start_time: str, end_time: str, created_by: str) -> None:
    """start_time / end_time are 'HH:MM' 24-hour strings, e.g. '17:00', '18:00'."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO schedules (start_time, end_time, created_by) VALUES (?, ?, ?)",
        (start_time, end_time, created_by),
    )
    conn.commit()
    conn.close()


def list_schedules() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM schedules WHERE active = 1 ORDER BY start_time").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_schedule(schedule_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()

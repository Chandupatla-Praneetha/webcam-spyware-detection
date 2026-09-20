"""
Owns the SQLite connection and the schema for the whole app.
Every table described in the spec lives here: users, activity_logs,
security_logs, intruder_logs, schedules.
"""
import sqlite3

import config


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',      -- 'admin' or 'user'
            face_registered INTEGER NOT NULL DEFAULT 0,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            level TEXT NOT NULL DEFAULT 'warning',
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS intruder_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            reason TEXT NOT NULL,
            username TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,    -- 'HH:MM' 24h -- camera is ENABLED at this time
            end_time TEXT NOT NULL,      -- 'HH:MM' 24h -- camera is DISABLED at this time
            created_by TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

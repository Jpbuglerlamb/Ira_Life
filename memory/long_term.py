# memory/long_term.py

import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "ai_memory.db"


# ============================================================
# Database Initialization
# ============================================================

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def migrate_reminders_table():
    """Ensure all required columns exist in reminders table."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(reminders)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    # Required columns
    required_columns = {
        "status": "TEXT DEFAULT 'pending'",
        "created_at": "TEXT"
    }

    for col_name, col_def in required_columns.items():
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE reminders ADD COLUMN {col_name} {col_def}")
            print(f"[Migration] Added '{col_name}' column to reminders table.")

    conn.commit()
    conn.close()


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # -----------------------------
    # Users table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
    """)

    # -----------------------------
    # Memory table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mode TEXT,
        key TEXT,
        value TEXT,
        timestamp TEXT,
        UNIQUE(user_id, mode, key),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # -----------------------------
    # Reminders table (minimal schema)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT NOT NULL,
        time TEXT,
        keep INTEGER DEFAULT 0,
        fired_at TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    # -----------------------------
    # Run migrations for existing DB
    # -----------------------------
    migrate_reminders_table()

# ============================================================
# User Service
# ============================================================

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def create_user(username: str, password: str):
        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, UserService.hash_password(password))
            )
            conn.commit()
            return {"id": cursor.lastrowid, "username": username}
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    @staticmethod
    def verify_user(username: str, password: str) -> bool:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM users WHERE username=?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()
        return bool(row and row[0] == UserService.hash_password(password))

    @staticmethod
    def get_user(username: str):
        """Return user dict or None"""
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username=?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "username": row[1]}
        return None

    @staticmethod
    def get_user_id(username: str):
        user = UserService.get_user(username)
        return user["id"] if user else None


# ============================================================
# Memory Service
# ============================================================

class MemoryService:
    @staticmethod
    def remember(user_id: int, mode: str, key: str, value: str):
        """Store or update a memory item for a user in a given mode."""
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memory (user_id, mode, key, value, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, mode, key)
            DO UPDATE SET value=excluded.value, timestamp=excluded.timestamp
        """, (user_id, mode, key, value, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

    @staticmethod
    def recall(user_id: int, mode: str, key: str):
        """Retrieve a single memory item."""
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM memory WHERE user_id=? AND mode=? AND key=?",
            (user_id, mode, key)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def list_memory(user_id: int, mode: str):
        """Return all memory items for a user in a specific mode."""
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, value, timestamp FROM memory WHERE user_id=? AND mode=? ORDER BY timestamp",
            (user_id, mode)
        )
        rows = cursor.fetchall()
        conn.close()
        # Return as a list of dicts
        return [{"key": k, "value": v, "timestamp": t} for k, v, t in rows]


# ============================================================
# Reminder Service (UPGRADED)
# ============================================================

class ReminderService:
    @staticmethod
    def add_reminder(user_id, text, time=None, keep=False):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (user_id, text, time, keep, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            text,
            time,
            int(keep),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def list_reminders(user_id, include_fired=False):
        conn = get_conn()
        cursor = conn.cursor()

        query = """
            SELECT id, text, time, status, COALESCE(time, created_at) as sort_time
            FROM reminders
            WHERE user_id=?
        """

        if not include_fired:
            query += " AND status='pending'"

        query += " ORDER BY sort_time"

        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def mark_fired(reminder_id):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders
            SET status='fired', fired_at=?
            WHERE id=?
        """, (datetime.utcnow().isoformat(), reminder_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_reminder(reminder_id):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
        conn.commit()
        conn.close()
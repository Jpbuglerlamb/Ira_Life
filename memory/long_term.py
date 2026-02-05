# memory/long_term.py
import sqlite3
from datetime import datetime
from auth.tokens import hash_password, verify_password

DB_FILE = "ai_memory.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
    """)

    cur.execute("""
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

    cur.execute("""
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

    # Create vector tables too
    from memory.vector_store import init_vector_tables
    init_vector_tables()

class UserService:
    @staticmethod
    def create_user(username: str, password: str):
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password))
            )
            conn.commit()
            return {"id": cur.lastrowid, "username": username}
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    @staticmethod
    def verify_user(username: str, password: str) -> bool:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        return bool(row and verify_password(password, row[0]))

    @staticmethod
    def get_user(username: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        return {"id": row[0], "username": row[1]} if row else None

    @staticmethod
    def get_user_id(username: str):
        user = UserService.get_user(username)
        return user["id"] if user else None

class MemoryService:
    @staticmethod
    def remember(user_id: int, mode: str, key: str, value: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO memory (user_id, mode, key, value, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, mode, key)
            DO UPDATE SET value=excluded.value, timestamp=excluded.timestamp
        """, (user_id, mode, key, value, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

    @staticmethod
    def recall(user_id: int, mode: str, key: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE user_id=? AND mode=? AND key=?", (user_id, mode, key))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def list_memory(user_id: int, mode: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT key, value, timestamp FROM memory WHERE user_id=? AND mode=? ORDER BY timestamp", (user_id, mode))
        rows = cur.fetchall()
        conn.close()
        return [{"key": k, "value": v, "timestamp": t} for k, v, t in rows]

class ReminderService:
    @staticmethod
    def add_reminder(user_id, text, time=None, keep=False):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reminders (user_id, text, time, keep, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, text, time, int(keep), datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

    @staticmethod
    def list_reminders(user_id, include_fired=False):
        conn = get_conn()
        cur = conn.cursor()
        q = """
            SELECT id, text, time, status, COALESCE(time, created_at) as sort_time
            FROM reminders
            WHERE user_id=?
        """
        if not include_fired:
            q += " AND status='pending'"
        q += " ORDER BY sort_time"
        cur.execute(q, (user_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def delete_reminder(reminder_id: int):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
        conn.commit()
        conn.close()

# memory/vector_store.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "ai_memory.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_vector_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memory_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        embedding TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()

def add_message(user_id: int, role: str, content: str, embedding: Optional[List[float]] = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memory_messages (user_id, role, content, created_at, embedding) VALUES (?, ?, ?, ?, ?)",
        (user_id, role, content, datetime.utcnow().isoformat(), json.dumps(embedding) if embedding else None),
    )
    conn.commit()
    conn.close()

def fetch_messages_with_embeddings(user_id: int, limit: int = 500) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, role, content, created_at, embedding
        FROM memory_messages
        WHERE user_id=?
        AND embedding IS NOT NULL
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()

    out = []
    for _id, role, content, created_at, emb in rows:
        try:
            vec = json.loads(emb) if emb else []
        except Exception:
            vec = []
        out.append({"id": _id, "role": role, "content": content, "created_at": created_at, "embedding": vec})
    return out

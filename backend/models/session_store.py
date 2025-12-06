# backend/models/session_store.py
import sqlite3
from contextlib import closing

DB_PATH = "sessions.db"

def init_db():
    """Initialize the SQLite database and sessions table."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT UNIQUE,
                token_json TEXT
            )
        """)
        conn.commit()

def store_token(email: str, token_json: str):
    """Store or update a user's token in the database."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO sessions (user_email, token_json)
            VALUES (?, ?)
        """, (email, token_json))
        conn.commit()

def get_token(email: str):
    """Fetch token JSON for a given user email."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT token_json FROM sessions WHERE user_email = ?", (email,))
        row = c.fetchone()
        return row[0] if row else None

def delete_token(email: str):
    """Delete token for a given user email."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE user_email = ?", (email,))
        conn.commit()

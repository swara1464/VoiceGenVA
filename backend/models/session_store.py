# backend/models/session_store.py
import json
import sqlite3
import os
from threading import Lock

# SQLite3 database path
DB_PATH = os.path.join(os.path.dirname(__file__), "tokens.db")

# Thread-safe lock for database operations
_db_lock = Lock()

def init_db():
    """Initialize SQLite3 database for token storage."""
    with _db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                email TEXT PRIMARY KEY,
                token_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print(f"SQLite3 token storage initialized at {DB_PATH}")

def store_token(email: str, token_json: str):
    """Store or update a user's token in SQLite3."""
    try:
        # Validate JSON
        json.loads(token_json)

        with _db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tokens (email, token_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (email, token_json))
            conn.commit()
            conn.close()
            print(f"Token stored successfully for {email}")
    except Exception as e:
        print(f"Error storing token for {email}: {e}")

def get_token(email: str):
    """Fetch token JSON string for a given user email from SQLite3."""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT token_json FROM tokens WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if row:
                print(f"Token retrieved successfully for {email}")
                return row[0]
            print(f"No token found for {email}")
            return None
    except Exception as e:
        print(f"Error retrieving token for {email}: {e}")
        return None

def delete_token(email: str):
    """Delete token for a given user email from SQLite3."""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tokens WHERE email = ?", (email,))
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if deleted:
                print(f"Token deleted successfully for {email}")
            else:
                print(f"No token found to delete for {email}")
    except Exception as e:
        print(f"Error deleting token for {email}: {e}")

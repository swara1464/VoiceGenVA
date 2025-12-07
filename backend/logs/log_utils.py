# backend/logs/log_utils.py
import datetime
import json
import sqlite3
import os
from threading import Lock

# SQLite3 database path
DB_PATH = os.path.join(os.path.dirname(__file__), "logs.db")

# Thread-safe lock for database operations
_db_lock = Lock()

def init_log_db():
    """Initializes SQLite3 database for logs storage."""
    with _db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_email TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print(f"SQLite3 logs storage initialized at {DB_PATH}")

def log_execution(user_email: str, action: str, status: str, details: dict):
    """
    Records an agent execution event into SQLite3.

    :param user_email: The email of the user who triggered the action.
    :param action: The high-level action being performed (e.g., GMAIL_SEND).
    :param status: Status of the action ('ATTEMPTING', 'SUCCESS', 'FAILED').
    :param details: Dictionary containing execution results or parameters.
    """
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs (timestamp, user_email, action, status, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.datetime.now().isoformat(),
                user_email,
                action,
                status,
                json.dumps(details)
            ))
            conn.commit()
            conn.close()
            print(f"Log recorded: {action} - {status}")
    except Exception as e:
        print(f"Error writing log: {e}")

def get_logs(user_email: str):
    """
    Retrieves all execution logs for a specific user, ordered by newest first.

    :param user_email: The email of the user to fetch logs for.
    :return: A list of log dictionaries with id, timestamp, user_email, action, status, details.
    """
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, user_email, action, status, details
                FROM logs
                WHERE user_email = ?
                ORDER BY timestamp DESC
            """, (user_email,))
            rows = cursor.fetchall()
            conn.close()

            logs = []
            for row in rows:
                logs.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "user_email": row[2],
                    "action": row[3],
                    "status": row[4],
                    "details": json.loads(row[5]) if row[5] else {}
                })
            return logs
    except Exception as e:
        print(f"Error retrieving logs for {user_email}: {e}")
        return []

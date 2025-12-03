# backend/logs/log_utils.py
import sqlite3
from datetime import datetime
import json

LOG_DB = "executions.db"

def init_log_db():
    """Initializes the SQLite database for execution logs."""
    conn = sqlite3.connect(LOG_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_email TEXT,
            action TEXT,
            status TEXT,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_execution(user_email: str, action: str, status: str, details: dict):
    """Inserts a new log record into the database."""
    init_log_db()
    conn = sqlite3.connect(LOG_DB)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    c.execute("""
        INSERT INTO logs (timestamp, user_email, action, status, details)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, user_email, action, status, json.dumps(details)))
    
    conn.commit()
    conn.close()

def get_logs(user_email: str):
    """Retrieves all logs for a specific user."""
    init_log_db()
    conn = sqlite3.connect(LOG_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE user_email = ? ORDER BY timestamp DESC", (user_email,))
    logs = c.fetchall()
    conn.close()
    return logs
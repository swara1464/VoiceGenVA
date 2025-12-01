import sqlite3

def init_db():
    conn = sqlite3.connect("sessions.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT UNIQUE,
            token_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_token(email, token_json):
    conn = sqlite3.connect("sessions.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO sessions (user_email, token_json)
        VALUES (?, ?)
    """, (email, token_json))
    conn.commit()
    conn.close()

# backend/logs/log_utils.py
import sqlite3
import datetime
import json

# Database file name is specified in app.py
DB_NAME = "executions.db" 

def init_log_db():
    """Initializes the SQLite database table for execution logs if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
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
        print(f"Log database '{DB_NAME}' initialized successfully.")
    except Exception as e:
        print(f"Error initializing log database: {e}")

def log_execution(user_email: str, action: str, status: str, details: dict):
    """
    Records an agent execution event into the logs database.

    :param user_email: The email of the user who triggered the action.
    :param action: The high-level action being performed (e.g., GMAIL_SEND).
    :param status: Status of the action ('ATTEMPTING', 'SUCCESS', 'FAILED').
    :param details: Dictionary containing execution results or parameters.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Convert the dictionary details to a JSON string for storage
        details_json = json.dumps(details)
        
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute("""
            INSERT INTO logs (timestamp, user_email, action, status, details)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, user_email, action, status, details_json))
        
        conn.commit()
        conn.close()
        # print(f"Log recorded: {action} - {status}")
    except Exception as e:
        print(f"Error writing log: {e}")

def get_logs(user_email: str):
    """
    Retrieves all execution logs for a specific user, ordered by newest first.

    :param user_email: The email of the user to fetch logs for.
    :return: A list of log tuples.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Fetch logs for the specific user, ordered by timestamp descending
        c.execute("""
            SELECT id, timestamp, user_email, action, status, details
            FROM logs
            WHERE user_email = ?
            ORDER BY timestamp DESC
        """, (user_email,))
        
        logs = c.fetchall()
        conn.close()
        return logs
    except Exception as e:
        print(f"Error retrieving logs for {user_email}: {e}")
        return []

if __name__ == '__main__':
    # Simple test case when running this module directly
    init_log_db()
    test_email = "test@agent.com"
    log_execution(test_email, "TEST_ACTION_1", "ATTEMPTING", {"param": "value"})
    log_execution(test_email, "TEST_ACTION_2", "SUCCESS", {"result": "ok"})
    print(get_logs(test_email))
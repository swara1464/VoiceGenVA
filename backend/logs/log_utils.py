# backend/logs/log_utils.py
import datetime
import json

# In-memory logs storage
# List of log entries
_logs = []

def init_log_db():
    """Initializes in-memory logs storage (no-op, just for API compatibility)."""
    print("In-memory logs storage initialized.")

def log_execution(user_email: str, action: str, status: str, details: dict):
    """
    Records an agent execution event into memory.

    :param user_email: The email of the user who triggered the action.
    :param action: The high-level action being performed (e.g., GMAIL_SEND).
    :param status: Status of the action ('ATTEMPTING', 'SUCCESS', 'FAILED').
    :param details: Dictionary containing execution results or parameters.
    """
    try:
        log_entry = {
            "id": len(_logs) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_email": user_email,
            "action": action,
            "status": status,
            "details": details
        }
        _logs.append(log_entry)
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
        user_logs = [log for log in _logs if log["user_email"] == user_email]
        # Return sorted by timestamp descending (newest first)
        return sorted(user_logs, key=lambda x: x["timestamp"], reverse=True)
    except Exception as e:
        print(f"Error retrieving logs for {user_email}: {e}")
        return []
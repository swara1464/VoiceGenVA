# backend/logs/log_utils.py
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = None

def init_log_db():
    """Initializes Supabase connection for logs."""
    global supabase
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Warning: Supabase credentials not configured. Logs will not be persisted.")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connection initialized for logs.")
    except Exception as e:
        print(f"Error initializing Supabase: {e}")

def log_execution(user_email: str, action: str, status: str, details: dict):
    """
    Records an agent execution event into the Supabase logs table.

    :param user_email: The email of the user who triggered the action.
    :param action: The high-level action being performed (e.g., GMAIL_SEND).
    :param status: Status of the action ('ATTEMPTING', 'SUCCESS', 'FAILED').
    :param details: Dictionary containing execution results or parameters.
    """
    if not supabase:
        return

    try:
        supabase.table("logs").insert({
            "user_email": user_email,
            "action": action,
            "status": status,
            "details": details
        }).execute()
    except Exception as e:
        print(f"Error writing log: {e}")

def get_logs(user_email: str):
    """
    Retrieves all execution logs for a specific user, ordered by newest first.

    :param user_email: The email of the user to fetch logs for.
    :return: A list of log dictionaries with id, timestamp, user_email, action, status, details.
    """
    if not supabase:
        return []

    try:
        response = supabase.table("logs").select(
            "id, timestamp, user_email, action, status, details"
        ).eq("user_email", user_email).order("timestamp", desc=True).execute()

        return response.data if response.data else []
    except Exception as e:
        print(f"Error retrieving logs for {user_email}: {e}")
        return []
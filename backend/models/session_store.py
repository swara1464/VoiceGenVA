# backend/models/session_store.py
import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = None

def init_db():
    """Initialize the Supabase connection for OAuth token storage."""
    global supabase
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Warning: Supabase credentials not configured. Token storage will not work.")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connection initialized for OAuth tokens.")
    except Exception as e:
        print(f"Error initializing Supabase for tokens: {e}")

def store_token(email: str, token_json: str):
    """Store or update a user's token in Supabase."""
    if not supabase:
        print("Error: Supabase not initialized. Cannot store token.")
        return

    try:
        # Parse to validate JSON
        token_data = json.loads(token_json)

        # Upsert: insert if new, update if exists (based on user_email UNIQUE constraint)
        supabase.table("oauth_tokens").upsert({
            "user_email": email,
            "token_json": token_data  # Store as JSONB
        }, on_conflict="user_email").execute()

        print(f"Token stored successfully for {email}")
    except Exception as e:
        print(f"Error storing token for {email}: {e}")

def get_token(email: str):
    """Fetch token JSON string for a given user email."""
    if not supabase:
        print("Error: Supabase not initialized. Cannot retrieve token.")
        return None

    try:
        response = supabase.table("oauth_tokens").select("token_json").eq("user_email", email).maybeSingle().execute()

        if response.data:
            # Return as JSON string (to match original SQLite behavior)
            return json.dumps(response.data["token_json"])
        return None
    except Exception as e:
        print(f"Error retrieving token for {email}: {e}")
        return None

def delete_token(email: str):
    """Delete token for a given user email."""
    if not supabase:
        print("Error: Supabase not initialized. Cannot delete token.")
        return

    try:
        supabase.table("oauth_tokens").delete().eq("user_email", email).execute()
        print(f"Token deleted successfully for {email}")
    except Exception as e:
        print(f"Error deleting token for {email}: {e}")

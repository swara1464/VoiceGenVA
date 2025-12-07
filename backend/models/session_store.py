# backend/models/session_store.py
import json

# In-memory token storage
# Maps user email to their OAuth token JSON string
_token_store = {}

def init_db():
    """Initialize in-memory token storage (no-op, just for API compatibility)."""
    print("In-memory token storage initialized.")

def store_token(email: str, token_json: str):
    """Store or update a user's token in memory."""
    try:
        # Validate JSON
        json.loads(token_json)
        _token_store[email] = token_json
        print(f"Token stored successfully for {email}")
    except Exception as e:
        print(f"Error storing token for {email}: {e}")

def get_token(email: str):
    """Fetch token JSON string for a given user email."""
    try:
        token = _token_store.get(email)
        if token:
            print(f"Token retrieved successfully for {email}")
            return token
        print(f"No token found for {email}")
        return None
    except Exception as e:
        print(f"Error retrieving token for {email}: {e}")
        return None

def delete_token(email: str):
    """Delete token for a given user email."""
    try:
        if email in _token_store:
            del _token_store[email]
            print(f"Token deleted successfully for {email}")
        else:
            print(f"No token found to delete for {email}")
    except Exception as e:
        print(f"Error deleting token for {email}: {e}")

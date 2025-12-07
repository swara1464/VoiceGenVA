# backend/models/session_store.py
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("❌ Supabase env variables not loaded yet")


def init_db():
    """No-op for backward compatibility. Supabase table already exists."""
    print("Using Supabase for token storage (oauth_tokens table)")

def store_token(email: str, token_json: str):
    """Store or update a user's token in Supabase."""
    try:
        # Validate JSON
        token_data = json.loads(token_json)

        # Check if token already exists
        existing = supabase.table("oauth_tokens").select("id").eq("user_email", email).execute()

        if existing.data:
            # Update existing token
            supabase.table("oauth_tokens").update({
                "token_json": token_data,
                "updated_at": "now()"
            }).eq("user_email", email).execute()
            print(f"✅ Token updated in Supabase for {email}")
        else:
            # Insert new token
            supabase.table("oauth_tokens").insert({
                "user_email": email,
                "token_json": token_data
            }).execute()
            print(f"✅ Token stored in Supabase for {email}")

    except Exception as e:
        print(f"❌ Error storing token in Supabase for {email}: {e}")

def get_token(email: str):
    """Fetch token JSON string for a given user email from Supabase."""
    try:
        result = supabase.table("oauth_tokens").select("token_json").eq("user_email", email).maybeSingle().execute()

        if result.data:
            print(f"✅ Token retrieved from Supabase for {email}")
            # Return as JSON string for backward compatibility
            return json.dumps(result.data["token_json"])

        print(f"⚠️ No token found in Supabase for {email}")
        return None

    except Exception as e:
        print(f"❌ Error retrieving token from Supabase for {email}: {e}")
        return None

def delete_token(email: str):
    """Delete token for a given user email from Supabase."""
    try:
        result = supabase.table("oauth_tokens").delete().eq("user_email", email).execute()

        if result.data:
            print(f"✅ Token deleted from Supabase for {email}")
        else:
            print(f"⚠️ No token found to delete in Supabase for {email}")

    except Exception as e:
        print(f"❌ Error deleting token from Supabase for {email}: {e}")

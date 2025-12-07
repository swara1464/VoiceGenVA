# backend/models/session_store.py
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")

# Initialize Supabase client
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ CRITICAL: Supabase credentials not found in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"✅ Supabase client initialized successfully")


def init_db():
    """No-op for backward compatibility. Supabase table already exists."""
    print("Using Supabase for token storage (oauth_tokens table)")

def store_token(email: str, token_json: str):
    """Store or update a user's token in Supabase."""
    try:
        print(f"💾 Attempting to store token for: {email}")

        # Validate JSON
        token_data = json.loads(token_json)
        print(f"💾 Token data parsed successfully")

        # Check if token already exists
        existing = supabase.table("oauth_tokens").select("id").eq("user_email", email).execute()
        print(f"💾 Existing token check: {bool(existing.data)}")

        if existing.data:
            # Update existing token - don't manually set updated_at, let DB handle it
            result = supabase.table("oauth_tokens").update({
                "token_json": token_data
            }).eq("user_email", email).execute()
            print(f"✅ Token updated in Supabase for {email}")
            print(f"✅ Update result: {result}")
        else:
            # Insert new token
            result = supabase.table("oauth_tokens").insert({
                "user_email": email,
                "token_json": token_data
            }).execute()
            print(f"✅ Token stored in Supabase for {email}")
            print(f"✅ Insert result: {result}")

    except Exception as e:
        print(f"❌ Error storing token in Supabase for {email}: {e}")
        import traceback
        traceback.print_exc()

def get_token(email: str):
    """Fetch token JSON string for a given user email from Supabase."""
    try:
        print(f"🔍 Attempting to retrieve token for: {email}")
        result = supabase.table("oauth_tokens").select("token_json").eq("user_email", email).maybeSingle().execute()

        print(f"🔍 Supabase query executed. Has data: {bool(result.data)}")

        if result.data:
            print(f"✅ Token retrieved from Supabase for {email}")
            token_json = result.data.get("token_json")

            # If token_json is already a dict, convert to string for backward compatibility
            if isinstance(token_json, dict):
                print(f"✅ Token is dict, converting to JSON string")
                return json.dumps(token_json)
            # If it's already a string, return as-is
            elif isinstance(token_json, str):
                print(f"✅ Token is string, returning as-is")
                return token_json
            else:
                print(f"❌ Unexpected token format: {type(token_json)}")
                return None

        print(f"⚠️ No token found in Supabase for {email}")
        return None

    except Exception as e:
        print(f"❌ Error retrieving token from Supabase for {email}: {e}")
        import traceback
        traceback.print_exc()
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

# backend/models/session_store.py
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase credentials - Using Service Role Key for server-side operations
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # This is the service_role key

# Initialize Supabase client
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ CRITICAL: Supabase credentials not found in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"✅ Supabase client initialized successfully with service role")


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

        # Use database function to bypass schema cache issues
        result = supabase.rpc('upsert_oauth_token', {
            'p_email': email,
            'p_token': token_data
        }).execute()

        print(f"✅ Token stored/updated in Supabase for {email} (ID: {result.data})")

    except Exception as e:
        # Fallback to PostgREST API if RPC fails
        try:
            print(f"⚠️ RPC failed, trying PostgREST API: {e}")
            existing = supabase.table("oauth_tokens").select("id").eq("user_email", email).execute()

            if existing.data:
                result = supabase.table("oauth_tokens").update({
                    "token_json": token_data
                }).eq("user_email", email).execute()
                print(f"✅ Token updated via PostgREST for {email}")
            else:
                result = supabase.table("oauth_tokens").insert({
                    "user_email": email,
                    "token_json": token_data
                }).execute()
                print(f"✅ Token stored via PostgREST for {email}")
        except Exception as fallback_error:
            print(f"❌ Error storing token in Supabase for {email}: {fallback_error}")
            import traceback
            traceback.print_exc()

def get_token(email: str):
    """Fetch token JSON string for a given user email from Supabase."""
    try:
        print(f"🔍 Attempting to retrieve token for: {email}")

        # Use database function to bypass schema cache issues
        try:
            result = supabase.rpc('get_oauth_token', {
                'p_email': email
            }).execute()

            token_json = result.data

            if token_json:
                print(f"✅ Token retrieved via RPC from Supabase for {email}")
                if isinstance(token_json, dict):
                    return json.dumps(token_json)
                elif isinstance(token_json, str):
                    return token_json
                else:
                    print(f"❌ Unexpected token format: {type(token_json)}")
                    return None
            else:
                print(f"⚠️ No token found in Supabase for {email}")
                return None

        except Exception as rpc_error:
            print(f"⚠️ RPC method failed, trying PostgREST API: {rpc_error}")

        # Fallback to PostgREST API
        result = supabase.table("oauth_tokens").select("token_json").eq("user_email", email).execute()

        print(f"🔍 Supabase query executed. Has data: {bool(result.data)}")

        if result.data and len(result.data) > 0:
            print(f"✅ Token retrieved from Supabase for {email}")
            token_json = result.data[0].get("token_json")

            if isinstance(token_json, dict):
                print(f"✅ Token is dict, converting to JSON string")
                return json.dumps(token_json)
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
        # Use database function to bypass schema cache issues
        result = supabase.rpc('delete_oauth_token', {
            'p_email': email
        }).execute()

        if result.data:
            print(f"✅ Token deleted from Supabase for {email}")
        else:
            print(f"⚠️ No token found to delete in Supabase for {email}")

    except Exception as e:
        print(f"❌ Error deleting token from Supabase for {email}: {e}")
        import traceback
        traceback.print_exc()

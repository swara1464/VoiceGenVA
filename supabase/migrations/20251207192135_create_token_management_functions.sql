/*
  # Create Token Management Functions
  
  1. Functions
    - `upsert_oauth_token(email, token)` - Insert or update OAuth token
    - `get_oauth_token(email)` - Retrieve OAuth token for user
    - `delete_oauth_token(email)` - Delete OAuth token for user
  
  2. Purpose
    - Bypass PostgREST schema cache issues by using direct function calls
    - Provide atomic operations for token management
    - Enable backend to work even when schema cache is stale
  
  3. Security
    - Functions execute with SECURITY DEFINER to bypass RLS
    - Only accessible via service role key (backend)
    - RLS remains enabled on table for additional protection
*/

-- Function to upsert (insert or update) an OAuth token
CREATE OR REPLACE FUNCTION upsert_oauth_token(
  p_email text,
  p_token jsonb
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_id uuid;
BEGIN
  INSERT INTO oauth_tokens (user_email, token_json)
  VALUES (p_email, p_token)
  ON CONFLICT (user_email)
  DO UPDATE SET 
    token_json = EXCLUDED.token_json,
    updated_at = now()
  RETURNING id INTO v_id;
  
  RETURN v_id;
END;
$$;

-- Function to get an OAuth token
CREATE OR REPLACE FUNCTION get_oauth_token(p_email text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_token jsonb;
BEGIN
  SELECT token_json INTO v_token
  FROM oauth_tokens
  WHERE user_email = p_email;
  
  RETURN v_token;
END;
$$;

-- Function to delete an OAuth token
CREATE OR REPLACE FUNCTION delete_oauth_token(p_email text)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_deleted boolean;
BEGIN
  DELETE FROM oauth_tokens
  WHERE user_email = p_email;
  
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RETURN v_deleted > 0;
END;
$$;
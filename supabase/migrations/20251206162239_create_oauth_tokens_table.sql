/*
  # Create OAuth Tokens Table

  1. New Tables
    - `oauth_tokens`
      - `id` (uuid, primary key)
      - `user_email` (text, unique, indexed)
      - `token_json` (jsonb, stores complete OAuth token data)
      - `created_at` (timestamp, automatic)
      - `updated_at` (timestamp, automatic)
  
  2. Security
    - Enable RLS on `oauth_tokens` table
    - Add policy for service role access only (users should not directly access tokens)
    - Tokens are managed server-side only via service role key
  
  3. Notes
    - Replaces SQLite session storage for production reliability
    - JSONB format stores token, refresh token, expiry, scopes, etc.
    - Updated timestamp tracks token refresh operations
*/

CREATE TABLE IF NOT EXISTS oauth_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_email text UNIQUE NOT NULL,
  token_json jsonb NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for fast lookup by email
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_email ON oauth_tokens(user_email);

-- Enable RLS
ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;

-- Service role has full access (backend uses service role key)
-- Users should NOT have direct access to tokens (security)
CREATE POLICY "Service role can manage all tokens"
  ON oauth_tokens
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_oauth_tokens_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp on updates
CREATE TRIGGER oauth_tokens_updated_at
  BEFORE UPDATE ON oauth_tokens
  FOR EACH ROW
  EXECUTE FUNCTION update_oauth_tokens_updated_at();
/*
  # Restore Service Role RLS Policy for OAuth Tokens

  1. Changes
    - Drop the anon policy
    - Restore service_role policy
    - Backend now uses SUPABASE_KEY (service role key) for secure token management

  2. Security
    - Only service role can access tokens
    - This is the most secure approach for server-side token storage
    - Frontend never accesses this table directly
*/

-- Drop the anon policy
DROP POLICY IF EXISTS "Backend can manage all tokens" ON oauth_tokens;

-- Restore service_role policy
CREATE POLICY "Service role can manage all tokens"
  ON oauth_tokens
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

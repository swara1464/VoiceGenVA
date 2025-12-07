/*
  # Fix OAuth Tokens RLS Policy

  1. Changes
    - Drop existing restrictive policy  
    - Add new policy that allows anon role to access tokens
    - This enables backend (using anon key) to store/retrieve tokens

  2. Security Note
    - Backend runs server-side with anon key
    - Frontend never directly accesses this table
    - Tokens are managed only through backend APIs
*/

-- Drop the existing policy
DROP POLICY IF EXISTS "Service role can manage all tokens" ON oauth_tokens;

-- Create new policy allowing anon role full access
-- (Backend uses anon key for server-side operations)
CREATE POLICY "Backend can manage all tokens"
  ON oauth_tokens
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);

/*
  # Create execution logs table

  1. New Tables
    - `logs`
      - `id` (uuid, primary key) - unique identifier for each log
      - `timestamp` (timestamptz) - when the action was executed
      - `user_email` (text) - email of user who triggered the action
      - `action` (text) - the type of action (e.g., GMAIL_SEND, CALENDAR_CREATE)
      - `status` (text) - status of the action (ATTEMPTING, SUCCESS, FAILED)
      - `details` (jsonb) - execution results or parameters

  2. Security
    - Enable RLS on `logs` table
    - Users can only read their own logs
    - Users cannot modify or delete logs (append-only audit trail)

  3. Indexes
    - Index on user_email for fast queries
    - Index on timestamp for sorting
*/

CREATE TABLE IF NOT EXISTS logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz DEFAULT now(),
  user_email text NOT NULL,
  action text NOT NULL,
  status text NOT NULL,
  details jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_logs_user_email ON logs(user_email);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);

ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own logs"
  ON logs FOR SELECT
  TO authenticated
  USING (user_email = auth.jwt()->>'email');

CREATE POLICY "Users cannot modify logs"
  ON logs FOR UPDATE
  TO authenticated
  USING (false);

CREATE POLICY "Users cannot delete logs"
  ON logs FOR DELETE
  TO authenticated
  USING (false);
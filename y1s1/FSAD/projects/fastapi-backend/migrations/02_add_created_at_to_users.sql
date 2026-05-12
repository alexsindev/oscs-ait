-- Add created_at column to users table
-- Migration: 02_add_created_at_to_users
-- Date: 2025-12-03

-- Add the created_at column with default value
ALTER TABLE users
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();

-- Set created_at for existing users to their earliest related record or current time
UPDATE users
SET created_at = COALESCE(
    (SELECT MIN(created_at) FROM posts WHERE owner_id = users.id),
    NOW()
)
WHERE created_at = NOW();

-- Add an index on created_at for better query performance
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

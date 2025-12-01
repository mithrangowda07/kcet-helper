-- Quick SQL script to add missing fields if needed
-- Run this in MySQL if your student table doesn't have is_staff and is_superuser

-- Check if columns exist first (optional - will error if they exist, but that's okay)
ALTER TABLE student 
ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;

-- Note: IF NOT EXISTS might not work in all MySQL versions
-- If it errors, the columns already exist, which is fine

-- Verify the structure
DESCRIBE student;


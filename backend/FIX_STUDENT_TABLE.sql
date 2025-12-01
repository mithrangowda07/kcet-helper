-- Complete SQL script to fix student table
-- Run this in MySQL to add all missing columns required by Django

USE dbms;

-- Check current structure first
DESCRIBE student;

-- Add all missing columns required by AbstractBaseUser and PermissionsMixin
-- If column already exists, you'll get an error - just skip that line

ALTER TABLE student 
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD COLUMN last_login TIMESTAMP NULL,
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;

-- Verify the changes
DESCRIBE student;

-- Expected columns after running this:
-- student_user_id (PRIMARY KEY)
-- type_of_student
-- unique_key (FK)
-- year_of_starting
-- college_code
-- phone_number
-- email_id
-- kcet_rank
-- hashed_password
-- created_at
-- updated_at
-- last_login
-- is_active
-- profile_completed
-- is_staff
-- is_superuser


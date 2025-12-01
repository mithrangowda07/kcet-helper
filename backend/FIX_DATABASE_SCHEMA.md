# Fix Database Schema Mismatch

## Error Explanation

The error `Unknown column 'updated_at' in 'field list'` means your database table doesn't have the `updated_at` column that Django is trying to use.

## Solution Options

### Option 1: Add Missing Columns to Database (Recommended)

Run this SQL script in MySQL to add the missing columns:

```sql
-- Add columns to student table
ALTER TABLE student 
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;

-- Add columns to college_reviews table
ALTER TABLE college_reviews
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Add columns to counselling_choices table
ALTER TABLE counselling_choices
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Add columns to student_meetings table
ALTER TABLE student_meetings
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
```

### Option 2: Check What Columns Actually Exist

First, check your actual table structure:

```sql
DESCRIBE student;
DESCRIBE college_reviews;
DESCRIBE counselling_choices;
DESCRIBE student_meetings;
```

Then adjust the models to match your actual database structure.

## Quick Fix Applied

I've updated the models to make `created_at` and `updated_at` nullable, but **you still need to add these columns to your database** for the application to work properly.

## Steps to Fix

1. **Check your table structure:**
   ```sql
   DESCRIBE student;
   ```

2. **Add missing columns** using the SQL script above

3. **Restart Django server:**
   ```bash
   python manage.py runserver
   ```

4. **Test registration again**

## Alternative: Remove Timestamp Fields

If you don't want to add these columns, you can remove them from the models, but this is **not recommended** as they're useful for tracking when records were created/updated.


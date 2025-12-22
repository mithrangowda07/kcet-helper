# Steps to Fix the Migration Error

The migration failed because it tried to add a unique field with default values, causing duplicate UUIDs. Follow these steps:

## Step 1: Clean the Database State

Run the fix script to remove partially created columns:

```powershell
cd backend
python fix_migration.py
```

This will remove any partially created `public_id` columns from the database.

## Step 2: Fake Rollback the Failed Migration (if needed)

If Django thinks the migration was applied, fake rollback it:

```powershell
python manage.py migrate colleges 0001_initial --fake
```

## Step 3: Run the Corrected Migration

Now run the migration again:

```powershell
python manage.py migrate
```

The corrected migration will:
1. Add `public_id` as nullable and non-unique
2. Populate unique UUIDs for all existing records
3. Make the field non-nullable and unique

## Alternative: Manual Database Fix

If the script doesn't work, manually run these SQL commands in your MySQL client:

```sql
-- Check if columns exist
SHOW COLUMNS FROM college LIKE 'public_id';
SHOW COLUMNS FROM branch LIKE 'public_id';

-- If they exist, remove them
ALTER TABLE college DROP COLUMN IF EXISTS public_id;
ALTER TABLE branch DROP COLUMN IF EXISTS public_id;

-- Drop any indexes if they exist
ALTER TABLE college DROP INDEX IF EXISTS college_public_id_unique;
ALTER TABLE branch DROP INDEX IF EXISTS branch_public_id_unique;
```

Then fake rollback and rerun the migration:

```powershell
python manage.py migrate colleges 0001_initial --fake
python manage.py migrate
```


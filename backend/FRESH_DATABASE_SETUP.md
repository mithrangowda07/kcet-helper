# Fresh Database Setup Guide

This guide will help you create a fresh database and let Django create all tables automatically.

## Step 1: Create New Database

Run this SQL in MySQL:

```sql
-- Drop old database if exists (WARNING: Deletes all data!)
DROP DATABASE IF EXISTS dbms_project;

-- Create fresh database
CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the new database
USE dbms_project;
```

Or use the provided script:
```bash
mysql -u root -p < CREATE_FRESH_DATABASE.sql
```

## Step 2: Update .env File

Update `backend/.env`:

```env
DB_NAME=dbms_project
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

## Step 3: Delete Old Migrations (Optional but Recommended)

To start completely fresh:

```bash
cd backend

# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

**OR manually delete:**
- `colleges/migrations/*.py` (except `__init__.py`)
- `students/migrations/*.py` (except `__init__.py`)
- `reviews/migrations/*.py` (except `__init__.py`)
- `counselling/migrations/*.py` (except `__init__.py`)
- `meetings/migrations/*.py` (except `__init__.py`)

## Step 4: Create Fresh Migrations

```bash
cd backend
python manage.py makemigrations
```

This will create migrations for:
- colleges (Cluster, College, Branch, Cutoff)
- students (Student, StudentCounter)
- reviews (CollegeReview)
- counselling (CounsellingChoice)
- meetings (StudentMeeting)

## Step 5: Apply Migrations

```bash
python manage.py migrate
```

This will create all tables in the `dbms_project` database.

## Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Step 7: Verify Tables Created

Check in MySQL:

```sql
USE dbms_project;
SHOW TABLES;
```

You should see:
- auth_group
- auth_group_permissions
- auth_permission
- auth_user_groups
- auth_user_user_permissions
- branch
- cluster
- college
- college_reviews
- counselling_choices
- cutoff
- django_admin_log
- django_content_type
- django_migrations
- django_session
- student
- student_counter
- student_meetings

## Step 8: Test the Application

```bash
python manage.py runserver
```

Try registering a new user - it should work now!

## Troubleshooting

### Error: "Table already exists"
- Make sure you're using the fresh `dbms_project` database
- Check `.env` file has correct database name
- Delete old migrations and recreate them

### Error: "Database doesn't exist"
- Run the CREATE DATABASE SQL command
- Verify database name in `.env` matches

### Error: "Migration conflicts"
- Delete all migration files (except `__init__.py`)
- Run `python manage.py makemigrations` again
- Run `python manage.py migrate`


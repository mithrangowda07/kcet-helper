# Database Setup for Existing MySQL Database

Since you already have tables in your MySQL database (`dbms`), follow these steps:

## Step 1: Update .env File

Make sure your `backend/.env` file has:

```env
DB_NAME=dbms
DB_USER=root
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
```

## Step 2: Check Database Schema

Verify your tables match the expected structure. Run this in MySQL:

```sql
DESCRIBE student;
DESCRIBE college;
DESCRIBE branch;
DESCRIBE cutoff;
DESCRIBE cluster;
DESCRIBE college_reviews;
DESCRIBE counselling_choices;
DESCRIBE student_meetings;
DESCRIBE student_counter;
```

## Step 3: Handle Missing Fields

If your `student` table doesn't have `is_staff` and `is_superuser` fields (which are added by PermissionsMixin), you have two options:

### Option A: Add Fields to Database (Recommended)

```sql
ALTER TABLE student 
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;
```

### Option B: Remove PermissionsMixin (If you don't need admin access)

Edit `backend/students/models.py` and change:
```python
class Student(AbstractBaseUser, PermissionsMixin):
```
to:
```python
class Student(AbstractBaseUser):
```

And remove any permission-related code.

## Step 4: Run Django Commands

```bash
cd backend
python manage.py makemigrations --dry-run  # Check what migrations would be created
python manage.py makemigrations  # Create migrations
python manage.py migrate --fake  # Mark migrations as applied without running them
```

**Important:** Use `--fake` flag because your tables already exist. This tells Django the migrations are already applied.

## Step 5: Verify Connection

```bash
python manage.py shell
```

Then in the shell:
```python
from colleges.models import College
College.objects.count()  # Should work if connection is good
```

## Step 6: Handle excel_import Table

The `excel_import` table is marked as `managed = False` in the model, so Django won't try to modify it. If you need to use it, you can query it directly:

```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM excel_import")
    rows = cursor.fetchall()
```

## Troubleshooting

### Error: "Table doesn't exist"
- Check table names match exactly (case-sensitive in some MySQL configs)
- Verify database name in `.env` is correct

### Error: "Unknown column"
- Check if all required fields exist in your tables
- Add missing columns manually or adjust the model

### Error: "Field type mismatch"
- Verify field types in database match model definitions
- Adjust model field types to match database

### Error: "Foreign key constraint"
- Verify foreign key relationships exist in database
- Check that referenced tables and columns exist


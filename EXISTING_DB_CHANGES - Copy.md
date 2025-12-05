# Changes Made for Existing Database

## Summary

The code has been updated to work with your existing MySQL database (`dbms`). Here's what was changed:

## ✅ Changes Made

### 1. Database Configuration (`backend/kcet_eduguide/settings.py`)
- Updated to use environment variables from `.env` file
- Default database name set to `dbms` (matching your database)
- Fixed SQL mode configuration
- Added proper charset settings

### 2. Models Updated
All models now have `managed = True` in Meta class to ensure Django manages them properly:

- ✅ `Cluster` - matches `cluster` table
- ✅ `College` - matches `college` table  
- ✅ `Branch` - matches `branch` table
- ✅ `Cutoff` - matches `cutoff` table
- ✅ `Student` - matches `student` table
- ✅ `StudentCounter` - matches `student_counter` table
- ✅ `CollegeReview` - matches `college_reviews` table
- ✅ `CounsellingChoice` - matches `counselling_choices` table
- ✅ `StudentMeeting` - matches `student_meetings` table
- ✅ `ExcelImport` - placeholder for `excel_import` table (marked as `managed = False`)

### 3. Student Model
- Removed explicit `is_staff` and `is_superuser` fields (they're added by `PermissionsMixin`)
- If your database doesn't have these columns, see instructions below

## 🔧 What You Need to Do

### Step 1: Update `.env` File

Create/update `backend/.env`:

```env
DB_NAME=dbms
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 2: Check Student Table Structure

Run in MySQL:
```sql
DESCRIBE student;
```

If `is_staff` and `is_superuser` columns don't exist, add them:

```sql
ALTER TABLE student 
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;
```

**OR** if you don't need admin features, edit `backend/students/models.py`:

Change:
```python
class Student(AbstractBaseUser, PermissionsMixin):
```

To:
```python
class Student(AbstractBaseUser):
```

### Step 3: Verify Table Names Match

All table names should match exactly (case-sensitive in some MySQL configs):

- ✅ `cluster` → `Cluster` model
- ✅ `college` → `College` model
- ✅ `branch` → `Branch` model
- ✅ `cutoff` → `Cutoff` model
- ✅ `student` → `Student` model
- ✅ `student_counter` → `StudentCounter` model
- ✅ `college_reviews` → `CollegeReview` model
- ✅ `counselling_choices` → `CounsellingChoice` model
- ✅ `student_meetings` → `StudentMeeting` model
- ⚠️ `excel_import` → `ExcelImport` model (unmanaged, won't be modified)

### Step 4: Run Django Commands

```bash
cd backend

# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Check what migrations would be created
python manage.py makemigrations --dry-run

# Create migrations (if needed)
python manage.py makemigrations

# Mark migrations as applied (since tables already exist)
python manage.py migrate --fake-initial

# Or if that doesn't work:
python manage.py migrate --fake
```

### Step 5: Test Connection

```bash
python manage.py shell
```

In the shell:
```python
from colleges.models import College
print(College.objects.count())  # Should show number of colleges
```

## ⚠️ Important Notes

1. **Field Types**: Make sure your database field types match the model definitions. If you get errors about field types, you may need to adjust either the database or the models.

2. **Foreign Keys**: Verify that foreign key relationships exist in your database. Django will use them if they exist.

3. **excel_import Table**: This table is marked as `managed = False`, so Django won't try to create or modify it. If you need to use it, query it directly using raw SQL.

4. **Migrations**: Since your tables already exist, use `--fake` or `--fake-initial` flags when running migrations to tell Django the tables are already created.

## 🐛 Troubleshooting

### Error: "Table 'dbms.student' doesn't exist"
- Check database name in `.env` matches your actual database name
- Verify you're connected to the correct MySQL database

### Error: "Unknown column 'is_staff'"
- Add the missing columns using the SQL script above
- Or remove `PermissionsMixin` from Student model

### Error: "Field type mismatch"
- Check your database column types match model field types
- Common issues: VARCHAR length, INTEGER vs BIGINT, etc.

### Error: "Foreign key constraint fails"
- Verify all referenced tables exist
- Check foreign key column names match `db_column` in models

## 📝 Next Steps

1. ✅ Update `.env` with your database credentials
2. ✅ Add `is_staff` and `is_superuser` columns if needed
3. ✅ Run migrations with `--fake-initial`
4. ✅ Test the connection
5. ✅ Start the server: `python manage.py runserver`

Your application should now work with your existing database!


# Complete Fresh Database Setup

This guide will help you create a completely fresh database `dbms_project` and let Django create all tables automatically.

## 🎯 Goal
- Create new database: `dbms_project`
- Remove old migrations
- Let Django create all tables with proper structure
- No manual table creation needed

## 📋 Step-by-Step Instructions

### Step 1: Create Fresh Database in MySQL

Open MySQL and run:

```sql
-- Drop old database if exists (WARNING: Deletes all data!)
DROP DATABASE IF EXISTS dbms_project;

-- Create fresh database
CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Verify
SHOW DATABASES LIKE 'dbms_project';
```

### Step 2: Update .env File

Update `backend/.env`:

```env
DB_NAME=dbms_project
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 3: Delete Old Migrations

**Windows (PowerShell):**
```powershell
cd backend
Get-ChildItem -Path . -Recurse -Filter "*.py" | Where-Object { 
    $_.FullName -match "migrations" -and $_.Name -ne "__init__.py" 
} | Remove-Item
```

**Linux/Mac:**
```bash
cd backend
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

**Or manually delete:**
- `colleges/migrations/0001_initial.py` (if exists)
- `students/migrations/0001_initial.py` (if exists)
- `reviews/migrations/0001_initial.py` (if exists)
- `counselling/migrations/0001_initial.py` (if exists)
- `meetings/migrations/0001_initial.py` (if exists)

**Keep:** All `__init__.py` files in migrations folders

### Step 4: Create Fresh Migrations

```bash
cd backend
python manage.py makemigrations
```

This will create migrations for:
- ✅ colleges (Cluster, College, Branch, Cutoff)
- ✅ students (Student, StudentCounter)
- ✅ reviews (CollegeReview)
- ✅ counselling (CounsellingChoice)
- ✅ meetings (StudentMeeting)

### Step 5: Apply Migrations (Create Tables)

```bash
python manage.py migrate
```

This will create ALL tables in `dbms_project` database with correct structure.

### Step 6: Verify Tables Created

Check in MySQL:

```sql
USE dbms_project;
SHOW TABLES;
```

You should see these tables:
- ✅ `cluster`
- ✅ `college`
- ✅ `branch`
- ✅ `cutoff`
- ✅ `student`
- ✅ `student_counter`
- ✅ `college_reviews`
- ✅ `counselling_choices`
- ✅ `student_meetings`
- Plus Django system tables (auth_*, django_*, etc.)

### Step 7: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 8: Test the Application

```bash
python manage.py runserver
```

Try registering a new user - it should work perfectly now!

## 🗑️ What Gets Created

### Your Application Tables:
1. **cluster** - Cluster codes and names
2. **college** - College information
3. **branch** - Branch information (linked to college and cluster)
4. **cutoff** - Historical cutoff data
5. **student** - Student accounts (with all required fields)
6. **student_counter** - Counter for student ID generation
7. **college_reviews** - Reviews by studying students
8. **counselling_choices** - Saved choices by counselling students
9. **student_meetings** - Meeting requests and scheduled meetings

### Django System Tables:
- `django_migrations` - Tracks applied migrations
- `django_content_type` - Content types
- `django_session` - Session data
- `auth_*` - Authentication tables (if using Django auth)

## ✅ Verification Checklist

- [ ] Database `dbms_project` created
- [ ] `.env` file updated with `DB_NAME=dbms_project`
- [ ] Old migrations deleted
- [ ] Fresh migrations created (`makemigrations`)
- [ ] Migrations applied (`migrate`)
- [ ] All tables visible in MySQL
- [ ] Server starts without errors
- [ ] Registration works

## 🐛 Troubleshooting

### Error: "Table already exists"
- Make sure you're using `dbms_project` (not `dbms`)
- Check `.env` file has correct database name
- Delete old migrations and recreate

### Error: "Database doesn't exist"
- Run the CREATE DATABASE SQL command
- Verify database name in `.env` matches

### Error: "Migration conflicts"
- Delete all migration files (except `__init__.py`)
- Run `python manage.py makemigrations` again
- Run `python manage.py migrate`

### Error: "Unknown column"
- This shouldn't happen with fresh migrations
- If it does, delete database and start over

## 🎉 Success!

Once all steps are complete, your application will have:
- ✅ Clean database structure
- ✅ All required columns
- ✅ Proper foreign keys
- ✅ Working authentication
- ✅ Ready for data entry


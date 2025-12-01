@echo off
REM Script to set up fresh database and migrations for Windows

echo ========================================
echo Fresh Database Setup Script
echo ========================================
echo.

echo Step 1: Creating fresh database...
echo Please run this SQL in MySQL:
echo.
echo DROP DATABASE IF EXISTS dbms_project;
echo CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo.
pause

echo.
echo Step 2: Deleting old migration files...
for /d /r . %%d in (migrations) do @if exist "%%d" (
    echo Deleting migrations in %%d
    del /q "%%d\*.py" 2>nul
    del /q "%%d\*.pyc" 2>nul
    echo. > "%%d\__init__.py"
)

echo.
echo Step 3: Creating fresh migrations...
python manage.py makemigrations

echo.
echo Step 4: Applying migrations...
python manage.py migrate

echo.
echo Step 5: Creating superuser (optional)...
python manage.py createsuperuser

echo.
echo ========================================
echo Setup Complete!
echo ========================================
pause


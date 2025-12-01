#!/bin/bash
# Script to set up fresh database and migrations for Linux/Mac

echo "========================================"
echo "Fresh Database Setup Script"
echo "========================================"
echo ""

echo "Step 1: Creating fresh database..."
echo "Please run this SQL in MySQL:"
echo ""
echo "DROP DATABASE IF EXISTS dbms_project;"
echo "CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo ""
read -p "Press enter after creating the database..."

echo ""
echo "Step 2: Deleting old migration files..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo ""
echo "Step 3: Creating fresh migrations..."
python manage.py makemigrations

echo ""
echo "Step 4: Applying migrations..."
python manage.py migrate

echo ""
echo "Step 5: Creating superuser (optional)..."
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"


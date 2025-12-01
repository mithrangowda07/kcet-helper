-- Script to create fresh database and let Django handle table creation
-- Run this in MySQL

-- Drop the old database if it exists (WARNING: This will delete all data!)
DROP DATABASE IF EXISTS dbms_project;

-- Create new fresh database
CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the new database
USE dbms_project;

-- Verify database is created
SHOW DATABASES LIKE 'dbms_project';

-- Note: Django will create all tables when you run migrations
-- No need to create tables manually!


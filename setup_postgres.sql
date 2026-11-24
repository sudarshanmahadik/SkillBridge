-- SkillBridge PostgreSQL Database Setup Script
-- Run this script using: psql -U postgres -f setup_postgres.sql

-- 1. Create database if it doesn't already exist
CREATE DATABASE skillbridge_db;

-- 2. Connect to the database
\c skillbridge_db;

-- 3. Verification message
SELECT 'SkillBridge database successfully created and ready for SQLAlchemy tables.' AS status;

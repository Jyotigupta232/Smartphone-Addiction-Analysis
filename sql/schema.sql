-- ====================================================================
-- XENO Data Engineering & Analytics Database Schema
-- Smartphone Addiction Analysis & Scale Performance System
-- ====================================================================

-- 1. User Behavioral Survey Table
CREATE TABLE IF NOT EXISTS users_survey (
    user_id TEXT PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    daily_usage_hours REAL,
    phone_usage_before_sleep TEXT,
    anxiety_without_phone TEXT,
    checks_per_hour INTEGER,
    impact_on_daily_life TEXT,
    time_without_checking_min INTEGER,
    smartphone_addiction INTEGER -- 1: Yes, 0: No, -1: Not Sure
);

-- 2. Unindexed App Usage Sessions Table (For Benchmark Testing)
CREATE TABLE IF NOT EXISTS app_usage_sessions_unindexed (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    app_category TEXT,
    app_name TEXT,
    session_duration_min REAL,
    screen_unlocks_in_session INTEGER,
    session_timestamp TIMESTAMP
);

-- 3. Indexed App Usage Sessions Table (Optimized for Production Scale)
CREATE TABLE IF NOT EXISTS app_usage_sessions_indexed (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    app_category TEXT,
    app_name TEXT,
    session_duration_min REAL,
    screen_unlocks_in_session INTEGER,
    session_timestamp TIMESTAMP
);

-- Indexes for High-Speed Query Performance (XENO Core Competency)
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON app_usage_sessions_indexed(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_category_timestamp ON app_usage_sessions_indexed(app_category, session_timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_app_duration ON app_usage_sessions_indexed(app_name, session_duration_min);

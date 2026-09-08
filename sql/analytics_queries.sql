-- ====================================================================
-- XENO Analytics Query Suite: Smartphone Usage & Behavioral Insights
-- Features: CTEs, Window Functions (LAG, RANK), Cohort Analysis, Joins
-- ====================================================================

-- 1. High-Frequency Users Ranking using Window Functions (RANK & ROW_NUMBER)
-- Goal: Identify top smartphone consumers per category by total screen duration
WITH CategoryUsage AS (
    SELECT 
        s.user_id,
        u.gender,
        u.smartphone_addiction,
        s.app_category,
        SUM(s.session_duration_min) AS total_category_min,
        COUNT(s.session_id) AS total_sessions,
        RANK() OVER (PARTITION BY s.app_category ORDER BY SUM(s.session_duration_min) DESC) AS category_rank
    FROM app_usage_sessions_indexed s
    JOIN users_survey u ON s.user_id = u.user_id
    GROUP BY s.user_id, s.app_category
)
SELECT * 
FROM CategoryUsage 
WHERE category_rank <= 5;

-- 2. Inter-Session Gap & Rapid Re-Unlock Analysis (Using LAG Window Function)
-- Goal: Detect impulse unlocking habits (re-unlocking phone within 3 minutes of closing an app)
WITH SessionGaps AS (
    SELECT 
        user_id,
        session_id,
        app_name,
        session_timestamp,
        LAG(session_timestamp) OVER (PARTITION BY user_id ORDER BY session_timestamp) AS prev_session_timestamp,
        session_duration_min
    FROM app_usage_sessions_indexed
)
SELECT 
    user_id,
    COUNT(*) AS rapid_reunlock_count,
    AVG(session_duration_min) AS avg_duration_after_reunlock
FROM (
    SELECT 
        user_id,
        session_duration_min,
        (JULIANDAY(session_timestamp) - JULIANDAY(prev_session_timestamp)) * 24 * 60 AS gap_minutes
    FROM SessionGaps
    WHERE prev_session_timestamp IS NOT NULL
)
WHERE gap_minutes <= 3.0
GROUP BY user_id
ORDER BY rapid_reunlock_count DESC
LIMIT 10;

-- 3. Nighttime Smartphone Usage Cohort Analysis (11 PM - 5 AM) vs Addiction Level
-- Goal: Correlate late-night usage with self-reported addiction & anxiety
WITH NightSessions AS (
    SELECT 
        s.user_id,
        SUM(CASE WHEN CAST(STRFTIME('%H', s.session_timestamp) AS INTEGER) >= 23 
                  OR CAST(STRFTIME('%H', s.session_timestamp) AS INTEGER) < 5 
                 THEN s.session_duration_min ELSE 0 END) AS night_duration_min,
        SUM(s.session_duration_min) AS total_duration_min
    FROM app_usage_sessions_indexed s
    GROUP BY s.user_id
)
SELECT 
    u.smartphone_addiction,
    u.phone_usage_before_sleep,
    COUNT(u.user_id) AS user_count,
    ROUND(AVG(n.night_duration_min), 2) AS avg_night_duration_min,
    ROUND(AVG((n.night_duration_min * 100.0) / NULLIF(n.total_duration_min, 0)), 2) AS avg_night_usage_pct
FROM users_survey u
JOIN NightSessions n ON u.user_id = n.user_id
GROUP BY u.smartphone_addiction, u.phone_usage_before_sleep
ORDER BY u.smartphone_addiction DESC;

-- 4. RFM Behavioral Scoring (Recency of Check, Frequency of Session, Duration Intensity)
-- Goal: Categorize users into 'High Addiction Risk', 'Moderate Risk', and 'Healthy Users'
WITH RFM_Base AS (
    SELECT 
        u.user_id,
        u.anxiety_without_phone,
        COUNT(s.session_id) AS total_sessions,
        SUM(s.session_duration_min) AS total_screen_time_min,
        AVG(s.screen_unlocks_in_session) AS avg_unlocks_per_session
    FROM users_survey u
    LEFT JOIN app_usage_sessions_indexed s ON u.user_id = s.user_id
    GROUP BY u.user_id
),
RFM_Scores AS (
    SELECT 
        user_id,
        anxiety_without_phone,
        total_sessions,
        total_screen_time_min,
        NTILE(3) OVER (ORDER BY total_sessions DESC) AS frequency_score,
        NTILE(3) OVER (ORDER BY total_screen_time_min DESC) AS duration_score,
        NTILE(3) OVER (ORDER BY avg_unlocks_per_session DESC) AS intensity_score
    FROM RFM_Base
)
SELECT 
    user_id,
    anxiety_without_phone,
    (frequency_score + duration_score + intensity_score) AS composite_addiction_score,
    CASE 
        WHEN (frequency_score + duration_score + intensity_score) >= 8 THEN 'Critical Risk'
        WHEN (frequency_score + duration_score + intensity_score) >= 5 THEN 'Moderate Risk'
        ELSE 'Low Risk'
    END AS risk_category
FROM RFM_Scores
ORDER BY composite_addiction_score DESC
LIMIT 15;

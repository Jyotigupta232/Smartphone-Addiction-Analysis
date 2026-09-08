import sqlite3
import pandas as pd
import numpy as np
import os
import re

def load_custom_df_to_dw(df_uploaded, db_path):
    """
    Ingests any user-uploaded CSV/Excel DataFrame into the 7-Table SQLite Data Warehouse,
    mapping flexible column variations and survey text responses dynamically into numerical dw tables.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    df = df_uploaded.copy()
    n_rows = len(df)

    # Helper function to find matching column using strict patterns
    def find_col_by_regex(patterns):
        for col in df.columns:
            col_lower = str(col).strip().lower()
            for pat in patterns:
                if re.search(pat, col_lower):
                    return col
        return None

    # 1. User IDs (Avoid matching words like 'use your')
    uid_col = find_col_by_regex([r'^\s*user_id\s*$', r'^\s*student_id\s*$', r'^\s*participant_id\s*$', r'\buser_id\b'])
    if uid_col and df[uid_col].nunique() >= min(10, n_rows // 2):
        user_ids = [f"USR_{str(val).strip()}" for val in df[uid_col]]
    else:
        user_ids = [f"USR_{1001 + i}" for i in range(n_rows)]
    df['user_id'] = user_ids

    # 2. Age Parser
    age_col = find_col_by_regex([r'\bage\b', r'how_old', r'1\.\s*age'])
    parsed_ages = []
    if age_col:
        for val in df[age_col]:
            val_str = str(val).strip().lower()
            if '15' in val_str or '18' in val_str:
                parsed_ages.append(17)
            elif '19' in val_str or '22' in val_str or '20' in val_str:
                parsed_ages.append(21)
            elif '23' in val_str or '25' in val_str:
                parsed_ages.append(24)
            elif '26' in val_str or '30' in val_str:
                parsed_ages.append(28)
            else:
                num = pd.to_numeric(val, errors='coerce')
                parsed_ages.append(int(num) if pd.notnull(num) else 22)
    else:
        parsed_ages = np.random.randint(17, 30, n_rows).tolist()
    df['age'] = parsed_ages

    # 3. Screen Time (Hours)
    st_col = find_col_by_regex([r'screen_time', r'hours', r'usage', r'daily.*smartphone', r'spend.*smartphone'])
    parsed_st = []
    if st_col:
        for val in df[st_col]:
            v_str = str(val).strip().lower()
            if 'less' in v_str or '<2' in v_str or ('1' in v_str and '2' in v_str and '12' not in v_str):
                parsed_st.append(1.5)
            elif '2' in v_str and '4' in v_str:
                parsed_st.append(3.0)
            elif '4' in v_str and '6' in v_str:
                parsed_st.append(5.0)
            elif 'more' in v_str or '6' in v_str or '>6' in v_str:
                parsed_st.append(8.5)
            else:
                num = pd.to_numeric(val, errors='coerce')
                parsed_st.append(float(num) if pd.notnull(num) else 5.5)
    else:
        parsed_st = np.round(np.random.normal(6.5, 2.0, n_rows).clip(1.5, 12.0), 1).tolist()
    df['screen_time'] = parsed_st

    # 4. Unlocks / Pickups per Day
    un_col = find_col_by_regex([r'unlock', r'check.*phone', r'frequency', r'times.*hour', r'pickups'])
    parsed_un = []
    if un_col:
        for val in df[un_col]:
            v_str = str(val).strip().lower()
            if '1' in v_str and '2' in v_str:
                parsed_un.append(25)
            elif '3' in v_str and '5' in v_str:
                parsed_un.append(60)
            elif '6' in v_str and '10' in v_str:
                parsed_un.append(120)
            elif 'more' in v_str or '10' in v_str:
                parsed_un.append(185)
            else:
                num = pd.to_numeric(val, errors='coerce')
                if pd.notnull(num):
                    parsed_un.append(int(num * 12 if num <= 25 else num))
                else:
                    parsed_un.append(75)
    else:
        parsed_un = np.random.randint(30, 180, n_rows).tolist()
    df['unlocks'] = parsed_un

    # 5. Sleep Hours & Bedtime Habits
    sl_col = find_col_by_regex([r'sleep', r'bedtime', r'before.*sleeping', r'night'])
    parsed_sl = []
    if sl_col:
        for val in df[sl_col]:
            v_str = str(val).strip().lower()
            if 'never' in v_str:
                parsed_sl.append(8.2)
            elif 'rarely' in v_str:
                parsed_sl.append(7.5)
            elif 'sometimes' in v_str:
                parsed_sl.append(6.0)
            elif 'always' in v_str:
                parsed_sl.append(4.8)
            else:
                num = pd.to_numeric(val, errors='coerce')
                parsed_sl.append(float(num) if pd.notnull(num) else 6.5)
    else:
        parsed_sl = np.round(np.random.normal(6.5, 1.2, n_rows).clip(3.5, 9.0), 1).tolist()
    df['sleep_hours'] = parsed_sl

    # 6. Daily Notifications & Anxiety Level
    anx_col = find_col_by_regex([r'anxious', r'restless', r'notif', r'alert'])
    parsed_notif = []
    if anx_col:
        for val in df[anx_col]:
            v_str = str(val).strip().lower()
            if 'very' in v_str or 'frequently' in v_str or 'always' in v_str:
                parsed_notif.append(310)
            elif 'sometimes' in v_str or 'occasionally' in v_str:
                parsed_notif.append(185)
            elif 'rarely' in v_str:
                parsed_notif.append(90)
            elif 'never' in v_str:
                parsed_notif.append(40)
            else:
                num = pd.to_numeric(val, errors='coerce')
                parsed_notif.append(int(num) if pd.notnull(num) else 140)
    else:
        parsed_notif = np.random.randint(40, 320, n_rows).tolist()
    df['daily_notifications'] = parsed_notif

    # 7. App Name & Category
    app_col = find_col_by_regex([r'primarily.*use', r'app_name', r'most_used', r'category', r'purpose'])
    if app_col:
        raw_apps = df[app_col].astype(str).fillna('Social Media')
        df['app_name'] = raw_apps
        cat_list = []
        for a_str in raw_apps:
            a_lower = a_str.lower()
            if 'social' in a_lower:
                cat_list.append('Social Media')
            elif 'study' in a_lower or 'class' in a_lower or 'work' in a_lower:
                cat_list.append('Productivity')
            elif 'video' in a_lower or 'ott' in a_lower or 'movie' in a_lower:
                cat_list.append('Entertainment')
            elif 'game' in a_lower or 'gaming' in a_lower:
                cat_list.append('Gaming')
            elif 'call' in a_lower or 'message' in a_lower or 'chat' in a_lower:
                cat_list.append('Messaging')
            else:
                cat_list.append('Other')
        df['category'] = cat_list
    else:
        df['app_name'] = np.random.choice(['Instagram', 'TikTok', 'WhatsApp', 'YouTube', 'PUBG Mobile', 'Notion'], size=n_rows)
        df['category'] = np.random.choice(['Social Media', 'Productivity', 'Entertainment', 'Gaming', 'Messaging'], size=n_rows)

    df['time_spent'] = np.round(df['screen_time'] * 40.0, 1)
    df['day_type'] = np.random.choice(['Weekday', 'Weekend'], size=n_rows, p=[0.71, 0.29])

    # 8. Addiction Risk Target Level
    addict_col = find_col_by_regex([r'addicted', r'risk_level', r'affected.*studies', r'addiction_risk'])
    parsed_risk = []
    if addict_col:
        for idx in range(n_rows):
            val_str = str(df[addict_col].iloc[idx]).strip().lower()
            if 'yes' in val_str or 'high' in val_str or 'frequently' in val_str:
                parsed_risk.append('High Risk')
            elif 'not sure' in val_str or 'medium' in val_str or 'occasionally' in val_str:
                parsed_risk.append('Medium Risk')
            elif 'no' in val_str or 'low' in val_str or 'never' in val_str or 'rarely' in val_str:
                parsed_risk.append('Low Risk')
            else:
                st_v = df['screen_time'].iloc[idx]
                sl_v = df['sleep_hours'].iloc[idx]
                score = 0.4 * st_v - 0.5 * sl_v
                parsed_risk.append('High Risk' if score > 1.5 else ('Medium Risk' if score > 0.5 else 'Low Risk'))
    else:
        for st_v, sl_v in zip(df['screen_time'], df['sleep_hours']):
            score = 0.4 * st_v - 0.5 * sl_v
            parsed_risk.append('High Risk' if score > 1.5 else ('Medium Risk' if score > 0.5 else 'Low Risk'))
    df['addiction_risk_level'] = parsed_risk

    # Construct 7 Relational DataWarehouse Tables
    unique_users = list(set(df['user_id'].tolist()))
    n_unique = len(unique_users)

    # Productivity Score derived from sleep, screen time, and age
    prod_scores = np.round((10.0 - (df['screen_time'] * 0.4) + (df['sleep_hours'] * 0.3)).clip(3.0, 9.8), 1).tolist()
    genders = df[find_col_by_regex([r'gender'])] if find_col_by_regex([r'gender']) else np.random.choice(['Female', 'Male', 'Prefer not to say'], n_unique)

    df_users = pd.DataFrame({
        'user_id': unique_users,
        'age': df.groupby('user_id')['age'].first().values,
        'gender': pd.Series(genders).astype(str).tolist()[:n_unique],
        'occupation': np.random.choice(['Student', 'Software Engineer', 'Data Analyst', 'Designer'], n_unique),
        'productivity_score': pd.Series(prod_scores).tolist()[:n_unique]
    })

    df_usage_logs = pd.DataFrame({
        'log_id': [500000 + i for i in range(n_rows)],
        'user_id': df['user_id'],
        'log_date': pd.date_range(end='2026-03-01', periods=n_rows, freq='h').strftime('%Y-%m-%d'),
        'screen_time': df['screen_time'],
        'unlocks': df['unlocks'],
        'day_type': df['day_type']
    })

    df_app_usage = pd.DataFrame({
        'app_log_id': [900000 + i for i in range(n_rows)],
        'user_id': df['user_id'],
        'app_name': df['app_name'],
        'category': df['category'],
        'time_spent': df['time_spent'],
        'log_date': pd.date_range(end='2026-03-01', periods=n_rows, freq='h').strftime('%Y-%m-%d')
    })

    df_sleep = pd.DataFrame({
        'sleep_id': [3000 + i for i in range(n_unique)],
        'user_id': unique_users,
        'sleep_hours': df.groupby('user_id')['sleep_hours'].mean().values,
        'sleep_quality_score': np.round((df.groupby('user_id')['sleep_hours'].mean().values * 1.1).clip(3.5, 9.5), 1),
        'phone_before_bed': np.random.choice(['Yes', 'No'], n_unique)
    })

    df_notifications = pd.DataFrame({
        'notif_id': [4000 + i for i in range(n_unique)],
        'user_id': unique_users,
        'daily_notifications': df.groupby('user_id')['daily_notifications'].mean().astype(int).values,
        'muted_count': np.random.randint(5, 45, n_unique)
    })

    df_feedback = pd.DataFrame({
        'feedback_id': [7000 + i for i in range(n_unique)],
        'user_id': unique_users,
        'addiction_risk_level': df.groupby('user_id')['addiction_risk_level'].first().values,
        'anxiety_level': np.random.choice(['High', 'Moderate', 'Low', 'None'], n_unique)
    })

    # Ingest into SQLite Database
    df_users.to_sql('users', conn, if_exists='replace', index=False)
    df_usage_logs.to_sql('usage_logs_unindexed', conn, if_exists='replace', index=False)
    df_usage_logs.to_sql('usage_logs', conn, if_exists='replace', index=False)
    df_app_usage.to_sql('app_usage', conn, if_exists='replace', index=False)
    df_sleep.to_sql('sleep_patterns', conn, if_exists='replace', index=False)
    df_notifications.to_sql('notifications', conn, if_exists='replace', index=False)
    df_feedback.to_sql('user_feedback', conn, if_exists='replace', index=False)

    # Re-apply Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user ON usage_logs(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_app_user ON app_usage(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_app_name ON app_usage(app_name);")
    conn.commit()
    conn.close()

    return n_rows, n_unique

def generate_sample_csv_template():
    """Generates a sample CSV template for users to download."""
    sample_df = pd.DataFrame({
        'user_id': [1001, 1002, 1003, 1004, 1005],
        'screen_time': [9.5, 4.2, 11.0, 3.5, 8.0],
        'unlocks': [120, 45, 160, 30, 95],
        'sleep_hours': [5.0, 7.5, 4.5, 8.0, 6.0],
        'daily_notifications': [240, 60, 320, 40, 180],
        'app_name': ['Instagram', 'Notion', 'TikTok', 'WhatsApp', 'YouTube'],
        'category': ['Social Media', 'Productivity', 'Social Media', 'Messaging', 'Entertainment'],
        'time_spent': [210, 45, 280, 50, 160],
        'day_type': ['Weekday', 'Weekday', 'Weekend', 'Weekday', 'Weekend']
    })
    return sample_df.to_csv(index=False).encode('utf-8')


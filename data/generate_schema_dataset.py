import os
import sqlite3
import numpy as np
import pandas as pd

def build_data_warehouse(data_dir, n_users=2500, n_logs=100000, random_state=42):
    np.random.seed(random_state)
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'smartphone_addiction_dw.db')
    
    # 1. Users Table
    user_ids = [1000 + i for i in range(n_users)]
    ages = np.random.randint(16, 45, size=n_users)
    genders = np.random.choice(['Male', 'Female', 'Other'], size=n_users, p=[0.48, 0.48, 0.04])
    occupations = np.random.choice(['Student', 'Software Engineer', 'Data Analyst', 'Student', 'Marketing Specialist', 'Designer', 'Other'], size=n_users)
    productivity_scores = np.round(np.random.uniform(3.0, 9.8, size=n_users), 1)
    
    df_users = pd.DataFrame({
        'user_id': user_ids,
        'age': ages,
        'gender': genders,
        'occupation': occupations,
        'productivity_score': productivity_scores
    })
    
    # 2. Usage Logs Table (High Volume)
    log_ids = [500000 + i for i in range(n_logs)]
    chosen_users = np.random.choice(user_ids, size=n_logs)
    dates = pd.date_range(end='2026-03-01', periods=90, freq='D')
    chosen_dates = np.random.choice(dates, size=n_logs)
    chosen_dates_ts = [pd.Timestamp(d) for d in chosen_dates]
    day_types = ['Weekend' if d.dayofweek in [5, 6] else 'Weekday' for d in chosen_dates_ts]
    screen_times = np.round(np.random.normal(loc=6.8, scale=2.8, size=n_logs).clip(0.5, 15.0), 1)
    unlocks = np.random.poisson(lam=65, size=n_logs).clip(10, 220)
    
    df_usage_logs = pd.DataFrame({
        'log_id': log_ids,
        'user_id': chosen_users,
        'log_date': [d.strftime('%Y-%m-%d') for d in chosen_dates_ts],
        'screen_time': screen_times,
        'unlocks': unlocks,
        'day_type': day_types
    })
    
    # 3. App Usage Table
    apps_categories = {
        'Instagram': 'Social Media',
        'TikTok': 'Social Media',
        'WhatsApp': 'Messaging',
        'YouTube': 'Entertainment',
        'PUBG Mobile': 'Gaming',
        'Netflix': 'Entertainment',
        'Reddit': 'Social Media',
        'Gmail': 'Productivity',
        'Notion': 'Productivity',
        'Subway Surfers': 'Gaming'
    }
    app_names_list = list(apps_categories.keys())
    
    chosen_apps = np.random.choice(app_names_list, size=n_logs)
    chosen_categories = [apps_categories[a] for a in chosen_apps]
    time_spents = np.round(np.random.exponential(scale=45.0, size=n_logs).clip(5.0, 320.0), 1)
    
    df_app_usage = pd.DataFrame({
        'app_log_id': [900000 + i for i in range(n_logs)],
        'user_id': chosen_users,
        'app_name': chosen_apps,
        'category': chosen_categories,
        'time_spent': time_spents,
        'log_date': [d.strftime('%Y-%m-%d') for d in chosen_dates_ts]
    })
    
    # 4. Sleep Patterns Table
    sleep_hrs = np.round(np.random.normal(loc=6.5, scale=1.4, size=n_users).clip(3.0, 10.0), 1)
    sleep_quality = np.round(np.random.uniform(4.0, 9.5, size=n_users), 1)
    phone_before_bed = np.random.choice(['Yes', 'No'], size=n_users, p=[0.75, 0.25])
    
    df_sleep_patterns = pd.DataFrame({
        'sleep_id': [3000 + i for i in range(n_users)],
        'user_id': user_ids,
        'sleep_hours': sleep_hrs,
        'sleep_quality_score': sleep_quality,
        'phone_before_bed': phone_before_bed
    })
    
    # 5. Notifications Table
    daily_notifs = np.random.randint(40, 350, size=n_users)
    muted_counts = np.random.randint(0, 80, size=n_users)
    
    df_notifications = pd.DataFrame({
        'notif_id': [4000 + i for i in range(n_users)],
        'user_id': user_ids,
        'daily_notifications': daily_notifs,
        'muted_count': muted_counts
    })
    
    # 6. User Feedback & Addiction Risk Target Table
    # Target: High Risk, Medium Risk, Low Risk
    risk_scores = (
        0.35 * df_users['user_id'].map(df_usage_logs.groupby('user_id')['screen_time'].mean()).fillna(6.0) +
        0.015 * df_notifications['daily_notifications'] -
        0.4 * df_sleep_patterns['sleep_hours'] +
        0.02 * df_users['user_id'].map(df_usage_logs.groupby('user_id')['unlocks'].mean()).fillna(50)
    )
    
    risk_labels = []
    for r in risk_scores:
        if r > 5.2:
            risk_labels.append('High Risk')
        elif r > 3.8:
            risk_labels.append('Medium Risk')
        else:
            risk_labels.append('Low Risk')
            
    df_user_feedback = pd.DataFrame({
        'feedback_id': [7000 + i for i in range(n_users)],
        'user_id': user_ids,
        'addiction_risk_level': risk_labels,
        'anxiety_level': np.random.choice(['High', 'Moderate', 'Low', 'None'], size=n_users, p=[0.35, 0.35, 0.20, 0.10])
    })
    
    # 7. Screen Time Table
    df_screen_time = pd.DataFrame({
        'screen_id': [8000 + i for i in range(n_users)],
        'user_id': user_ids,
        'pickup_count': df_users['user_id'].map(df_usage_logs.groupby('user_id')['unlocks'].mean()).astype(int).fillna(45),
        'continuous_screen_hrs': np.round(np.random.uniform(1.0, 5.5, size=n_users), 1)
    })
    
    # Write to SQLite Database
    conn = sqlite3.connect(db_path)
    df_users.to_sql('users', conn, if_exists='replace', index=False)
    df_usage_logs.to_sql('usage_logs_unindexed', conn, if_exists='replace', index=False)
    df_usage_logs.to_sql('usage_logs', conn, if_exists='replace', index=False)
    df_app_usage.to_sql('app_usage', conn, if_exists='replace', index=False)
    df_screen_time.to_sql('screen_time', conn, if_exists='replace', index=False)
    df_sleep_patterns.to_sql('sleep_patterns', conn, if_exists='replace', index=False)
    df_notifications.to_sql('notifications', conn, if_exists='replace', index=False)
    df_user_feedback.to_sql('user_feedback', conn, if_exists='replace', index=False)
    
    # Apply Indexes to `usage_logs` and `app_usage`
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user ON usage_logs(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_app_user ON app_usage(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_app_name ON app_usage(app_name);")
    conn.commit()
    conn.close()
    
    # Save CSVs for easy reference
    df_users.to_csv(os.path.join(data_dir, 'users.csv'), index=False)
    df_usage_logs.to_csv(os.path.join(data_dir, 'usage_logs.csv'), index=False)
    df_app_usage.to_csv(os.path.join(data_dir, 'app_usage.csv'), index=False)
    df_sleep_patterns.to_csv(os.path.join(data_dir, 'sleep_patterns.csv'), index=False)
    df_notifications.to_csv(os.path.join(data_dir, 'notifications.csv'), index=False)
    df_user_feedback.to_csv(os.path.join(data_dir, 'user_feedback.csv'), index=False)
    
    print(f"Successfully generated 7-Table Relational Data Warehouse at {db_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_data_warehouse(os.path.join(base_dir, 'data'))

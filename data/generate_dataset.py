import os
import sqlite3
import numpy as np
import pandas as pd

def generate_survey_dataset(n_samples=2500, random_state=42):
    """
    Generates behavioral survey dataset matching smartphone addiction attributes.
    Target Variable: Self-Reported Smartphone Addiction (1 -> Yes, 0 -> No, -1 -> Not Sure)
    """
    np.random.seed(random_state)
    
    age = np.random.randint(16, 35, size=n_samples)
    genders = np.random.choice(['Male', 'Female', 'Other'], size=n_samples, p=[0.48, 0.48, 0.04])
    daily_usage_hours = np.round(np.random.normal(loc=5.5, scale=2.2, size=n_samples).clip(0.5, 14.0), 1)
    phone_usage_before_sleep = np.random.choice(['High', 'Moderate', 'Low', 'None'], size=n_samples, p=[0.45, 0.30, 0.15, 0.10])
    anxiety_without_phone = np.random.choice(['High', 'Moderate', 'Low', 'None'], size=n_samples, p=[0.38, 0.35, 0.17, 0.10])
    checks_per_hour = np.random.poisson(lam=7.5, size=n_samples).clip(1, 30)
    impact_on_daily_life = np.random.choice(['High', 'Moderate', 'Low', 'None'], size=n_samples, p=[0.35, 0.35, 0.20, 0.10])
    time_without_checking_min = np.random.randint(5, 240, size=n_samples)
    
    # Calculate weighted addiction risk score
    anxiety_map = {'High': 3, 'Moderate': 2, 'Low': 1, 'None': 0}
    impact_map = {'High': 3, 'Moderate': 2, 'Low': 1, 'None': 0}
    sleep_map = {'High': 3, 'Moderate': 2, 'Low': 1, 'None': 0}
    
    anxiety_num = np.array([anxiety_map[x] for x in anxiety_without_phone])
    impact_num = np.array([impact_map[x] for x in impact_on_daily_life])
    sleep_num = np.array([sleep_map[x] for x in phone_usage_before_sleep])
    
    risk_score = (
        0.30 * daily_usage_hours + 
        0.25 * checks_per_hour + 
        0.8 * anxiety_num + 
        0.7 * impact_num + 
        0.6 * sleep_num - 
        0.01 * time_without_checking_min
    )
    
    p_addicted = 1 / (1 + np.exp(-(risk_score - 10) / 2.5))
    
    addiction_labels = []
    for p in p_addicted:
        r = np.random.rand()
        if r < p * 0.8:
            addiction_labels.append(1)
        elif r < p:
            addiction_labels.append(-1)
        else:
            addiction_labels.append(0)
            
    df = pd.DataFrame({
        'User_ID': [f'USR_{i+1000:05d}' for i in range(n_samples)],
        'Age': age,
        'Gender': genders,
        'Daily_Usage_Hours': daily_usage_hours,
        'Phone_Usage_Before_Sleep': phone_usage_before_sleep,
        'Anxiety_Without_Phone': anxiety_without_phone,
        'Checks_Per_Hour': checks_per_hour,
        'Impact_On_Daily_Life': impact_on_daily_life,
        'Time_Without_Checking_Phone_Min': time_without_checking_min,
        'Smartphone_Addiction': addiction_labels
    })
    
    return df

def generate_usage_sessions_dataset(survey_df, n_sessions=100000, random_state=42):
    """
    Generates high-frequency app usage session logs for SQL performance benchmarks.
    """
    np.random.seed(random_state)
    user_ids = survey_df['User_ID'].values
    
    categories = ['Social Media', 'Gaming', 'Messaging', 'Productivity', 'Entertainment', 'Shopping']
    apps = {
        'Social Media': ['Instagram', 'TikTok', 'X (Twitter)', 'Reddit'],
        'Gaming': ['PUBG Mobile', 'Subway Surfers', 'Candy Crush', 'Call of Duty'],
        'Messaging': ['WhatsApp', 'Telegram', 'Signal'],
        'Productivity': ['Notion', 'Google Docs', 'Slack', 'Gmail'],
        'Entertainment': ['YouTube', 'Netflix', 'Spotify'],
        'Shopping': ['Amazon', 'Flipkart', 'Myntra']
    }
    
    chosen_users = np.random.choice(user_ids, size=n_sessions)
    chosen_categories = np.random.choice(categories, size=n_sessions, p=[0.35, 0.20, 0.20, 0.05, 0.15, 0.05])
    chosen_apps = [np.random.choice(apps[cat]) for cat in chosen_categories]
    
    durations = np.random.exponential(scale=18.0, size=n_sessions).clip(1.0, 180.0).round(1)
    screen_unlocks = np.random.poisson(lam=3.0, size=n_sessions).clip(1, 15)
    
    dates = pd.date_range(end='2026-03-01', periods=90, freq='D')
    chosen_dates = np.random.choice(dates, size=n_sessions)
    hours = np.random.randint(0, 24, size=n_sessions)
    timestamps = [d + pd.Timedelta(hours=h, minutes=np.random.randint(0, 60)) for d, h in zip(chosen_dates, hours)]
    
    sessions_df = pd.DataFrame({
        'Session_ID': [f'SES_{i+100000:07d}' for i in range(n_sessions)],
        'User_ID': chosen_users,
        'App_Category': chosen_categories,
        'App_Name': chosen_apps,
        'Session_Duration_Min': durations,
        'Screen_Unlocks_In_Session': screen_unlocks,
        'Session_Timestamp': timestamps
    })
    
    return sessions_df

if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(data_dir, exist_ok=True)
    
    print("Generating survey dataset...")
    survey_df = generate_survey_dataset(n_samples=2500)
    survey_path = os.path.join(data_dir, 'smartphone_addiction_dataset.csv')
    survey_df.to_csv(survey_path, index=False)
    print(f"Saved survey dataset ({len(survey_df)} rows) to {survey_path}")
    
    print("Generating 100k+ session logs for SQL performance benchmarks...")
    sessions_df = generate_usage_sessions_dataset(survey_df, n_sessions=100000)
    sessions_path = os.path.join(data_dir, 'app_usage_sessions.csv')
    sessions_df.to_csv(sessions_path, index=False)
    print(f"Saved session logs dataset ({len(sessions_df)} rows) to {sessions_path}")

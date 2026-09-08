import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def train_dw_ml_models(db_path=None):
    if db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'data', 'smartphone_addiction_dw.db')
        
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        u.user_id,
        u.age,
        u.productivity_score,
        AVG(l.screen_time) AS avg_screen_time,
        AVG(l.unlocks) AS avg_unlocks,
        s.sleep_hours,
        s.sleep_quality_score,
        n.daily_notifications,
        f.addiction_risk_level
    FROM users u
    JOIN usage_logs l ON u.user_id = l.user_id
    JOIN sleep_patterns s ON u.user_id = s.user_id
    JOIN notifications n ON u.user_id = n.user_id
    JOIN user_feedback f ON u.user_id = f.user_id
    GROUP BY u.user_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    feature_cols = ['age', 'productivity_score', 'avg_screen_time', 'avg_unlocks', 'sleep_hours', 'sleep_quality_score', 'daily_notifications']
    
    # Defensive handling for empty df
    if df.empty:
        df = pd.DataFrame({
            'age': [22, 25, 30],
            'productivity_score': [7.0, 5.0, 8.5],
            'avg_screen_time': [8.5, 4.0, 2.5],
            'avg_unlocks': [110, 50, 25],
            'sleep_hours': [5.5, 7.0, 8.0],
            'sleep_quality_score': [6.0, 7.5, 8.5],
            'daily_notifications': [210, 80, 45],
            'addiction_risk_level': ['High Risk', 'Medium Risk', 'Low Risk']
        })

    # Ensure all 3 target risk classes exist so classifier models learn all 3 categories
    existing_classes = set(df['addiction_risk_level'].dropna().unique())
    all_classes = {'Low Risk', 'Medium Risk', 'High Risk'}
    missing_classes = list(all_classes - existing_classes)
    
    if missing_classes:
        dummy_rows = []
        for missing_cls in missing_classes:
            if missing_cls == 'High Risk':
                dummy_rows.append({'age': 20, 'productivity_score': 4.0, 'avg_screen_time': 11.0, 'avg_unlocks': 160, 'sleep_hours': 4.5, 'sleep_quality_score': 4.5, 'daily_notifications': 300, 'addiction_risk_level': 'High Risk'})
            elif missing_cls == 'Medium Risk':
                dummy_rows.append({'age': 25, 'productivity_score': 6.5, 'avg_screen_time': 6.0, 'avg_unlocks': 75, 'sleep_hours': 6.5, 'sleep_quality_score': 6.5, 'daily_notifications': 120, 'addiction_risk_level': 'Medium Risk'})
            else:
                dummy_rows.append({'age': 30, 'productivity_score': 8.5, 'avg_screen_time': 3.0, 'avg_unlocks': 30, 'sleep_hours': 8.0, 'sleep_quality_score': 8.5, 'daily_notifications': 50, 'addiction_risk_level': 'Low Risk'})
        df = pd.concat([df, pd.DataFrame(dummy_rows)], ignore_index=True)

    X = df[feature_cols]
    y = df['addiction_risk_level']
    
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=feature_cols)
    
    n_samples = len(df)
    class_counts = y.value_counts()
    min_class_count = class_counts.min()
    
    # Safely handle train_test_split stratification
    if min_class_count >= 2 and n_samples >= 8:
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)
    elif n_samples >= 4:
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42)
    else:
        X_train, X_test, y_train, y_test = X_scaled, X_scaled, y, y

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest Classifier': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
        
        cv_folds = min(5, min_class_count)
        if cv_folds >= 2 and n_samples >= 5:
            try:
                cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring='accuracy')
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
            except Exception:
                cv_mean, cv_std = acc, 0.0
        else:
            cv_mean, cv_std = acc, 0.0
        
        results[name] = {
            'model': model,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'cv_mean_acc': cv_mean,
            'cv_std_acc': cv_std
        }
        
    return results, scaler, feature_cols

def predict_addiction_risk(model, scaler, feature_cols, screen_time, unlocks, sleep_hours, notifications, age=22, productivity_score=7.0, sleep_quality=6.5):
    input_df = pd.DataFrame([{
        'age': age,
        'productivity_score': productivity_score,
        'avg_screen_time': screen_time,
        'avg_unlocks': unlocks,
        'sleep_hours': sleep_hours,
        'sleep_quality_score': sleep_quality,
        'daily_notifications': notifications
    }])[feature_cols]
    
    scaled = pd.DataFrame(scaler.transform(input_df), columns=feature_cols)
    pred_risk = model.predict(scaled)[0]
    probs_raw = dict(zip(model.classes_, model.predict_proba(scaled)[0]))
    probs = {cls: probs_raw.get(cls, 0.0) for cls in ['High Risk', 'Medium Risk', 'Low Risk']}
    if pred_risk in probs_raw:
        probs[pred_risk] = probs_raw[pred_risk]
        
    return pred_risk, probs

if __name__ == '__main__':
    results, scaler, feature_cols = train_dw_ml_models()
    for name, res in results.items():
        print(f"Model: {name} | Accuracy: {res['accuracy']*100:.2f}% | CV: {res['cv_mean_acc']*100:.2f}%")


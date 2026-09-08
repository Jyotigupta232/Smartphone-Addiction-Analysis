import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocessing import load_and_preprocess_data

def train_and_evaluate_models(data_path=None):
    if data_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, 'data', 'smartphone_addiction_dataset.csv')
        
    raw_df, encoded_df, X, X_scaled, y, scaler, feature_cols = load_and_preprocess_data(data_path)
    
    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'k-Nearest Neighbors (KNN)': KNeighborsClassifier(n_neighbors=7),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        # Fit model
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Performance metrics
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        # Cross validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
        cm = confusion_matrix(y_test, y_pred)
        
        # Feature importance if supported
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            feature_importance = dict(zip(feature_cols, np.abs(model.coef_[0])))
            
        results[name] = {
            'model_object': model,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'cv_mean_acc': cv_scores.mean(),
            'cv_std_acc': cv_scores.std(),
            'confusion_matrix': cm,
            'feature_importance': feature_importance,
            'y_test': y_test,
            'y_pred': y_pred
        }
        
    return results, X_scaled, y, feature_cols, scaler

if __name__ == '__main__':
    results, X_scaled, y, feature_cols, scaler = train_and_evaluate_models()
    print("="*60)
    print("        MACHINE LEARNING MODEL BENCHMARK RESULTS")
    print("="*60)
    for model_name, res in results.items():
        print(f"\nModel: {model_name}")
        print(f"  • Test Accuracy       : {res['accuracy']*100:.2f}%")
        print(f"  • 5-Fold Cross-Val Acc: {res['cv_mean_acc']*100:.2f}% (±{res['cv_std_acc']*100:.2f}%)")
        print(f"  • Weighted F1-Score   : {res['f1_score']:.4f}")

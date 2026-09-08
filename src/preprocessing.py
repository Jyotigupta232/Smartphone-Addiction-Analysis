import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

def load_and_preprocess_data(csv_path):
    """
    Loads survey dataset, cleans missing values, encodes ordinal/categorical features,
    and prepares feature matrix X and target vector y for ML models.
    """
    df = pd.read_csv(csv_path)
    
    # 1. Handle missing values (Imputation with mode for categorical, median for numeric)
    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=['object']).columns
    
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)
            
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mode()[0], inplace=True)
            
    # 2. Ordinal Mappings for Intensity Features
    intensity_mapping = {'None': 0, 'Low': 1, 'Moderate': 2, 'High': 3}
    
    encoded_df = df.copy()
    encoded_df['Phone_Usage_Before_Sleep_Enc'] = encoded_df['Phone_Usage_Before_Sleep'].map(intensity_mapping)
    encoded_df['Anxiety_Without_Phone_Enc'] = encoded_df['Anxiety_Without_Phone'].map(intensity_mapping)
    encoded_df['Impact_On_Daily_Life_Enc'] = encoded_df['Impact_On_Daily_Life'].map(intensity_mapping)
    
    # Gender One-Hot Encoding
    encoded_df = pd.get_dummies(encoded_df, columns=['Gender'], drop_first=True)
    
    # Define Feature matrix and Target
    feature_cols = [
        'Age', 'Daily_Usage_Hours', 'Checks_Per_Hour', 
        'Time_Without_Checking_Phone_Min', 'Phone_Usage_Before_Sleep_Enc',
        'Anxiety_Without_Phone_Enc', 'Impact_On_Daily_Life_Enc'
    ] + [c for c in encoded_df.columns if c.startswith('Gender_')]
    
    X = encoded_df[feature_cols]
    y = encoded_df['Smartphone_Addiction']
    
    # Scale Features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=feature_cols)
    
    raw_df = df
    return raw_df, encoded_df, X, X_scaled, y, scaler, feature_cols

if __name__ == '__main__':
    import os
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'smartphone_addiction_dataset.csv')
    if os.path.exists(dataset_path):
        raw_df, encoded_df, X, X_scaled, y, scaler, feature_cols = load_and_preprocess_data(dataset_path)
        print(f"Dataset successfully preprocessed! Feature shape: {X.shape}, Target distribution:\n{y.value_counts()}")

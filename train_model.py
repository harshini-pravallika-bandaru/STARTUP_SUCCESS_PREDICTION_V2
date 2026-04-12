# train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

FEATURES = [
    'linkedin_followers', 'timelapse_until_fifth_year', 'employees_on_linkedin',
    'twitter_followers', 'last_round_investors_count', 'last_raised_amount',
    'investor_count', 'lead_investor_count', 'total_funding_amount',
    'founders_count', 'round_count', 'facebook_followers',
    'founders_different_nationality', 'founders_entrepreneurial_background',
    'founders_male_count', 'founders_female_count', 'founders_degree',
    'trade_names_count', 'inventions_count', 'startup_age'
]

def generate_training_data():
    np.random.seed(42)
    successful = []
    for _ in range(232):
        successful.append({
            'linkedin_followers': np.random.randint(1000, 50000),
            'timelapse_until_fifth_year': np.random.uniform(1, 24),
            'employees_on_linkedin': np.random.randint(10, 500),
            'twitter_followers': np.random.randint(500, 30000),
            'last_round_investors_count': np.random.randint(1, 5),
            'last_raised_amount': np.random.uniform(500000, 10000000),
            'investor_count': np.random.randint(3, 20),
            'lead_investor_count': np.random.randint(1, 5),
            'total_funding_amount': np.random.uniform(1000000, 20000000),
            'founders_count': np.random.randint(2, 5),
            'round_count': np.random.randint(2, 6),
            'facebook_followers': np.random.randint(500, 20000),
            'founders_different_nationality': np.random.randint(1, 4),
            'founders_entrepreneurial_background': np.random.randint(1, 3),
            'founders_male_count': np.random.randint(1, 4),
            'founders_female_count': np.random.randint(0, 2),
            'founders_degree': np.random.randint(1, 3),
            'trade_names_count': np.random.randint(1, 5),
            'inventions_count': np.random.randint(0, 3),
            'startup_age': np.random.randint(1, 4),
            'success': 1
        })
    unsuccessful = []
    for _ in range(168):
        unsuccessful.append({
            'linkedin_followers': np.random.randint(0, 1000),
            'timelapse_until_fifth_year': np.random.uniform(24, 60),
            'employees_on_linkedin': np.random.randint(0, 20),
            'twitter_followers': np.random.randint(0, 500),
            'last_round_investors_count': np.random.randint(5, 15),
            'last_raised_amount': np.random.uniform(0, 500000),
            'investor_count': np.random.randint(0, 5),
            'lead_investor_count': np.random.randint(0, 2),
            'total_funding_amount': np.random.uniform(0, 1000000),
            'founders_count': np.random.randint(1, 3),
            'round_count': np.random.randint(0, 2),
            'facebook_followers': np.random.randint(0, 500),
            'founders_different_nationality': np.random.randint(0, 2),
            'founders_entrepreneurial_background': np.random.randint(0, 1),
            'founders_male_count': np.random.randint(1, 3),
            'founders_female_count': np.random.randint(0, 1),
            'founders_degree': np.random.randint(0, 2),
            'trade_names_count': np.random.randint(0, 2),
            'inventions_count': np.random.randint(0, 1),
            'startup_age': np.random.randint(1, 5),
            'success': 0
        })
    df = pd.DataFrame(successful + unsuccessful)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)

def train_and_save():
    print("Training Random Forest model...")
    df = generate_training_data()
    X = df[FEATURES]
    y = df['success']
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    model = RandomForestClassifier(n_estimators=100, max_depth=10,
                                   min_samples_split=5, min_samples_leaf=2,
                                   random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)
    joblib.dump(model, 'rf_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("Model saved as rf_model.pkl and scaler.pkl")

if __name__ == '__main__':
    train_and_save()
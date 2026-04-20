# train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

DATASET_PATH = "startup_training_data.xlsx"

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
    data = []

    for _ in range(500):
        row = {
            'linkedin_followers': np.random.randint(0, 20000),
            'timelapse_until_fifth_year': np.random.uniform(1, 60),
            'employees_on_linkedin': np.random.randint(1, 500),
            'twitter_followers': np.random.randint(0, 30000),
            'last_round_investors_count': np.random.randint(0, 15),
            'last_raised_amount': np.random.uniform(0, 10000000),
            'investor_count': np.random.randint(0, 20),
            'lead_investor_count': np.random.randint(0, 5),
            'total_funding_amount': np.random.uniform(0, 15000000),
            'founders_count': np.random.randint(1, 5),
            'round_count': np.random.randint(0, 6),
            'facebook_followers': np.random.randint(0, 20000),
            'founders_different_nationality': np.random.randint(0, 4),
            'founders_entrepreneurial_background': np.random.randint(0, 2),
            'founders_male_count': np.random.randint(0, 4),
            'founders_female_count': np.random.randint(0, 3),
            'founders_degree': np.random.randint(0, 2),
            'trade_names_count': np.random.randint(0, 5),
            'inventions_count': np.random.randint(0, 3),
            'startup_age': np.random.randint(1, 6),
        }

        # probabilistic success score (REALISTIC)
        score = (
            0.25 * (row['total_funding_amount'] / 15000000) +
            0.15 * (row['linkedin_followers'] / 20000) +
            0.15 * (row['employees_on_linkedin'] / 500) +
            0.10 * (row['investor_count'] / 20) +
            0.10 * (row['round_count'] / 6) +
            0.25 * np.random.rand()   # noise = KEY
        )

        row['success'] = 1 if score > 0.5 else 0
        data.append(row)

    df = pd.DataFrame(data)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)

def load_or_generate_data():
    if os.path.exists(DATASET_PATH):
        print("Loading existing dataset...")
        df = pd.read_excel(DATASET_PATH)
    else:
        print("Dataset not found. Generating new data (not saving to file)...")
        df = generate_training_data()
        df.to_excel(DATASET_PATH, index=False)
        print(f"Dataset saved at {DATASET_PATH}")

    return df

def feature_engineering(df):
    df['funding_per_employee'] = df['total_funding_amount'] / (df['employees_on_linkedin'] + 1)
    df['followers_per_age'] = df['linkedin_followers'] / (df['startup_age'] + 1)
    return df

def train_and_save():
    print("Training Random Forest model...")

    df = load_or_generate_data()
    df = feature_engineering(df)

    X = df[FEATURES + ['funding_per_employee', 'followers_per_age']]
    y = df['success']

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    # Train on train data only
    model.fit(X_train, y_train)

    # EVALUATION
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Accuracy: {accuracy:.2%}")
    print(classification_report(y_test, y_pred))

    # CROSS VALIDATION (REAL METRIC)
    cv_scores = cross_val_score(model, X_scaled, y, cv=5)
    print("\nCross Validation Accuracy:", f"{cv_scores.mean():.2%}")

    # saving the model
    joblib.dump(model, 'rf_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    print("\nModel saved as rf_model.pkl and scaler.pkl")

if __name__ == '__main__':
    train_and_save()

# prediction_engine.py
import joblib
import numpy as np
import os
import sys

_model = None
_scaler = None

def _train_and_save():
    """Dynamically import train_model and run training"""
    # Import here to avoid circular import
    from train_model import train_and_save
    train_and_save()

def _load():
    global _model, _scaler
    if _model is not None:
        return _model, _scaler

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'rf_model.pkl')
    scaler_path = os.path.join(base_dir, 'scaler.pkl')

    # If files don't exist or are corrupted, train them
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("Model files missing. Training now...")
        _train_and_save()

    try:
        _model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)
    except (EOFError, OSError, Exception) as e:
        print(f"Error loading model: {e}. Retraining...")
        _train_and_save()
        _model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)

    return _model, _scaler

def predict(startup_dict):
    """startup_dict: dict with keys matching the 20 features"""
    model, scaler = _load()

    # STEP 1: Extract base values
    linkedin_followers = startup_dict.get('linkedin_followers', 0)
    employees = startup_dict.get('employees_on_linkedin', 0)
    funding = startup_dict.get('total_funding_amount', 0)
    startup_age = startup_dict.get('startup_age', 0)

    # STEP 2: Feature engineering (ADD HERE)
    funding_per_employee = funding / (employees + 1)
    followers_per_age = linkedin_followers / (startup_age + 1)

    # STEP 3: Build full feature vector (22 features)
    features = [
        linkedin_followers,
        startup_dict.get('timelapse_until_fifth_year', 30.0),
        employees,
        startup_dict.get('twitter_followers', 0),
        startup_dict.get('last_round_investors_count', 0),
        startup_dict.get('last_raised_amount', 0.0),
        startup_dict.get('investor_count', 0),
        startup_dict.get('lead_investor_count', 0),
        funding,
        startup_dict.get('founders_count', 0),
        startup_dict.get('round_count', 0),
        startup_dict.get('facebook_followers', 0),
        startup_dict.get('founders_different_nationality', 0),
        startup_dict.get('founders_entrepreneurial_background', 0),
        startup_dict.get('founders_male_count', 0),
        startup_dict.get('founders_female_count', 0),
        startup_dict.get('founders_degree', 0),
        startup_dict.get('trade_names_count', 0),
        startup_dict.get('inventions_count', 0),
        startup_age,

        # engineered features at the END (same order as training)
        funding_per_employee,
        followers_per_age
    ]


    X = np.array(features).reshape(1, -1)
    X_scaled = scaler.transform(X)
    prob = model.predict_proba(X_scaled)[0][1]   # probability of success
    score = round(prob * 100, 1)

    # Grade
    if score >= 80: grade = 'A'
    elif score >= 70: grade = 'B'
    elif score >= 60: grade = 'C'
    elif score >= 50: grade = 'D'
    else: grade = 'F'

    # Cluster (simple rule-based)
    twitter = startup_dict.get('twitter_followers', 0)
    facebook = startup_dict.get('facebook_followers', 0)
    rounds = startup_dict.get('round_count', 0)
    funding = startup_dict.get('total_funding_amount', 0)
    if twitter > 10000 or facebook > 10000:
        cluster = 'HAS'
    elif rounds >= 3:
        cluster = 'HRS'
    elif funding > 5000000:
        cluster = 'HFS'
    else:
        cluster = 'HIL'

    explanation = f"Probability of success: {prob:.1%}. Score: {score}/100. Grade: {grade}. Cluster: {cluster}."
    recommendation = (
        "High investment potential." if score >= 75 else
        "Moderate potential – improve social media and funding." if score >= 60 else
        "Focus on LinkedIn presence and lead investors." if score >= 45 else
        "High risk – needs stronger social proof and funding traction."
    )

    return {
        'score': score,
        'grade': grade,
        'cluster': cluster,
        'explanation': explanation,
        'recommendation': recommendation
    }

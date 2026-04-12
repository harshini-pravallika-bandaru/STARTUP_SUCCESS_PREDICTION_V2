from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    contact_info = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False)  # 'startup' or 'investor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships (one-to-one)
    startup = db.relationship('Startup', backref='user', uselist=False, cascade='all, delete-orphan')
    investor = db.relationship('Investor', backref='user', uselist=False, cascade='all, delete-orphan')
    wallet_address = db.Column(db.String(100), nullable=True)  # store Ethereum address

class Startup(db.Model):
    __tablename__ = 'startups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    startup_name = db.Column(db.String(100), default='')
    industry_type = db.Column(db.String(50))
    founders_count = db.Column(db.Integer, default=0)
    founders_different_nationality = db.Column(db.Integer, default=0)
    founders_entrepreneurial_background = db.Column(db.Integer, default=0)
    founders_male_count = db.Column(db.Integer, default=0)
    founders_female_count = db.Column(db.Integer, default=0)
    founders_degree = db.Column(db.Integer, default=0)
    round_count = db.Column(db.Integer, default=0)
    investor_count = db.Column(db.Integer, default=0)
    lead_investor_count = db.Column(db.Integer, default=0)
    total_funding_amount = db.Column(db.Float, default=0.0)
    last_round_investors_count = db.Column(db.Integer, default=0)
    last_raised_amount = db.Column(db.Float, default=0.0)
    timelapse_until_fifth_year = db.Column(db.Float, default=0.0)
    facebook_followers = db.Column(db.Integer, default=0)
    twitter_followers = db.Column(db.Integer, default=0)
    linkedin_followers = db.Column(db.Integer, default=0)
    employees_on_linkedin = db.Column(db.Integer, default=0)
    trade_names_count = db.Column(db.Integer, default=0)
    inventions_count = db.Column(db.Integer, default=0)
    startup_age = db.Column(db.Integer, default=0)

    success_prediction_score = db.Column(db.Float)
    prediction_grade = db.Column(db.String(2))
    prediction_cluster = db.Column(db.String(10))
    prediction_explanation = db.Column(db.Text)
    prediction_recommendation = db.Column(db.Text)
    prediction_updated_at = db.Column(db.DateTime)

    total_invested_amount = db.Column(db.Float, default=0.0)
    total_investors = db.Column(db.Integer, default=0)

    investments = db.relationship('Investment', backref='startup', lazy=True)

class Investor(db.Model):
    __tablename__ = 'investors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    investor_name = db.Column(db.String(100))
    total_invested = db.Column(db.Float, default=0.0)
    investments = db.relationship('Investment', backref='investor', lazy=True)

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('investors.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    investment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='CONFIRMED')
    blockchain_tx_hash = db.Column(db.String(100), nullable=True)
    blockchain_synced = db.Column(db.Boolean, default=False)
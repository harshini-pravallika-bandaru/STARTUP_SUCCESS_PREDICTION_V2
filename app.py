from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Startup, Investor, Investment
from prediction_engine import predict
from werkzeug.security import generate_password_hash, check_password_hash
import os
import threading

# Import blockchain module (only if environment variables are set)
try:
    from blockchain import record_investment_on_chain
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    BLOCKCHAIN_AVAILABLE = False
    print(f"Blockchain import failed: {e}")
    print("Warning: blockchain.py not found or missing dependencies. Blockchain recording disabled.")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///startup_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------- Helper functions ----------
def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def get_current_user():
    return User.query.get(session.get('user_id'))

def async_record_investment(investment_id, startup_owner_address, startup_id, amount, notes):
    """Background thread to record investment on blockchain"""
    if not BLOCKCHAIN_AVAILABLE:
        return
    with app.app_context():
        inv = Investment.query.get(investment_id)
        if not inv:
            return
        tx_hash = record_investment_on_chain(startup_owner_address, startup_id, amount, notes)
        if tx_hash:
            inv.blockchain_tx_hash = tx_hash
            inv.blockchain_synced = True
        else:
            inv.blockchain_synced = False
        db.session.commit()

# ---------- Routes ----------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        contact = request.form['contact_info']
        password = request.form['password']
        confirm = request.form['confirm_password']
        role = request.form['role']
        wallet_address = request.form.get('wallet_address', '').strip()

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        user = User(email=email, contact_info=contact, password_hash=hashed, role=role,
                    wallet_address=wallet_address if wallet_address else None)
        db.session.add(user)
        db.session.flush()

        if role == 'startup':
            startup = Startup(user_id=user.id)
            db.session.add(startup)
        else:  # investor
            investor_name = request.form.get('investor_name', '')
            investor = Investor(user_id=user.id, investor_name=investor_name)
            db.session.add(investor)

        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/set_wallet', methods=['POST'])
@login_required()
def set_wallet():
    """Allow logged-in users to set/update their Ethereum wallet address"""
    wallet_address = request.form.get('wallet_address', '').strip()
    if not wallet_address:
        flash('Wallet address cannot be empty.', 'danger')
        return redirect(url_for('dashboard'))
    user = get_current_user()
    user.wallet_address = wallet_address
    db.session.commit()
    flash('Wallet address updated successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required()
def dashboard():
    role = session['role']
    if role == 'startup':
        return redirect(url_for('startup_dashboard'))
    else:
        return redirect(url_for('investor_dashboard'))

# ---------- Startup ----------
@app.route('/startup/dashboard')
@login_required(role='startup')
def startup_dashboard():
    current_user = get_current_user()          # rename to avoid confusion
    startup = Startup.query.filter_by(user_id=current_user.id).first()
    if not startup:
        flash('Startup profile not found.', 'danger')
        return redirect(url_for('logout'))

    investments = Investment.query.filter_by(startup_id=startup.id).order_by(Investment.investment_date.desc()).all()
    industries = [
        'B2B_SOFTWARE_AND_SERVICES', 'CONSUMER', 'HEALTHCARE', 'FINANCIAL',
        'EDUCATION', 'REAL_ESTATE_AND_CONSTRUCTION', 'INDUSTRIALS', 'GOVERNMENT', 'UNSPECIFIED'
    ]
    # Pass both 'startup' and 'user' (the current_user) to the template
    return render_template('startup_dashboard.html',
                           startup=startup,
                           investments=investments,
                           industries=industries,
                           user=current_user)

@app.route('/startup/update', methods=['POST'])
@login_required(role='startup')
def startup_update():
    user = get_current_user()
    startup = Startup.query.filter_by(user_id=user.id).first()
    if not startup:
        flash('Profile not found.', 'danger')
        return redirect(url_for('logout'))

    # Update all fields from form (same as before)
    startup.startup_name = request.form.get('startup_name', '')
    startup.industry_type = request.form.get('industry_type')
    startup.founders_count = int(request.form.get('founders_count', 0))
    startup.founders_different_nationality = int(request.form.get('founders_different_nationality', 0))
    startup.founders_entrepreneurial_background = int(request.form.get('founders_entrepreneurial_background', 0))
    startup.founders_male_count = int(request.form.get('founders_male_count', 0))
    startup.founders_female_count = int(request.form.get('founders_female_count', 0))
    startup.founders_degree = int(request.form.get('founders_degree', 0))
    startup.round_count = int(request.form.get('round_count', 0))
    startup.investor_count = int(request.form.get('investor_count', 0))
    startup.lead_investor_count = int(request.form.get('lead_investor_count', 0))
    startup.total_funding_amount = float(request.form.get('total_funding_amount', 0))
    startup.last_round_investors_count = int(request.form.get('last_round_investors_count', 0))
    startup.last_raised_amount = float(request.form.get('last_raised_amount', 0))
    startup.timelapse_until_fifth_year = float(request.form.get('timelapse_until_fifth_year', 0))
    startup.facebook_followers = int(request.form.get('facebook_followers', 0))
    startup.twitter_followers = int(request.form.get('twitter_followers', 0))
    startup.linkedin_followers = int(request.form.get('linkedin_followers', 0))
    startup.employees_on_linkedin = int(request.form.get('employees_on_linkedin', 0))
    startup.trade_names_count = int(request.form.get('trade_names_count', 0))
    startup.inventions_count = int(request.form.get('inventions_count', 0))
    startup.startup_age = int(request.form.get('startup_age', 0))

    # Run prediction
    startup_dict = {c.name: getattr(startup, c.name) for c in startup.__table__.columns}
    pred = predict(startup_dict)
    startup.success_prediction_score = pred['score']
    startup.prediction_grade = pred['grade']
    startup.prediction_cluster = pred['cluster']
    startup.prediction_explanation = pred['explanation']
    startup.prediction_recommendation = pred['recommendation']
    startup.prediction_updated_at = db.func.current_timestamp()

    db.session.commit()
    flash('Profile updated and prediction recalculated.', 'success')
    return redirect(url_for('startup_dashboard'))

# ---------- Investor ----------
@app.route('/investor/dashboard')
@login_required(role='investor')
def investor_dashboard():
    user = get_current_user()
    investor = Investor.query.filter_by(user_id=user.id).first()
    if not investor:
        flash('Investor profile not found.', 'danger')
        return redirect(url_for('logout'))

    industry = request.args.get('industry')
    if industry:
        most_invested = db.session.query(Startup).filter(Startup.industry_type == industry).order_by(Startup.total_invested_amount.desc()).all()
        highest_pred = db.session.query(Startup).filter(Startup.industry_type == industry).filter(Startup.success_prediction_score.isnot(None)).order_by(Startup.success_prediction_score.desc()).all()
    else:
        most_invested = Startup.query.order_by(Startup.total_invested_amount.desc()).all()
        highest_pred = Startup.query.filter(Startup.success_prediction_score.isnot(None)).order_by(Startup.success_prediction_score.desc()).all()

    industries = [
        'B2B_SOFTWARE_AND_SERVICES', 'CONSUMER', 'HEALTHCARE', 'FINANCIAL',
        'EDUCATION', 'REAL_ESTATE_AND_CONSTRUCTION', 'INDUSTRIALS', 'GOVERNMENT', 'UNSPECIFIED'
    ]
    return render_template('investor_dashboard.html', investor=investor, most_invested=most_invested,
                           highest_pred=highest_pred, industries=industries, selected_industry=industry)

@app.route('/invest', methods=['POST'])
@login_required(role='investor')
def invest():
    startup_id = request.form.get('startup_id')
    amount = float(request.form.get('amount', 0))
    notes = request.form.get('notes', '')

    if amount <= 0:
        flash('Amount must be positive.', 'danger')
        return redirect(url_for('investor_dashboard'))

    user = get_current_user()
    investor = Investor.query.filter_by(user_id=user.id).first()
    startup = Startup.query.get(startup_id)

    if not startup or not investor:
        flash('Invalid investment.', 'danger')
        return redirect(url_for('investor_dashboard'))

    # Create investment record
    inv = Investment(startup_id=startup.id, investor_id=investor.id, amount=amount, notes=notes,
                     blockchain_synced=False)  # default
    db.session.add(inv)

    # Update totals
    startup.total_invested_amount = (startup.total_invested_amount or 0) + amount
    startup.total_investors = (startup.total_investors or 0) + 1
    investor.total_invested = (investor.total_invested or 0) + amount

    db.session.commit()

    # Blockchain recording in background
    if BLOCKCHAIN_AVAILABLE:
        startup_owner = User.query.get(startup.user_id)
        if startup_owner and startup_owner.wallet_address:
            thread = threading.Thread(
                target=async_record_investment,
                args=(inv.id, startup_owner.wallet_address, startup.id, amount, notes)
            )
            thread.start()
            flash(f'Successfully invested ${amount:,.2f} in {startup.startup_name}. Blockchain recording started.', 'success')
        else:
            flash(f'Successfully invested ${amount:,.2f} in {startup.startup_name}. No wallet address set for startup, blockchain recording skipped.', 'warning')
    else:
        flash(f'Successfully invested ${amount:,.2f} in {startup.startup_name}. Blockchain service not available.', 'info')

    return redirect(url_for('investor_dashboard'))

# ---------- Run ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
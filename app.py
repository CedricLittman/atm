
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_migrate import Migrate

# Initialize Flask application
app = Flask(__name__)

# Configure secret key for session security
# os.urandom generates a cryptographically secure random key
app.config['SECRET_KEY'] = os.urandom(24)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Define User model for database
# Represents user accounts with authentication and balance information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
    username = db.Column(db.String(50), unique=True, nullable=False)  # Unique username
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    balance = db.Column(db.Float, default=0.0)  # User's account balance
    transactions = db.relationship('Transaction', backref='user', lazy=True)  # Link to user's transactions

# Define Transaction model to track all financial activities
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique transaction identifier
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to user
    type = db.Column(db.String(10), nullable=False)  # Transaction type (deposit/withdraw/transfer)
    amount = db.Column(db.Float, nullable=False)  # Transaction amount
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # When transaction occurred
    recipient_username = db.Column(db.String(50), nullable=True)  # For transfers, the recipient's username
    sender_username = db.Column(db.String(50), nullable=True)


# Home route - main dashboard after login
@app.route('/')
def index():
    # Redirect to login if no user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch user details for the dashboard
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect registration form data
        username = request.form['username']
        password = request.form['password']
        initial_balance = float(request.form.get('initial_balance', 0))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        # Hash password for secure storage
        hashed_password = generate_password_hash(password)
        
        # Create new user account
        new_user = User(username=username, password=hashed_password, balance=initial_balance)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate user credentials
        username = request.form['username']
        password = request.form['password']

        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check password using secure hash comparison
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Create user session
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

# Logout route to end user session
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user from session
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Deposit money route
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process deposit transaction
        amount = float(request.form['amount'])
        
        # Validate deposit amount
        if amount <= 0:
            flash('Invalid deposit amount', 'error')
            return redirect(url_for('deposit'))

        # Update user balance
        user = User.query.get(session['user_id'])
        user.balance += amount

        # Record transaction in database
        transaction = Transaction(user_id=user.id, type='deposit', amount=amount)
        db.session.add(transaction)
        db.session.commit()

        flash(f'Successfully deposited ${amount:.2f}', 'success')
        return redirect(url_for('index'))

    return render_template('deposit.html')

# Withdraw money route
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process withdrawal transaction
        amount = float(request.form['amount'])
        user = User.query.get(session['user_id'])

        # Validate withdrawal amount
        if amount <= 0:
            flash('Invalid withdrawal amount', 'error')
            return redirect(url_for('withdraw'))

        # Check sufficient funds
        if amount > user.balance:
            flash('Insufficient funds', 'error')
            return redirect(url_for('withdraw'))

        # Update user balance
        user.balance -= amount

        # Record transaction in database
        transaction = Transaction(user_id=user.id, type='withdraw', amount=amount)
        db.session.add(transaction)
        db.session.commit()

        flash(f'Successfully withdrew ${amount:.2f}', 'success')
        return redirect(url_for('index'))

    return render_template('withdraw.html')

# Transaction history route
@app.route('/transactions')
def transactions():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch user's transactions, most recent first
    user = User.query.get(session['user_id'])
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc()).all()
    return render_template('transactions.html', transactions=transactions)

# Money transfer route
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process money transfer
        recipient_username = request.form['recipient']
        amount = float(request.form['amount'])

        # Find sender and recipient
        sender = User.query.get(session['user_id'])
        recipient = User.query.filter_by(username=recipient_username).first()

        # Validate transfer details
        if not recipient:
            flash('Recipient not found', 'error')
            return redirect(url_for('transfer'))

        if amount <= 0:
            flash('Invalid transfer amount', 'error')
            return redirect(url_for('transfer'))

        if amount > sender.balance:
            flash('Insufficient funds', 'error')
            return redirect(url_for('transfer'))

        # Perform transfer by updating balances
        sender.balance -= amount
        recipient.balance += amount

        # Record transactions for both sender and recipient
        sender_transaction = Transaction(
            user_id=sender.id, 
            type='transfer_out', 
            amount=amount,
            sender_username=sender.username  # Record the sender's username
        )
        
        recipient_transaction = Transaction(
            user_id=recipient.id,
            type='transfer_in',
            amount=amount,
            recipient_username=sender.username  # Store the sender's username for the recipient transaction
        )

        db.session.add_all([sender_transaction, recipient_transaction])
        db.session.commit()

        flash(f'Successfully transferred ${amount:.2f} to {recipient_username}', 'success')
        return redirect(url_for('index'))

    return render_template('transfer.html')




# Main application entry point
if __name__ == '__main__':
    # Create database tables before running the app
    with app.app_context():
        db.create_all()
    # Run the Flask development server
    app.run(debug=True)
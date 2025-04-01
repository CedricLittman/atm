# create_user.py - Module for creating new users

from werkzeug.security import generate_password_hash
from flask import flash

def create_user(db, User, username, password, initial_balance=0.0):
    """
    Create a new user in the ATM system database
    
    Args:
        db: SQLAlchemy database instance
        User: User model class
        username (str): Unique username for the new user
        password (str): Password for the new user (will be hashed)
        initial_balance (float, optional): Initial account balance. Defaults to 0.0.
        
    Returns:
        tuple: (bool, str or User) - Success status and either error message or User object
    """
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return False, "Username already exists"
        
    try:
        # Hash password for secure storage
        hashed_password = generate_password_hash(password)
        
        # Create new user account
        new_user = User(
            username=username, 
            password=hashed_password, 
            balance=float(initial_balance)
        )
        
        # Add and commit to database
        db.session.add(new_user)
        db.session.commit()
        
        print(f"User '{username}' created successfully with ID: {new_user.id}")
        return True, new_user
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating user: {str(e)}"


# Example usage
if __name__ == "__main__":
    from app import app, db, User
    
    with app.app_context():
        success, result = create_user(db, User, "new_user", "password123", 1000.0)
        
        if success:
            print(f"Created user: {result.username} with balance: ${result.balance}")
        else:
            print(f"Failed to create user: {result}")
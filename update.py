# update_user.py - Module for updating user information

from werkzeug.security import generate_password_hash

def update_user(db, User, user_id, **kwargs):
    """
    Update user information in the ATM system
    
    Args:
        db: SQLAlchemy database instance
        User: User model class
        user_id (int): ID of the user to update
        **kwargs: Fields to update (username, password, balance)
            - username (str): New username
            - password (str): New password (will be hashed)
            - balance (float): New account balance
            
    Returns:
        tuple: (bool, str or User) - Success status and either error message or updated User object
    """
    user = User.query.get(user_id)
    
    if not user:
        return False, "User not found"
        
    try:
        changes_made = False
        
        # Update username if provided
        if 'username' in kwargs:
            new_username = kwargs['username']
            # Check if new username is already taken by another user
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != user_id:
                return False, "Username already exists"
            
            old_username = user.username
            user.username = new_username
            changes_made = True
            print(f"Username changed from '{old_username}' to '{new_username}'")
            
        # Update password if provided
        if 'password' in kwargs:
            user.password = generate_password_hash(kwargs['password'])
            changes_made = True
            print("Password updated successfully")
            
        # Update balance if provided
        if 'balance' in kwargs:
            old_balance = user.balance
            user.balance = float(kwargs['balance'])
            changes_made = True
            print(f"Balance updated from ${old_balance:.2f} to ${user.balance:.2f}")
        
        if not changes_made:
            return False, "No changes specified"
            
        db.session.commit()
        return True, user
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating user: {str(e)}"


# Example usage
if __name__ == "__main__":
    from app import app, db, User
    
    with app.app_context():
        # Example 1: Update username
        print("Example 1: Updating username")
        success, result = update_user(db, User, 1, username="new_username")
        
        if success:
            print(f"User updated successfully. New username: {result.username}")
        else:
            print(f"Failed to update user: {result}")
            
        # Example 2: Update password
        print("\nExample 2: Updating password")
        success, result = update_user(db, User, 1, password="new_secure_password")
        
        if success:
            print("Password updated successfully")
        else:
            print(f"Failed to update password: {result}")
            
        # Example 3: Update balance
        print("\nExample 3: Updating balance")
        success, result = update_user(db, User, 1, balance=2500.0)
        
        if success:
            print(f"Balance updated successfully. New balance: ${result.balance:.2f}")
        else:
            print(f"Failed to update balance: {result}")
            
        # Example 4: Update multiple fields
        print("\nExample 4: Updating multiple fields")
        success, result = update_user(
            db, User, 1, 
            username="complete_update",
            password="multi_update_pwd",
            balance=3000.0
        )
        
        if success:
            print(f"Multiple fields updated successfully for user: {result.username}")
        else:
            print(f"Failed to update multiple fields: {result}")
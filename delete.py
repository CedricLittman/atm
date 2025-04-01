# delete_user.py - Module for deleting users

def delete_user(db, User, Transaction, user_id):
    """
    Delete a user and their associated transactions from the ATM system
    
    Args:
        db: SQLAlchemy database instance
        User: User model class
        Transaction: Transaction model class
        user_id (int): ID of the user to delete
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    user = User.query.get(user_id)
    
    if not user:
        return False, "User not found"
        
    try:
        username = user.username
        
        # Delete all transactions associated with this user
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        transaction_count = len(transactions)
        
        for transaction in transactions:
            db.session.delete(transaction)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return True, f"User '{username}' and {transaction_count} associated transactions deleted successfully"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting user: {str(e)}"


# Example usage
if __name__ == "__main__":
    from app import app, db, User, Transaction
    
    with app.app_context():
        # Deleting a user by ID
        user_id_to_delete = 2  # Change this to a valid user ID in your database
        
        # Get user information before deletion
        user = User.query.get(user_id_to_delete)
        if user:
            print(f"Attempting to delete user: {user.username} (ID: {user.id})")
            
            # Delete the user
            success, message = delete_user(db, User, Transaction, user_id_to_delete)
            
            if success:
                print(f"Success: {message}")
            else:
                print(f"Failed: {message}")
        else:
            print(f"User with ID {user_id_to_delete} not found")
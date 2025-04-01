# read_user.py - Module for retrieving user information

def get_user_by_id(User, user_id):
    """
    Retrieve a user by their ID
    
    Args:
        User: User model class
        user_id (int): The ID of the user to retrieve
        
    Returns:
        User or None: The user object if found, None otherwise
    """
    return User.query.get(user_id)


def get_user_by_username(User, username):
    """
    Retrieve a user by their username
    
    Args:
        User: User model class
        username (str): The username to search for
        
    Returns:
        User or None: The user object if found, None otherwise
    """
    return User.query.filter_by(username=username).first()


def get_all_users(User):
    """
    Retrieve all users from the database
    
    Args:
        User: User model class
        
    Returns:
        list: List of all user objects
    """
    return User.query.all()


def print_user_info(user):
    """
    Print formatted user information
    
    Args:
        user: User object to display
    """
    if user:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Balance: ${user.balance:.2f}")
        print(f"Number of transactions: {len(user.transactions)}")
    else:
        print("User not found")


# Example usage
if __name__ == "__main__":
    from app import app, db, User
    
    with app.app_context():
        print("Finding user by ID:")
        user = get_user_by_id(User, 1)
        print_user_info(user)
        
        print("\nFinding user by username:")
        user = get_user_by_username(User, "admin")
        print_user_info(user)
        
        print("\nListing all users:")
        users = get_all_users(User)
        print(f"Total users: {len(users)}")
        
        for i, user in enumerate(users, 1):
            print(f"\nUser {i}:")
            print_user_info(user)
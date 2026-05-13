"""
Authentication service for Smart Inventory Management System
"""
from flask_login import login_user, logout_user
from extensions import db
from models.user import User

class AuthenticationService:
    """Service class for handling authentication operations"""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, role='customer'):
        """
        Register a new user with validation
        
        Args:
            email (str): User's email address
            password (str): User's password
            first_name (str): User's first name
            last_name (str): User's last name
            role (str): User's role (customer or admin)
        
        Returns:
            tuple: (success: bool, user: User|None, error_message: str|None)
        """
        try:
            # Check if user already exists
            existing_user = User.get_by_email(email)
            if existing_user:
                return False, None, "A user with this email address already exists"
            
            # Create new user with validation
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Set password (includes validation)
            user.set_password(password)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            return True, user, None
            
        except ValueError as e:
            # Validation error
            return False, None, str(e)
        except Exception as e:
            # Database or other error
            db.session.rollback()
            return False, None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password
        
        Args:
            email (str): User's email address
            password (str): User's password
        
        Returns:
            tuple: (success: bool, user: User|None, error_message: str|None)
        """
        try:
            # Validate input
            if not email or not password:
                return False, None, "Email and password are required"
            
            # Find user by email
            user = User.get_by_email(email)
            if not user:
                return False, None, "Invalid email or password"
            
            # Check if user is active
            if not user.is_active:
                return False, None, "Account is deactivated. Please contact administrator."
            
            # Verify password
            if not user.check_password(password):
                return False, None, "Invalid email or password"
            
            return True, user, None
            
        except Exception as e:
            return False, None, f"Authentication failed: {str(e)}"
    
    @staticmethod
    def login_user_session(user, remember=False):
        """
        Log in user and create session
        
        Args:
            user (User): User object to log in
            remember (bool): Whether to remember the user
        
        Returns:
            bool: Success status
        """
        try:
            # Update last login timestamp
            user.update_last_login()
            
            # Create Flask-Login session
            login_user(user, remember=remember)
            
            return True
            
        except Exception as e:
            print(f"Login session creation failed: {e}")
            return False
    
    @staticmethod
    def logout_user_session():
        """
        Log out current user and clear session
        
        Returns:
            bool: Success status
        """
        try:
            logout_user()
            return True
        except Exception as e:
            print(f"Logout failed: {e}")
            return False
    
    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email address
        
        Args:
            email (str): User's email address
        
        Returns:
            User|None: User object or None if not found
        """
        try:
            return User.get_by_email(email)
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User's ID
        
        Returns:
            User|None: User object or None if not found
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """
        Change user's password
        
        Args:
            user (User): User object
            current_password (str): Current password
            new_password (str): New password
        
        Returns:
            tuple: (success: bool, error_message: str|None)
        """
        try:
            # Verify current password
            if not user.check_password(current_password):
                return False, "Current password is incorrect"
            
            # Set new password (includes validation)
            user.set_password(new_password)
            
            # Save to database
            db.session.commit()
            
            return True, None
            
        except ValueError as e:
            # Validation error
            return False, str(e)
        except Exception as e:
            # Database or other error
            db.session.rollback()
            return False, f"Password change failed: {str(e)}"
    
    @staticmethod
    def update_user_profile(user, first_name=None, last_name=None):
        """
        Update user profile information
        
        Args:
            user (User): User object
            first_name (str, optional): New first name
            last_name (str, optional): New last name
        
        Returns:
            tuple: (success: bool, error_message: str|None)
        """
        try:
            # Update fields if provided
            if first_name is not None:
                user.first_name = User.validate_name(first_name, "First name")
            
            if last_name is not None:
                user.last_name = User.validate_name(last_name, "Last name")
            
            # Save to database
            db.session.commit()
            
            return True, None
            
        except ValueError as e:
            # Validation error
            return False, str(e)
        except Exception as e:
            # Database or other error
            db.session.rollback()
            return False, f"Profile update failed: {str(e)}"
    
    @staticmethod
    def deactivate_user(user):
        """
        Deactivate user account
        
        Args:
            user (User): User object to deactivate
        
        Returns:
            tuple: (success: bool, error_message: str|None)
        """
        try:
            user.is_active = False
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"User deactivation failed: {str(e)}"
    
    @staticmethod
    def activate_user(user):
        """
        Activate user account
        
        Args:
            user (User): User object to activate
        
        Returns:
            tuple: (success: bool, error_message: str|None)
        """
        try:
            user.is_active = True
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"User activation failed: {str(e)}"
    
    @staticmethod
    def get_user_statistics():
        """
        Get user statistics for admin dashboard
        
        Returns:
            dict: User statistics
        """
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            customers = User.query.filter_by(role=User.ROLE_CUSTOMER, is_active=True).count()
            admins = User.query.filter_by(role=User.ROLE_ADMIN, is_active=True).count()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'customers': customers,
                'admins': admins,
                'inactive_users': total_users - active_users
            }
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'customers': 0,
                'admins': 0,
                'inactive_users': 0
            }
    
    @staticmethod
    def require_role(required_role):
        """
        Decorator to require specific user role
        
        Args:
            required_role (str): Required role ('admin' or 'customer')
        
        Returns:
            function: Decorator function
        """
        def decorator(f):
            from functools import wraps
            from flask_login import current_user
            from flask import abort
            
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(401)  # Unauthorized
                
                if current_user.role != required_role:
                    abort(403)  # Forbidden
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    @staticmethod
    def require_admin(f):
        """
        Decorator to require admin role
        
        Args:
            f (function): Function to decorate
        
        Returns:
            function: Decorated function
        """
        return AuthenticationService.require_role(User.ROLE_ADMIN)(f)
    
    @staticmethod
    def require_customer(f):
        """
        Decorator to require customer role
        
        Args:
            f (function): Function to decorate
        
        Returns:
            function: Decorated function
        """
        return AuthenticationService.require_role(User.ROLE_CUSTOMER)(f)
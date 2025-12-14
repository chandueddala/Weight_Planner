"""
Authentication Module for Weight Planner
Supports local authentication with bcrypt password hashing.
Can be extended to support AWS Cognito integration.
"""
import os
import re
import uuid
import logging
import bcrypt
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Import user store functions
from .user_store import get_user_by_email, get_or_create_user, update_user_profile


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, ""


def sanitize_username(text: str) -> str:
    """
    Sanitize text for username (alphanumeric and underscores only).
    
    Args:
        text: Input text
        
    Returns:
        Sanitized username
    """
    # Remove special characters, keep only alphanumeric and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', text)
    return sanitized.lower()


def generate_unique_username(full_name: str, email: str) -> str:
    """
    Generate a unique username from full name or email.
    
    Args:
        full_name: User's full name
        email: User's email address
        
    Returns:
        Unique username
    """
    from .user_store import check_username_exists
    
    # Try to use name first
    base_username = sanitize_username(full_name.replace(' ', ''))
    
    # If name is too short or empty, use email prefix
    if len(base_username) < 3:
        email_prefix = email.split('@')[0]
        base_username = sanitize_username(email_prefix)
    
    # Ensure minimum length
    min_length = int(os.getenv('MIN_USERNAME_LENGTH', '3'))
    max_length = int(os.getenv('MAX_USERNAME_LENGTH', '20'))
    
    if len(base_username) < min_length:
        base_username = base_username + str(uuid.uuid4().hex[:min_length - len(base_username)])
    
    # Truncate if too long
    base_username = base_username[:max_length - 4]  # Reserve 4 chars for suffix
    
    # Check uniqueness and append number if needed
    username = base_username
    attempt = 0
    
    while check_username_exists(username):
        attempt += 1
        suffix = str(attempt).zfill(3)
        username = base_username[:max_length - len(suffix)] + suffix
        
        # Safety check - max 1000 attempts
        if attempt > 999:
            username = base_username + uuid.uuid4().hex[:4]
            break
    
    logger.info(f"Generated unique username: {username}")
    return username


def signup_user(email: str, password: str, full_name: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Register a new user with local authentication.
    
    Args:
        email: User's email address
        password: Plain text password
        full_name: User's full name
        
    Returns:
        Tuple of (success, message, user_data)
    """
    try:
        # Validate email
        if not validate_email(email):
            return False, "Invalid email format", None
        
        # Validate password
        is_valid_pwd, pwd_error = validate_password(password)
        if not is_valid_pwd:
            return False, pwd_error, None
        
        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return False, "Email already registered", None
        
        # Generate unique username
        username = generate_unique_username(full_name, email)
        
        # Hash password
        hashed_pwd = hash_password(password)
        
        # Generate unique user_id
        user_id = str(uuid.uuid4())
        
        # Get starting credits from environment
        starting_credits = int(os.getenv('DEFAULT_STARTING_CREDITS', '20'))
        
        # Create user in DynamoDB
        user = get_or_create_user(
            user_id=user_id,
            email=email,
            starting_credits=starting_credits
        )
        
        # Update user with additional fields
        update_user_profile(
            user_id=user_id,
            full_name=full_name,
            username=username,
            password_hash=hashed_pwd,
            auth_provider="local",
            email_verified=True,  # Email validation only, no verification needed
            onboarding_completed=False
        )

        logger.info(f"User signup successful: {email} (username: {username})")

        # Return user data
        user_data = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "username": username,
            "credits_remaining": starting_credits,
            "onboarding_completed": False,
            "email_verified": True
        }

        return True, f"Account created successfully! Your username is: {username}", user_data
        
    except Exception as e:
        logger.error(f"Signup error for {email}: {str(e)}")
        return False, f"Signup failed: {str(e)}", None


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate user with email and password.

    Args:
        email: User's email address
        password: Plain text password

    Returns:
        Tuple of (success, message, user_data)
    """
    try:
        # Get user by email
        user = get_user_by_email(email)

        if not user:
            return False, "We couldn't find an account with this email address. Please check your email or sign up to create a new account.", None

        # Verify password
        stored_hash = user.get('password_hash', '')

        if not stored_hash:
            return False, "This account is not configured for password login. Please contact support for assistance.", None

        if not verify_password(password, stored_hash):
            return False, "The password you entered is incorrect. Please try again or reset your password.", None
        
        # Update last login
        from .user_store import update_user_profile
        update_user_profile(
            user_id=user['user_id'],
            last_login=datetime.now(timezone.utc).isoformat()
        )
        
        logger.info(f"User login successful: {email}")

        # Check email verification status
        email_verified = user.get('email_verified', False)

        # Return user data
        user_data = {
            "user_id": user['user_id'],
            "email": user['email'],
            "full_name": user.get('full_name', ''),
            "username": user.get('username', ''),
            "credits_remaining": int(user.get('credits_remaining', 0)),
            "onboarding_completed": user.get('onboarding_completed', False),
            "email_verified": email_verified
        }

        return True, "Login successful!", user_data
        
    except Exception as e:
        logger.error(f"Login error for {email}: {str(e)}")
        return False, f"Login failed: {str(e)}", None


def get_current_user(session_state) -> Optional[Dict]:
    """
    Get currently authenticated user from session state.
    
    Args:
        session_state: Streamlit session state
        
    Returns:
        User data dict or None if not authenticated
    """
    if hasattr(session_state, 'authenticated') and session_state.authenticated:
        return {
            "user_id": session_state.user_id,
            "email": session_state.email,
            "full_name": session_state.get('full_name', ''),
            "username": session_state.get('username', ''),
            "credits_remaining": session_state.get('credits_remaining', 0)
        }
    return None


def logout_user(session_state):
    """
    Log out the current user by clearing session state.
    
    Args:
        session_state: Streamlit session state
    """
    # Clear authentication-related session state
    if hasattr(session_state, 'authenticated'):
        session_state.authenticated = False
    if hasattr(session_state, 'user_id'):
        del session_state.user_id
    if hasattr(session_state, 'email'):
        del session_state.email
    if hasattr(session_state, 'full_name'):
        del session_state.full_name
    if hasattr(session_state, 'username'):
        del session_state.username
    if hasattr(session_state, 'credits_remaining'):
        del session_state.credits_remaining
    
    logger.info("User logged out")

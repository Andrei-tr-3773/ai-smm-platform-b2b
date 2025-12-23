"""Authentication utilities for user login and session management."""
import bcrypt
import jwt
import os
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional
from models.user import User
from repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-PLEASE")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        password: Plain text password
        hashed: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def create_jwt_token(user_id: str, email: str) -> str:
    """
    Create JWT token for user session.

    Args:
        user_id: User ID
        email: User email

    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }

    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"JWT token creation failed: {e}")
        raise


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def get_current_user() -> Optional[User]:
    """
    Get current logged-in user from session.

    Returns:
        User object or None if not logged in
    """
    # Check if auth token exists in session
    if 'auth_token' not in st.session_state:
        return None

    # Verify token
    token_data = verify_jwt_token(st.session_state['auth_token'])
    if not token_data:
        # Token invalid or expired, clear session
        clear_session()
        return None

    # Get user from database
    try:
        repo = UserRepository()
        user = repo.get_user_by_id(token_data['user_id'])

        if not user:
            # User deleted, clear session
            clear_session()
            return None

        return user
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        return None


def require_auth() -> User:
    """
    Decorator/function to require authentication for a page.

    Returns:
        User object if authenticated

    Raises:
        Redirects to login page if not authenticated
    """
    user = get_current_user()

    if not user:
        st.error("🔒 Please log in to access this page")

        # Show login button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Login", type="primary", use_container_width=True):
                st.switch_page("pages/02_Login.py")

        st.stop()

    return user


def create_session(user: User):
    """
    Create user session after successful login.

    Args:
        user: User object
    """
    # Create JWT token
    token = create_jwt_token(str(user.id), user.email)

    # Store in session
    st.session_state['auth_token'] = token
    st.session_state['user_id'] = str(user.id)
    st.session_state['user_email'] = user.email
    st.session_state['user_name'] = user.name
    st.session_state['workspace_id'] = user.workspace_id
    st.session_state['user_role'] = user.role

    # Update last login
    try:
        repo = UserRepository()
        repo.update_last_login(str(user.id))
    except Exception as e:
        logger.error(f"Failed to update last login: {e}")

    logger.info(f"Session created for user: {user.email}")


def clear_session():
    """Clear user session (logout)."""
    # Clear all auth-related session keys
    keys_to_clear = [
        'auth_token', 'user_id', 'user_email', 'user_name',
        'workspace_id', 'user_role'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    logger.info("Session cleared")


def is_authenticated() -> bool:
    """
    Check if user is authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return get_current_user() is not None


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least 1 uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least 1 lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least 1 number")

    # Optional: Check for special characters (recommended for Week 7)
    # special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # if not any(c in special_chars for c in password):
    #     errors.append("Password must contain at least 1 special character")

    return (len(errors) == 0, errors)


def check_user_role(user: User, required_role: str) -> bool:
    """
    Check if user has required role.

    Args:
        user: User object
        required_role: Required role (owner, admin, member)

    Returns:
        True if user has role, False otherwise
    """
    role_hierarchy = {
        'owner': 3,
        'admin': 2,
        'member': 1
    }

    user_level = role_hierarchy.get(user.role, 0)
    required_level = role_hierarchy.get(required_role, 0)

    return user_level >= required_level

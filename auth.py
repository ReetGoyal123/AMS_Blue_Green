"""
Authentication module
"""
import hashlib
import re
from db import create_user, get_user_by_username

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

def signup_user(username, email, password, role="student"):
    is_valid, message = validate_username(username)
    if not is_valid:
        return False, message
    if not validate_email(email):
        return False, "Invalid email format"
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    return create_user(username, email, hash_password(password), role)

def login_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return False, None, "Invalid username or password"
    if not verify_password(password, user['password_hash']):
        return False, None, "Invalid username or password"
    return True, user, "Login successful"

def logout_user(session_state):
    session_state.authenticated = False
    session_state.user_id = None
    session_state.username = None
    session_state.email = None
    session_state.role = None
    session_state.page = 'login'
    session_state.login_role = None
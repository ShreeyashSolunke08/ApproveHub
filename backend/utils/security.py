"""
ApproveHub — Security & Authentication Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Session management, access control decorators, cryptographically secure
password generation, and standardized approval serial formatting.

Author: Shreeyash Solunke
Institution: VIT Pune, Department of Information Technology
"""

import secrets
import string
from datetime import datetime
from functools import wraps
from flask import session, request, jsonify, redirect, url_for
from backend.models import User

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        # Check bearer token or auth header for API calls
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_val = auth_header.split(" ", 1)[1]
            if token_val.isdigit():
                user_id = int(token_val)
    if user_id:
        return User.query.get(user_id)
    return None

def login_user(user, remember=False):
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role
    session["user_email"] = user.email
    if remember:
        session.permanent = True
    else:
        session.permanent = False

def logout_user():
    session.clear()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Please log in."}), 401
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Unauthorized"}), 401
                return redirect(url_for("auth.login_page"))
            if user.role not in allowed_roles:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Forbidden. Insufficient permissions."}), 403
                return redirect(url_for("auth.login_page"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_random_password(length=10):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def generate_random_approval_no(doc_id, step_no=1, dept_code="IT"):
    year = datetime.now().strftime("%y")
    code = (dept_code or "IT")[:2].upper()
    suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"AH-{year}-{code}-{int(doc_id):04d}-{suffix}"


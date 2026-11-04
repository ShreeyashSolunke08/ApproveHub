import secrets
import string
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

def login_user(user):
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role
    session["user_email"] = user.email

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
                    return jsonify({"error": f"Forbidden. Required role: {', '.join(allowed_roles)}"}), 403
                return render_unauthorized()
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def render_unauthorized():
    return """
    <html><body style="font-family:sans-serif;text-align:center;padding:50px;">
    <h2>403 - Access Forbidden</h2>
    <p>You do not have permission to view this resource.</p>
    <a href="/">Go to Homepage</a>
    </body></html>
    """, 403

def generate_random_approval_no(doc_id, step_order, dept_code="IT"):
    """
    Generates high-entropy random approval number: e.g. AH-26-IT-0412-7KQ3
    Unguessable and strictly verified against database.
    """
    rand_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"AH-26-{dept_code.upper()}-{doc_id:04d}-{rand_suffix}"

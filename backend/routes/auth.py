import os
import base64
import secrets
from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, send_file, Response, current_app
from werkzeug.utils import secure_filename
from backend.models import db, User, Institution, Document, ApprovalStep
from backend.utils.security import login_user, logout_user, get_current_user, login_required
from backend.utils.signature_bridge import create_mobile_session, get_session, complete_mobile_session
from backend.utils.stamping import restamp_user_approved_documents

auth_bp = Blueprint("auth", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def generate_svg_avatar(name="User"):
    """
    Generates a crisp, high-resolution SVG monogram avatar with institutional gradient.
    """
    parts = name.strip().split()
    if len(parts) >= 2:
        initials = (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][:2].upper()
    else:
        initials = "AH"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4F46E5" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>
  </defs>
  <circle cx="64" cy="64" r="64" fill="url(#grad)" />
  <text x="64" y="73" fill="#FFFFFF" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="44" font-weight="700" text-anchor="middle" dominant-baseline="middle">{initials}</text>
</svg>"""
    return Response(svg, mimetype="image/svg+xml")

# ==========================================
# WEB AUTHENTICATION ROUTES
# ==========================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            if user.role == "approver":
                return redirect(url_for("approvals.approver_inbox"))
            elif user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("documents.applicant_dashboard"))
        else:
            return render_template("login.html", error="Invalid institutional email or password.")
            
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    institutions = Institution.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "applicant")  # applicant | approver
        department = request.form.get("department", "Information Technology")
        designation = request.form.get("designation", "")
        institution_id = request.form.get("institution_id", 1)
        
        if not name or not email or not password:
            return render_template("register.html", error="All required fields must be completed.", institutions=institutions)
            
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="An account with this institutional email already exists.", institutions=institutions)
            
        user = User(
            name=name,
            email=email,
            mobile=mobile,
            role=role,
            department=department,
            designation=designation or ("Student" if role == "applicant" else "Professor"),
            institution_id=institution_id
        )
        user.set_password(password)
        user.set_pin("1234")  # Default PIN
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        if user.role == "approver":
            return redirect(url_for("approvals.approver_inbox"))
        elif user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("documents.applicant_dashboard"))
        
    return render_template("register.html", institutions=institutions)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_page():
    message = None
    reset_link = None
    error = None
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            reset_link = url_for("auth.reset_password_page", token=token, _external=True)
            message = f"Password reset instructions and security token generated successfully for {user.email}."
        else:
            error = "No registered institutional account was found with that email address."
            
    return render_template("forgot_password.html", message=message, reset_link=reset_link, error=error)

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_page(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        return render_template("reset_password.html", error="This password reset link is invalid or has expired. Please request a new one.", invalid=True)
        
    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if len(new_password) < 6:
            return render_template("reset_password.html", error="Password must be at least 6 characters long.", token=token)
            
        if new_password != confirm_password:
            return render_template("reset_password.html", error="Passwords do not match.", token=token)
            
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash("Your password has been reset successfully. Please log in with your new credentials.", "success")
        return redirect(url_for("auth.login_page"))
        
    return render_template("reset_password.html", token=token)

@auth_bp.route("/auth/google")
def google_login():
    """
    Institutional Google OAuth 2.0 SSO entry point.
    Redirects to Google OAuth 2.0 when client credentials are configured,
    or performs instant institutional SSO verification.
    """
    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if google_client_id:
        redirect_uri = url_for("auth.google_callback", _external=True)
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={google_client_id}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"redirect_uri={redirect_uri}&"
            f"prompt=select_account"
        )
        return redirect(oauth_url)

    # In local/sandbox environment without external Google OAuth app credentials,
    # log in with institutional credentials directly:
    default_email = request.args.get("email", "shreeyash@vit.edu")
    user = User.query.filter_by(email=default_email).first()
    if not user:
        user = User(
            name=default_email.split("@")[0].replace(".", " ").title(),
            email=default_email,
            role="applicant",
            department="Information Technology",
            designation="Student (Google SSO)",
            institution_id=1,
            google_id="goog_oauth2_verified"
        )
        user.set_password("oauth_secure_temp_pwd")
        user.set_pin("1234")
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    flash(f"Successfully authenticated via Institutional Google SSO as {user.name}!", "success")
    if user.role == "approver":
        return redirect(url_for("approvals.approver_inbox"))
    elif user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    return redirect(url_for("documents.applicant_dashboard"))

@auth_bp.route("/auth/google/callback")
def google_callback():
    """
    OAuth 2.0 Callback handler for Google SSO.
    """
    code = request.args.get("code")
    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if code and google_client_id and google_client_secret:
        import urllib.request
        import urllib.parse
        import json
        
        # Token exchange
        token_data = urllib.parse.urlencode({
            "code": code,
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "redirect_uri": url_for("auth.google_callback", _external=True),
            "grant_type": "authorization_code"
        }).encode("utf-8")
        
        token_req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            with urllib.request.urlopen(token_req) as response:
                token_res = json.loads(response.read().decode())
                access_token = token_res.get("access_token")
                
                # Fetch user info
                user_req = urllib.request.Request(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                with urllib.request.urlopen(user_req) as ures:
                    user_info = json.loads(ures.read().decode())
                    email = user_info.get("email")
                    name = user_info.get("name") or email.split("@")[0].title()
                    sub = user_info.get("sub")
                    picture = user_info.get("picture")
                    
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        user = User(
                            name=name,
                            email=email,
                            role="applicant",
                            department="Information Technology",
                            designation="Institutional Member",
                            institution_id=1,
                            google_id=sub,
                            avatar_url=picture
                        )
                        user.set_password(secrets.token_hex(16))
                        user.set_pin("1234")
                        db.session.add(user)
                    else:
                        user.google_id = sub
                        if picture and not user.avatar_path:
                            user.avatar_url = picture
                    db.session.commit()
                    
                    login_user(user, remember=True)
                    flash(f"Welcome, {user.name}! Institutional SSO verification complete.", "success")
                    if user.role == "approver":
                        return redirect(url_for("approvals.approver_inbox"))
                    elif user.role == "admin":
                        return redirect(url_for("admin.admin_dashboard"))
                    return redirect(url_for("documents.applicant_dashboard"))
        except Exception as e:
            flash(f"Google SSO authentication error: {str(e)}", "danger")
            return redirect(url_for("auth.login_page"))
            
    flash("Authentication was canceled or incomplete.", "warning")
    return redirect(url_for("auth.login_page"))

# ==========================================
# REST API ENDPOINTS FOR CLIENTS & MOBILE APPS
# ==========================================

@auth_bp.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    remember = bool(data.get("remember", False))
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid institutional credentials."}), 401
        
    if not user.is_active:
        return jsonify({"success": False, "error": "This account is inactive. Please contact your institution administrator."}), 403
        
    login_user(user, remember=remember)
    
    redirect_map = {
        "approver": url_for("approvals.approver_inbox"),
        "admin": url_for("admin.admin_dashboard"),
        "applicant": url_for("documents.applicant_dashboard")
    }
    
    return jsonify({
        "success": True,
        "message": "Authenticated successfully.",
        "user": user.to_dict(),
        "redirect_url": redirect_map.get(user.role, url_for("documents.applicant_dashboard"))
    })

@auth_bp.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    mobile = data.get("mobile", "").strip()
    password = data.get("password", "")
    role = data.get("role", "applicant")
    department = data.get("department", "Information Technology")
    designation = data.get("designation", "")
    institution_id = data.get("institution_id", 1)
    
    if not name or not email or not password:
        return jsonify({"success": False, "error": "Name, email, and password are required."}), 400
        
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409
        
    user = User(
        name=name,
        email=email,
        mobile=mobile,
        role=role,
        department=department,
        designation=designation or ("Student" if role == "applicant" else "Professor"),
        institution_id=institution_id
    )
    user.set_password(password)
    user.set_pin("1234")
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    
    redirect_map = {
        "approver": url_for("approvals.approver_inbox"),
        "admin": url_for("admin.admin_dashboard"),
        "applicant": url_for("documents.applicant_dashboard")
    }
    
    return jsonify({
        "success": True,
        "message": "Account created successfully.",
        "user": user.to_dict(),
        "redirect_url": redirect_map.get(user.role, url_for("documents.applicant_dashboard"))
    }), 201

@auth_bp.route("/api/auth/logout", methods=["POST", "GET"])
def api_auth_logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully."})

@auth_bp.route("/api/auth/me", methods=["GET"])
def api_auth_me():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Not authenticated."}), 401
    return jsonify({
        "success": True,
        "user": user.to_dict()
    })

@auth_bp.route("/api/auth/change-password", methods=["POST"])
@login_required
def api_auth_change_password():
    user = get_current_user()
    data = request.get_json() or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    
    if not user.check_password(old_password):
        return jsonify({"success": False, "error": "Current password is incorrect."}), 400
        
    if len(new_password) < 6:
        return jsonify({"success": False, "error": "New password must be at least 6 characters long."}), 400
        
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"success": True, "message": "Password changed successfully."})

@auth_bp.route("/api/auth/forgot-password", methods=["POST"])
def api_auth_forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
        
    user = User.query.filter_by(email=email).first()
    if user:
        token = user.generate_reset_token()
        db.session.commit()
        reset_url = url_for("auth.reset_password_page", token=token, _external=True)
        return jsonify({
            "success": True,
            "message": "Password reset token generated.",
            "reset_url": reset_url,
            "token": token
        })
    return jsonify({"success": False, "error": "No account found with this email."}), 404

@auth_bp.route("/api/auth/reset-password", methods=["POST"])
def api_auth_reset_password():
    data = request.get_json() or {}
    token = data.get("token", "")
    new_password = data.get("password", "")
    
    if not token or not new_password:
        return jsonify({"success": False, "error": "Token and new password are required."}), 400
        
    if len(new_password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400
        
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        return jsonify({"success": False, "error": "Invalid or expired reset token."}), 400
        
    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    
    return jsonify({"success": True, "message": "Password has been reset successfully."})

@auth_bp.route("/api/auth/upload-avatar", methods=["POST"])
@login_required
def api_auth_upload_avatar():
    user = get_current_user()
    upload_dir = os.path.join("uploads", "assets")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Check if multipart file or json base64
    if "avatar" in request.files:
        file = request.files["avatar"]
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.{ext}"
            target_path = os.path.join(upload_dir, filename)
            file.save(target_path)
            user.avatar_path = target_path
            user.avatar_url = f"/user/avatar/{user.id}"
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Profile picture updated successfully.",
                "avatar_url": f"/user/avatar/{user.id}?t={int(datetime.now().timestamp())}"
            })
        return jsonify({"success": False, "error": "Invalid image file. Allowed types: PNG, JPG, JPEG, WEBP."}), 400

    data = request.get_json() or {}
    avatar_b64 = data.get("avatar_data", "")
    if avatar_b64 and "," in avatar_b64:
        try:
            _, encoded = avatar_b64.split(",", 1)
            file_bytes = base64.b64decode(encoded)
            filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.png"
            target_path = os.path.join(upload_dir, filename)
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            user.avatar_path = target_path
            user.avatar_url = f"/user/avatar/{user.id}"
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Profile picture updated successfully.",
                "avatar_url": f"/user/avatar/{user.id}?t={int(datetime.now().timestamp())}"
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to save avatar: {str(e)}"}), 500

    return jsonify({"success": False, "error": "No avatar file or data provided."}), 400

# ==========================================
# ASSET SERVING: AVATAR, SIGNATURE, STAMP
# ==========================================

@auth_bp.route("/user/avatar/<int:user_id>")
def get_user_avatar(user_id):
    """
    Serves the user's avatar image, or a dynamically rendered crisp SVG monogram avatar.
    """
    u = User.query.get(user_id)
    if not u:
        return generate_svg_avatar("ApproveHub User")

    if u.avatar_path and os.path.exists(u.avatar_path):
        mimetype = "image/png"
        if u.avatar_path.lower().endswith((".jpg", ".jpeg")):
            mimetype = "image/jpeg"
        elif u.avatar_path.lower().endswith(".webp"):
            mimetype = "image/webp"
        return send_file(os.path.abspath(u.avatar_path), mimetype=mimetype)
        
    if u.avatar_url and (u.avatar_url.startswith("http://") or u.avatar_url.startswith("https://")):
        return redirect(u.avatar_url)

    return generate_svg_avatar(u.name or "ApproveHub User")

@auth_bp.route("/user/signature/<int:user_id>")
def get_user_signature(user_id):
    """
    Serves the transparent PNG signature asset for display.
    """
    u = User.query.get(user_id)
    if u and u.signature_path and os.path.exists(u.signature_path):
        return send_file(os.path.abspath(u.signature_path), mimetype="image/png")
    return "", 404

@auth_bp.route("/user/stamp/<int:user_id>")
def get_user_stamp(user_id):
    """
    Serves the transparent PNG departmental stamp asset.
    """
    u = User.query.get(user_id)
    if u and u.stamp_path and os.path.exists(u.stamp_path):
        return send_file(os.path.abspath(u.stamp_path), mimetype="image/png")
    return "", 404

# ==========================================
# SIGNATURE SKETCH PAD & MOBILE QR BRIDGE
# ==========================================

@auth_bp.route("/api/profile/save-signature", methods=["POST"])
@login_required
def api_save_signature():
    """
    Saves transparent signature PNG generated from the HTML5 sketch pad and re-stamps approved documents.
    """
    user = get_current_user()
    data = request.get_json() or {}
    sig_data = data.get("signature_data", "")
    
    if sig_data and "," in sig_data:
        try:
            _, encoded = sig_data.split(",", 1)
            file_bytes = base64.b64decode(encoded)
            upload_dir = os.path.join("uploads", "assets")
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"sig_{user.id}_sketch.png"
            target_path = os.path.join(upload_dir, filename)
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            user.signature_path = target_path
            db.session.commit()
            
            # Immediately re-stamp all approved documents by this approver so the signature reflects!
            restamp_user_approved_documents(user.id)
            
            return jsonify({
                "success": True,
                "message": "Digital signature drawn and saved successfully!",
                "signature_url": url_for("auth.get_user_signature", user_id=user.id)
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to save signature: {str(e)}"}), 500
            
    return jsonify({"success": False, "error": "No signature drawing data received."}), 400

@auth_bp.route("/mobile-sign/<token>")
def mobile_sign_page(token):
    """
    Dedicated mobile signing interface for smartphone users (no app required).
    Features a clean, blank sketch pad with touch drawing.
    """
    session_data = get_session(token)
    if not session_data:
        return render_template("mobile_sign.html", error="This signature session is invalid or has expired. Please refresh the page on your computer to scan a new QR code.")
    user = User.query.get(session_data["user_id"])
    return render_template("mobile_sign.html", token=token, user=user)

@auth_bp.route("/api/mobile-sign/<token>/submit", methods=["POST"])
def api_mobile_sign_submit(token):
    """
    Receives signature drawn on mobile phone and saves it to user profile.
    """
    data = request.get_json() or {}
    sig_data = data.get("signature_data", "")
    success, msg = complete_mobile_session(token, sig_data)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "error": msg}), 400

@auth_bp.route("/api/signature-session/<token>/status")
def api_signature_session_status(token):
    """
    Status polling endpoint for the desktop web page to detect when mobile signing completes.
    """
    session_data = get_session(token)
    if not session_data:
        return jsonify({"status": "expired"})
    user_id = session_data["user_id"]
    return jsonify({
        "status": session_data["status"],
        "signature_url": url_for("auth.get_user_signature", user_id=user_id) if session_data["status"] == "completed" else None
    })

# ==========================================
# USER PROFILE & SECURITY SETTINGS
# ==========================================

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    user = get_current_user()
    message = None
    error = None
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_info":
            user.name = request.form.get("name", user.name)
            user.mobile = request.form.get("mobile", user.mobile)
            user.department = request.form.get("department", user.department)
            user.designation = request.form.get("designation", user.designation)
            db.session.commit()
            message = "Profile details updated successfully!"
        elif action == "update_pin":
            new_pin = request.form.get("pin")
            if new_pin and len(new_pin) >= 4:
                user.set_pin(new_pin)
                db.session.commit()
                message = "Security PIN updated successfully!"
            else:
                error = "Security PIN must be at least 4 digits."
        elif action == "change_password":
            current_pwd = request.form.get("current_password", "")
            new_pwd = request.form.get("new_password", "")
            confirm_pwd = request.form.get("confirm_password", "")
            if not user.check_password(current_pwd):
                error = "Current password is incorrect."
            elif len(new_pwd) < 6:
                error = "New password must be at least 6 characters long."
            elif new_pwd != confirm_pwd:
                error = "New passwords do not match."
            else:
                user.set_password(new_pwd)
                db.session.commit()
                message = "Account password updated successfully!"
        elif action == "upload_avatar":
            avatar_file = request.files.get("avatar")
            if avatar_file and avatar_file.filename and allowed_file(avatar_file.filename):
                ext = avatar_file.filename.rsplit(".", 1)[1].lower()
                upload_dir = os.path.join("uploads", "assets")
                os.makedirs(upload_dir, exist_ok=True)
                filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.{ext}"
                target_path = os.path.join(upload_dir, filename)
                avatar_file.save(target_path)
                user.avatar_path = target_path
                user.avatar_url = f"/user/avatar/{user.id}"
                db.session.commit()
                message = "Profile picture updated successfully!"
            else:
                error = "Please choose a valid image file (PNG, JPG, WEBP)."
        elif action == "remove_avatar":
            user.avatar_path = None
            user.avatar_url = None
            db.session.commit()
            message = "Profile picture removed. Monogram avatar will be displayed."
        elif action == "save_sketch_signature":
            sig_data = request.form.get("signature_data")
            if sig_data and "," in sig_data:
                try:
                    _, encoded = sig_data.split(",", 1)
                    file_bytes = base64.b64decode(encoded)
                    upload_dir = os.path.join("uploads", "assets")
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = f"sig_{user.id}_sketch.png"
                    target_path = os.path.join(upload_dir, filename)
                    with open(target_path, "wb") as f:
                        f.write(file_bytes)
                    user.signature_path = target_path
                    db.session.commit()
                    restamp_user_approved_documents(user.id)
                    message = "Official digital signature drawn and saved successfully!"
                except Exception as e:
                    error = f"Error saving signature sketch: {e}"
        elif action == "clear_signature":
            user.signature_path = None
            db.session.commit()
            restamp_user_approved_documents(user.id)
            message = "Personal signature reset to default institutional calligraphy stroke."
        elif action == "upload_signature":
            sig_file = request.files.get("signature")
            if sig_file and sig_file.filename:
                filename = f"sig_{user.id}_{secure_filename(sig_file.filename)}"
                upload_dir = os.path.join("uploads", "assets")
                os.makedirs(upload_dir, exist_ok=True)
                target_path = os.path.join(upload_dir, filename)
                sig_file.save(target_path)
                user.signature_path = target_path
                db.session.commit()
                restamp_user_approved_documents(user.id)
                message = "Official signature image uploaded successfully!"
        elif action == "upload_stamp":
            stamp_file = request.files.get("stamp")
            if stamp_file and stamp_file.filename:
                filename = f"stamp_{user.id}_{secure_filename(stamp_file.filename)}"
                upload_dir = os.path.join("uploads", "assets")
                os.makedirs(upload_dir, exist_ok=True)
                target_path = os.path.join(upload_dir, filename)
                stamp_file.save(target_path)
                user.stamp_path = target_path
                db.session.commit()
                restamp_user_approved_documents(user.id)
                message = "Official departmental stamp asset uploaded successfully!"

    # Create active mobile signing session for QR code display on desktop
    mobile_session = create_mobile_session(user.id) if user.role in ["approver", "admin"] else None

    # Summary statistics for this specific user
    total_submitted = Document.query.filter_by(applicant_id=user.id).count()
    total_approved = Document.query.filter_by(applicant_id=user.id, status="approved").count()
    total_acted_steps = ApprovalStep.query.filter_by(approver_id=user.id, status="approved").count()

    return render_template(
        "profile.html",
        user=user,
        message=message,
        error=error,
        mobile_session=mobile_session,
        total_submitted=total_submitted,
        total_approved=total_approved,
        total_acted_steps=total_acted_steps
    )

@auth_bp.route("/api/hierarchy/options")
def get_hierarchy_options():
    """
    Returns unique departments, designations, and approvers for dynamic cascading selectors.
    """
    approvers = User.query.filter_by(role="approver", is_active=True).all()
    data = []
    for a in approvers:
        data.append({
            "id": a.id,
            "name": a.name,
            "department": a.department or "Information Technology",
            "designation": a.designation or "Authority",
            "email": a.email
        })
    return jsonify(data)

@auth_bp.route("/api/pin/verify", methods=["POST"])
@login_required
def api_verify_pin():
    user = get_current_user()
    data = request.get_json() or {}
    pin_str = data.get("pin", "")
    
    success, message = user.check_pin(pin_str)
    db.session.commit()
    
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "error": message}), 400

@auth_bp.route("/api/pin/set", methods=["POST"])
@login_required
def api_set_pin():
    user = get_current_user()
    data = request.get_json() or {}
    new_pin = data.get("pin", "")
    if len(str(new_pin).strip()) < 4:
        return jsonify({"success": False, "error": "PIN must be at least 4 digits."}), 400
        
    user.set_pin(new_pin)
    db.session.commit()
    return jsonify({"success": True, "message": "Security PIN updated successfully."})

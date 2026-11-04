import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
from backend.models import db, User, Institution, Document, ApprovalStep
from backend.utils.security import login_user, logout_user, get_current_user, login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == "approver":
                return redirect(url_for("approvals.approver_inbox"))
            elif user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("documents.applicant_dashboard"))
        else:
            return render_template("login.html", error="Invalid institutional email or password.")
            
    return render_template("login.html")

@auth_bp.route("/auth/google")
def google_login():
    """
    Google SSO entry point with quick simulation / OAuth redirection.
    Allows instant institutional authentication with Google.
    """
    demo_email = request.args.get("email", "shreeyash@vit.edu")
    user = User.query.filter_by(email=demo_email).first()
    if not user:
        # Create Google-authenticated user on the fly
        user = User(
            name=demo_email.split("@")[0].replace(".", " ").title(),
            email=demo_email,
            role="applicant",
            department="Information Technology",
            designation="Student (Google SSO)",
            institution_id=1,
            google_id="goog_demo_oauth2_verified"
        )
        user.set_password("oauth_temp_pwd_123")
        user.set_pin("1234")
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"Successfully authenticated via Google as {user.name}!", "success")
    if user.role == "approver":
        return redirect(url_for("approvals.approver_inbox"))
    elif user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    return redirect(url_for("documents.applicant_dashboard"))

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
            return render_template("register.html", error="All fields are required.", institutions=institutions)
            
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="An account with this email already exists.", institutions=institutions)
            
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

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    user = get_current_user()
    message = None
    
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
                message = "Official departmental stamp asset uploaded successfully!"

    # Summary statistics for this specific user
    total_submitted = Document.query.filter_by(applicant_id=user.id).count()
    total_approved = Document.query.filter_by(applicant_id=user.id, status="approved").count()
    total_acted_steps = ApprovalStep.query.filter_by(approver_id=user.id, status="approved").count()

    return render_template(
        "profile.html",
        user=user,
        message=message,
        total_submitted=total_submitted,
        total_approved=total_approved,
        total_acted_steps=total_acted_steps
    )

import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from backend.models import db, User, Document, ApprovalStep, Timeline, Institution
from backend.utils.security import login_required, role_required, get_current_user

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    user = get_current_user()
    
    total_requests = Document.query.count()
    pending_count = Document.query.filter(Document.status.in_(["pending", "in_progress"])).count()
    compliance_count = Document.query.filter_by(status="compliance").count()
    approved_count = Document.query.filter_by(status="approved").count()
    rejected_count = Document.query.filter_by(status="rejected").count()
    total_people = User.query.count()
    
    recent_activity = Timeline.query.order_by(Timeline.timestamp.desc()).limit(12).all()
    
    return render_template(
        "admin_dashboard.html",
        user=user,
        total_requests=total_requests,
        pending_count=pending_count,
        compliance_count=compliance_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_people=total_people,
        recent_activity=recent_activity
    )

@admin_bp.route("/admin/documents")
@login_required
@role_required("admin")
def admin_documents():
    user = get_current_user()
    status_filter = request.args.get("status", "all")
    search_q = request.args.get("q", "").strip().lower()

    query = Document.query

    if status_filter != "all":
        if status_filter == "pending":
            query = query.filter(Document.status.in_(["pending", "in_progress"]))
        else:
            query = query.filter_by(status=status_filter)

    all_docs = query.order_by(Document.created_at.desc()).all()

    if search_q:
        docs = [d for d in all_docs if (search_q in d.title.lower() or search_q in d.applicant.name.lower() or str(d.id) == search_q)]
    else:
        docs = all_docs

    counts = {
        "all": Document.query.count(),
        "pending": Document.query.filter(Document.status.in_(["pending", "in_progress"])).count(),
        "approved": Document.query.filter_by(status="approved").count(),
        "compliance": Document.query.filter_by(status="compliance").count(),
        "rejected": Document.query.filter_by(status="rejected").count(),
    }

    return render_template(
        "admin_documents.html",
        user=user,
        documents=docs,
        status_filter=status_filter,
        search_q=search_q,
        counts=counts
    )

@admin_bp.route("/admin/hierarchy")
@login_required
@role_required("admin")
def hierarchy_builder():
    user = get_current_user()
    approvers = User.query.filter_by(role="approver").all()
    departments = {}
    for a in approvers:
        dept = a.department or "General"
        desig = a.designation or "Authority"
        if dept not in departments:
            departments[dept] = {}
        if desig not in departments[dept]:
            departments[dept][desig] = []
        departments[dept][desig].append(a)
        
    return render_template("admin_hierarchy.html", user=user, departments=departments)

@admin_bp.route("/admin/people", methods=["GET", "POST"])
@login_required
@role_required("admin")
def people_management():
    user = get_current_user()
    search_q = request.args.get("q", "").strip().lower()

    if request.method == "POST":
        action = request.form.get("action")
        target_id = request.form.get("user_id")
        target_user = User.query.get(target_id)
        if target_user and action == "toggle_active":
            target_user.is_active = not target_user.is_active
            db.session.commit()

    all_users = User.query.order_by(User.id.asc()).all()
    if search_q:
        users = [u for u in all_users if (search_q in u.name.lower() or search_q in u.email.lower() or search_q in (u.department or '').lower())]
    else:
        users = all_users

    return render_template("admin_people.html", user=user, users=users, search_q=search_q)

@admin_bp.route("/admin/audit")
@login_required
@role_required("admin")
def audit_log():
    user = get_current_user()
    logs = Timeline.query.order_by(Timeline.timestamp.desc()).limit(100).all()
    return render_template("admin_audit.html", user=user, logs=logs)

@admin_bp.route("/admin/audit/export.csv")
@login_required
@role_required("admin")
def export_audit_csv():
    logs = Timeline.query.order_by(Timeline.timestamp.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp (UTC)", "Document ID", "Actor", "Event", "Details", "IP Address"])
    
    for l in logs:
        writer.writerow([
            l.id,
            l.timestamp.isoformat() if l.timestamp else "",
            l.document_id,
            l.user.name if l.user else "System",
            l.event,
            l.details,
            l.ip_address or ""
        ])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=approvehub_audit_log.csv"}
    )

@admin_bp.route("/admin/settings", methods=["GET", "POST"])
@login_required
@role_required("admin")
def institution_settings():
    user = get_current_user()
    inst = Institution.query.first()
    if not inst:
        inst = Institution(name="VIT Pune", code="VITP")
        db.session.add(inst)
        db.session.commit()
        
    if request.method == "POST":
        inst.name = request.form.get("name", inst.name)
        inst.sequential_enforced = bool(request.form.get("sequential_enforced"))
        inst.require_pin = bool(request.form.get("require_pin"))
        inst.auto_expire_days = int(request.form.get("auto_expire_days", 14))
        db.session.commit()
        return redirect(url_for("admin.institution_settings"))
        
    return render_template("admin_settings.html", user=user, institution=inst)

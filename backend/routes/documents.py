import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, current_app, abort
from werkzeug.utils import secure_filename
from backend.models import db, Document, ApprovalStep, Timeline, User
from backend.utils.security import login_required, get_current_user, generate_random_approval_no
from backend.utils.hashing import sha256_file, verify_file
from backend.utils.validators import validate_pdf_file

documents_bp = Blueprint("documents", __name__)

# Document Type Catalogs
STUDENT_DOC_TYPES = [
    ("bonafide", "Bonafide Certificate Request"),
    ("leave_student", "Leave Application (Duty / Medical)"),
    ("noc_project", "Project / Internship NOC Letter"),
    ("railway_concession", "Railway Concession Form"),
    ("scholarship_form", "Scholarship Verification Document"),
    ("lor_request", "Letter of Recommendation (LOR)"),
    ("other_student", "Other Institutional Request")
]

STAFF_DOC_TYPES = [
    ("leave_faculty", "Casual / Duty Leave Application"),
    ("grant_research", "Research / Conference Grant Requisition"),
    ("purchase_indent", "Lab Equipment / Purchase Indent"),
    ("budget_approval", "Department Budget & Sponsorship Approval"),
    ("faculty_noc", "Faculty NOC / Deputation Approval"),
    ("exam_clearance", "Exam Duty & Paper Moderation Clearance"),
    ("other_staff", "Other Official Administrative Request")
]

@documents_bp.route("/")
def home():
    user = get_current_user()
    return render_template("index.html", user=user)

@documents_bp.route("/download-apk")
@documents_bp.route("/download/app")
def download_apk():
    apk_path = os.path.join(current_app.static_folder, "downloads", "ApproveHub.apk")
    if not os.path.exists(apk_path):
        alt_path = os.path.join(current_app.root_path, "android_build_artifact", "ApproveHub-Android-APK", "app-debug.apk")
        if os.path.exists(alt_path):
            return send_file(alt_path, as_attachment=True, download_name="ApproveHub.apk", mimetype="application/vnd.android.package-archive")
        abort(404)
    return send_file(apk_path, as_attachment=True, download_name="ApproveHub.apk", mimetype="application/vnd.android.package-archive")

@documents_bp.route("/dashboard")
@documents_bp.route("/user")
@login_required
def applicant_dashboard():
    user = get_current_user()
    search_query = request.args.get("q", "").strip().lower()
    type_filter = request.args.get("type", "").strip()

    query = Document.query.filter_by(applicant_id=user.id)
    
    if search_query:
        query = query.filter(Document.title.ilike(f"%{search_query}%"))
    if type_filter:
        query = query.filter_by(document_type=type_filter)
        
    documents = query.order_by(Document.created_at.desc()).all()
    
    # Calculate quick dashboard counts
    all_user_docs = Document.query.filter_by(applicant_id=user.id).all()
    active_count = sum(1 for d in all_user_docs if d.status in ["pending", "in_progress", "compliance"])
    approved_count = sum(1 for d in all_user_docs if d.status == "approved")
    rejected_count = sum(1 for d in all_user_docs if d.status == "rejected")
    
    doc_types = STAFF_DOC_TYPES if user.role in ["approver", "admin"] else STUDENT_DOC_TYPES
    
    return render_template(
        "applicant_dashboard.html",
        user=user,
        documents=documents,
        active_count=active_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        search_query=search_query,
        type_filter=type_filter,
        doc_types=doc_types
    )

@documents_bp.route("/documents/new", methods=["GET", "POST"])
@login_required
def upload_document():
    user = get_current_user()
    doc_types = STAFF_DOC_TYPES if user.role in ["approver", "admin"] else STUDENT_DOC_TYPES

    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title", "").strip()
        doc_type = request.form.get("document_type", "bonafide")
        
        # If title empty, auto-populate from document type
        if not title:
            for k, label in doc_types:
                if k == doc_type:
                    title = label
                    break
            if not title:
                title = "Official Document Request"
        
        is_valid, msg = validate_pdf_file(file)
        if not is_valid:
            return render_template("upload.html", error=msg, user=user, doc_types=doc_types)
            
        safe_name = f"doc_{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
        docs_dir = current_app.config["DOCS_FOLDER"]
        os.makedirs(docs_dir, exist_ok=True)
        save_path = os.path.join(docs_dir, safe_name)
        file.save(save_path)
        
        # Immediate SHA-256 integrity calculation
        original_hash = sha256_file(save_path)
        
        doc = Document(
            institution_id=user.institution_id or 1,
            applicant_id=user.id,
            title=title,
            document_type=doc_type,
            file_path=save_path,
            original_hash=original_hash,
            status="draft",
            current_step=1,
            total_steps=1,
            qr_pos_x=0.78,
            qr_pos_y=0.03,
            qr_page_no=1
        )
        db.session.add(doc)
        db.session.commit()
        
        # Log upload in audit timeline
        tl = Timeline(
            document_id=doc.id,
            user_id=user.id,
            event="DOCUMENT_UPLOADED",
            details=f"File '{file.filename}' uploaded ({title}). SHA-256: {original_hash[:16]}...",
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        
        return redirect(url_for("documents.place_marks", doc_id=doc.id))

    return render_template("upload.html", user=user, doc_types=doc_types)

@documents_bp.route("/documents/<int:doc_id>/place", methods=["GET", "POST"])
@login_required
def place_marks(doc_id):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    
    if document.applicant_id != user.id and user.role != "admin":
        abort(403)
        
    approvers = User.query.filter_by(role="approver", is_active=True).all()
    
    if request.method == "POST":
        data = request.get_json() if request.is_json else None
        if not data:
            return jsonify({"error": "Invalid payload"}), 400
            
        steps_data = data.get("steps", [])
        if not steps_data:
            return jsonify({"error": "At least one approver must be selected."}), 400
            
        # Clean existing draft steps if re-configuring
        ApprovalStep.query.filter_by(document_id=document.id).delete()
        
        for idx, step_info in enumerate(steps_data):
            approver_id = int(step_info.get("approver_id"))
            page_no = int(step_info.get("page_no", 1))
            pos_x = float(step_info.get("pos_x", 0.08 + (idx * 0.45)))
            pos_y = float(step_info.get("pos_y", 0.75))
            mark_type = step_info.get("mark_type", "signature")
            
            step_status = "pending" if idx == 0 else "waiting"
            app_no = generate_random_approval_no(document.id, idx + 1, user.department[:2] if user.department else "IT")
            
            step = ApprovalStep(
                document_id=document.id,
                approver_id=approver_id,
                step_order=idx + 1,
                mark_type=mark_type,
                page_no=page_no,
                pos_x=pos_x,
                pos_y=pos_y,
                status=step_status,
                approval_no=app_no
            )
            db.session.add(step)
            
        # QR Code position chosen by applicant
        qr_info = data.get("qr_position", {})
        document.qr_pos_x = float(qr_info.get("pos_x", 0.78))
        document.qr_pos_y = float(qr_info.get("pos_y", 0.03))
        document.qr_page_no = int(qr_info.get("page_no", 1))
        
        document.total_steps = len(steps_data)
        document.current_step = 1
        document.status = "pending"
        
        # Add timeline event
        tl = Timeline(
            document_id=document.id,
            user_id=user.id,
            event="WORKFLOW_ROUTED",
            details=f"Approval chain assigned: {len(steps_data)} authority levels with custom QR position.",
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        
        return jsonify({"success": True, "redirect_url": url_for("documents.document_detail", doc_id=document.id)})
        
    return render_template("place_marks.html", user=user, document=document, approvers=approvers)

@documents_bp.route("/documents/<int:doc_id>")
@login_required
def document_detail(doc_id):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    
    is_assigned = any(s.approver_id == user.id for s in document.approval_steps)
    if document.applicant_id != user.id and not is_assigned and user.role != "admin":
        abort(403)
        
    timeline_events = Timeline.query.filter_by(document_id=doc_id).order_by(Timeline.timestamp.asc()).all()
    
    # Active authority holding the document
    current_active_step = None
    for s in document.approval_steps:
        if s.status == "pending":
            current_active_step = s
            break

    return render_template(
        "document_detail.html",
        user=user,
        document=document,
        timeline_events=timeline_events,
        current_active_step=current_active_step
    )

@documents_bp.route("/documents/<int:doc_id>/download")
@login_required
def download_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    target_path = document.final_path if (document.status == "approved" and document.final_path) else document.file_path
    expected_hash = document.final_hash if (document.status == "approved" and document.final_hash) else document.original_hash
    
    if not verify_file(target_path, expected_hash):
        abort(400, description="Cryptographic integrity mismatch! File has been tampered with or modified on disk.")
        
    return send_file(target_path, as_attachment=True, download_name=f"{document.title.replace(' ', '_')}.pdf")

@documents_bp.route("/documents/<int:doc_id>/preview")
@login_required
def preview_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    target_path = document.final_path if (document.status == "approved" and document.final_path) else document.file_path
    return send_file(target_path, mimetype="application/pdf")

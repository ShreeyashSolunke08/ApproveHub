import os
import uuid
import pymupdf
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, current_app, abort, Response, flash
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
            width_pts = float(step_info.get("width_pts", 140.0))
            height_pts = float(step_info.get("height_pts", 50.0))
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
                width_pts=width_pts,
                height_pts=height_pts,
                status=step_status,
                approval_no=app_no
            )
            db.session.add(step)
            
        # QR Code position and size chosen by applicant
        qr_info = data.get("qr_position", {})
        document.qr_pos_x = float(qr_info.get("pos_x", 0.78))
        document.qr_pos_y = float(qr_info.get("pos_y", 0.03))
        document.qr_page_no = int(qr_info.get("page_no", 1))
        document.qr_size = float(qr_info.get("qr_size", 54.0))
        
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

def _resolve_doc_path(file_path):
    if not file_path:
        return None
    if os.path.exists(file_path):
        return file_path
    candidate = os.path.join(current_app.config.get("DOCS_FOLDER", "uploads/docs"), os.path.basename(file_path))
    if os.path.exists(candidate):
        return candidate
    fallback = os.path.join(current_app.config.get("DOCS_FOLDER", "uploads/docs"), "bonafide_request.pdf")
    if os.path.exists(fallback):
        return fallback
    return None

@documents_bp.route("/api/documents/<int:doc_id>/pages-info")
@login_required
def get_document_pages_info(doc_id):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    if document.applicant_id != user.id and user.role not in ["admin", "approver"]:
        abort(403)
        
    resolved_path = _resolve_doc_path(document.file_path)
    if not resolved_path or not os.path.exists(resolved_path):
        return jsonify({"error": "Document file not found on disk"}), 404
        
    doc = pymupdf.open(resolved_path)
    total_pages = len(doc)
    pages = []
    for i in range(total_pages):
        p = doc[i]
        pages.append({
            "page_num": i + 1,
            "width": p.rect.width,
            "height": p.rect.height
        })
    doc.close()
    return jsonify({
        "total_pages": total_pages,
        "pages": pages
    })

@documents_bp.route("/api/documents/<int:doc_id>/page/<int:page_num>/render")
@login_required
def render_document_page(doc_id, page_num):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    if document.applicant_id != user.id and user.role not in ["admin", "approver"]:
        abort(403)
        
    resolved_path = _resolve_doc_path(document.file_path)
    if not resolved_path or not os.path.exists(resolved_path):
        abort(404)
        
    doc = pymupdf.open(resolved_path)
    total_pages = len(doc)
    idx = min(max(0, page_num - 1), total_pages - 1)
    page = doc[idx]
    pix = page.get_pixmap(dpi=150)
    png_bytes = pix.tobytes("png")
    doc.close()
    return Response(png_bytes, mimetype="image/png")

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

def _check_doc_access(document, user):
    """Enforces strict role-based and ownership-based access control (Anti-IDOR)."""
    is_approver = any(s.approver_id == user.id for s in document.approval_steps)
    if document.applicant_id != user.id and not is_approver and user.role != "admin":
        abort(403, description="Unauthorized: You do not have permission to access this requisition.")

@documents_bp.route("/documents/<int:doc_id>/download")
@login_required
def download_document(doc_id):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    _check_doc_access(document, user)
    
    target_path = document.final_path if (document.status == "approved" and document.final_path) else document.file_path
    expected_hash = document.final_hash if (document.status == "approved" and document.final_hash) else document.original_hash
    
    if not verify_file(target_path, expected_hash):
        abort(400, description="Cryptographic integrity mismatch! File has been tampered with or modified on disk.")
        
    return send_file(target_path, as_attachment=True, download_name=f"{document.title.replace(' ', '_')}.pdf")

@documents_bp.route("/documents/<int:doc_id>/preview")
@login_required
def preview_document(doc_id):
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    _check_doc_access(document, user)
    
    target_path = document.final_path if (document.status == "approved" and document.final_path) else document.file_path
    return send_file(target_path, mimetype="application/pdf")

@documents_bp.route("/documents/<int:doc_id>/withdraw", methods=["POST"])
@login_required
def withdraw_document(doc_id):
    """
    Allows the applicant (or admin) to withdraw / take back an active application.
    Halts any pending approval steps and marks the document as withdrawn.
    """
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    
    if document.applicant_id != user.id and user.role != "admin":
        abort(403, description="You are not authorized to withdraw this application.")
        
    if document.status == "approved":
        flash("Approved documents have already been sealed and cannot be withdrawn.", "danger")
        return redirect(url_for("documents.document_detail", doc_id=doc_id))
        
    try:
        document.status = "withdrawn"
        
        # Cancel any waiting, pending, or compliance steps
        for step in document.approval_steps:
            if step.status in ["waiting", "pending", "compliance"]:
                step.status = "rejected"
                step.remark = f"Application withdrawn by applicant {user.name}."
                
        # Record in timeline
        tl = Timeline(
            document_id=document.id,
            user_id=user.id,
            event="APPLICATION_WITHDRAWN",
            details=f"Application '{document.title}' was taken back / withdrawn by applicant {user.name}."
        )
        db.session.add(tl)
        db.session.commit()
        flash(f"Application '{document.title}' has been successfully withdrawn.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to withdraw application: {str(e)}", "danger")

    return redirect(url_for("documents.applicant_dashboard"))

@documents_bp.route("/documents/<int:doc_id>/resubmit", methods=["POST"])
@login_required
def resubmit_compliance(doc_id):
    """
    Compliance Resolution Workflow:
    Allows an applicant to address reviewer comments, optionally upload an updated PDF,
    and transition the workflow from 'compliance' back to 'pending' for re-review.
    """
    user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    
    if document.applicant_id != user.id and user.role != "admin":
        abort(403)
        
    if document.status != "compliance":
        flash("This document is not currently flagged for compliance resolution.", "warning")
        return redirect(url_for("documents.document_detail", doc_id=doc_id))
        
    notes = request.form.get("resubmit_notes", "").strip()
    replacement_file = request.files.get("replacement_file")
    
    try:
        updated_file_msg = ""
        if replacement_file and replacement_file.filename:
            is_valid, msg = validate_pdf_file(replacement_file)
            if not is_valid:
                flash(f"Invalid replacement file: {msg}", "danger")
                return redirect(url_for("documents.document_detail", doc_id=doc_id))
                
            safe_name = f"doc_{uuid.uuid4().hex[:12]}_{secure_filename(replacement_file.filename)}"
            docs_dir = current_app.config["DOCS_FOLDER"]
            save_path = os.path.join(docs_dir, safe_name)
            replacement_file.save(save_path)
            
            document.file_path = save_path
            document.original_hash = sha256_file(save_path)
            updated_file_msg = f" (Updated PDF '{replacement_file.filename}' uploaded, SHA-256: {document.original_hash[:16]}...)"
            
        # Locate the compliance step and reset to pending
        compliance_step = None
        for step in document.approval_steps:
            if step.status == "compliance":
                step.status = "pending"
                compliance_step = step
                break
                
        document.status = "in_progress" if document.current_step > 1 else "pending"
        
        detail_msg = f"Compliance requirements addressed by applicant {user.name}. Notes: '{notes or 'Corrections completed'}'{updated_file_msg}"
        tl = Timeline(
            document_id=document.id,
            user_id=user.id,
            event="COMPLIANCE_RESOLVED",
            details=detail_msg,
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        
        flash("Compliance corrections submitted successfully! The authority has been notified to resume review.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting compliance response: {str(e)}", "danger")
        
    return redirect(url_for("documents.document_detail", doc_id=doc_id))

@documents_bp.route("/documents/<int:doc_id>/certificate")
def download_audit_certificate(doc_id):
    """
    Generates and downloads a formal 1-page Cryptographic Audit Trail Certificate
    (Certificate of Authenticity & Signoff Completion) with tamper fingerprints.
    """
    document = Document.query.get_or_404(doc_id)
    user = get_current_user()
    
    # Publicly accessible if approved and has final hash, else requires login access
    if document.status != "approved":
        if not user:
            return redirect(url_for("auth.login_page"))
        _check_doc_access(document, user)
        
    # Generate vector certificate with PyMuPDF
    cert_doc = pymupdf.open()
    page = cert_doc.new_page(width=612, height=792)  # Standard US Letter
    
    # Border & Institutional Header
    page.draw_rect(pymupdf.Rect(24, 24, 588, 768), color=(0.2, 0.25, 0.35), width=1.5)
    page.draw_rect(pymupdf.Rect(28, 28, 584, 764), color=(0.85, 0.88, 0.92), width=0.8)
    
    # Header Banner
    page.draw_rect(pymupdf.Rect(28, 28, 584, 110), color=None, fill=(0.06, 0.12, 0.22))
    page.insert_text(pymupdf.Point(50, 68), "APPROVEHUB — CERTIFICATE OF AUTHENTICITY", fontsize=15, fontname="hebo", color=(1, 1, 1))
    page.insert_text(pymupdf.Point(50, 92), "Official Institutional Cryptographic Signoff Trail & Integrity Record", fontsize=9.5, fontname="helv", color=(0.8, 0.85, 0.9))
    
    # Document Metadata Block
    y = 145
    page.insert_text(pymupdf.Point(50, y), f"Document Title: {document.title}", fontsize=11, fontname="hebo", color=(0.1, 0.15, 0.25))
    y += 20
    inst_name = document.institution.name if document.institution else "VIT Pune"
    page.insert_text(pymupdf.Point(50, y), f"Issuing Institution: {inst_name}  |  Document ID: #{document.id}", fontsize=9, fontname="helv", color=(0.3, 0.35, 0.4))
    y += 18
    app_name = document.applicant.name if document.applicant else "N/A"
    app_email = document.applicant.email if document.applicant else "N/A"
    page.insert_text(pymupdf.Point(50, y), f"Applicant: {app_name} ({app_email})", fontsize=9, fontname="helv", color=(0.3, 0.35, 0.4))
    y += 18
    sub_date = document.created_at.strftime("%d %B %Y at %H:%M UTC") if document.created_at else "N/A"
    page.insert_text(pymupdf.Point(50, y), f"Submitted On: {sub_date}  |  Lifecycle Status: {document.status.upper()}", fontsize=9, fontname="helv", color=(0.3, 0.35, 0.4))
    
    # Hash Integrity Section
    y += 30
    page.draw_rect(pymupdf.Rect(45, y - 10, 567, y + 54), color=(0.82, 0.86, 0.92), fill=(0.96, 0.97, 0.99), width=1)
    page.insert_text(pymupdf.Point(55, y + 8), "CRYPTOGRAPHIC INTEGRITY FINGERPRINTS", fontsize=9, fontname="hebo", color=(0.15, 0.25, 0.45))
    page.insert_text(pymupdf.Point(55, y + 26), f"Original Submission Hash (SHA-256): {document.original_hash}", fontsize=7.5, fontname="courier", color=(0.2, 0.2, 0.2))
    f_hash = document.final_hash or "Pending Final Institutional Authority Signoff"
    page.insert_text(pymupdf.Point(55, y + 42), f"Final Approved Sealed Hash (SHA-256): {f_hash}", fontsize=7.5, fontname="courier", color=(0.06, 0.46, 0.25) if document.final_hash else (0.5, 0.5, 0.5))
    
    # Signoff Hierarchy Table
    y += 80
    page.insert_text(pymupdf.Point(50, y), "CHRONOLOGICAL SIGNATURE & APPROVAL TRAIL", fontsize=10, fontname="hebo", color=(0.1, 0.15, 0.25))
    y += 15
    
    # Table Header
    page.draw_rect(pymupdf.Rect(45, y - 5, 567, y + 16), color=None, fill=(0.90, 0.92, 0.96))
    page.insert_text(pymupdf.Point(52, y + 10), "Step", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    page.insert_text(pymupdf.Point(85, y + 10), "Authorized Approver", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    page.insert_text(pymupdf.Point(235, y + 10), "Designation / Dept", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    page.insert_text(pymupdf.Point(375, y + 10), "Approval No.", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    page.insert_text(pymupdf.Point(470, y + 10), "Timestamp (UTC)", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    y += 24
    
    for step in document.approval_steps:
        status_color = (0.05, 0.55, 0.25) if step.status == "approved" else (0.6, 0.4, 0.1)
        approver_name = step.approver.name if step.approver else "Unassigned"
        desig = f"{step.approver.designation or 'Authority'} ({step.approver.department or 'Dept'})"
        app_no = step.approval_no or "Pending"
        acted = step.acted_at.strftime("%d %b %Y, %H:%M") if step.acted_at else "Pending"
        
        page.insert_text(pymupdf.Point(55, y), str(step.step_order), fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
        page.insert_text(pymupdf.Point(85, y), approver_name[:24], fontsize=8, fontname="helv", color=(0.1, 0.1, 0.1))
        page.insert_text(pymupdf.Point(235, y), desig[:26], fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
        page.insert_text(pymupdf.Point(375, y), app_no, fontsize=7.5, fontname="courier", color=status_color)
        page.insert_text(pymupdf.Point(470, y), acted, fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
        y += 20
        
    # Timeline Audit Highlights
    y += 25
    page.insert_text(pymupdf.Point(50, y), "SECURITY & VERIFICATION AUDIT TRAIL (LAST 5 EVENTS)", fontsize=10, fontname="hebo", color=(0.1, 0.15, 0.25))
    y += 15
    recent_tl = Timeline.query.filter_by(document_id=doc_id).order_by(Timeline.timestamp.asc()).limit(6).all()
    for ev in recent_tl:
        t_str = ev.timestamp.strftime("%d %b %H:%M") if ev.timestamp else ""
        actor = ev.user.name if ev.user else "System"
        page.insert_text(pymupdf.Point(52, y), f"• [{t_str}] {ev.event} by {actor}: {ev.details[:68]}...", fontsize=7.5, fontname="helv", color=(0.35, 0.38, 0.42))
        y += 16
        
    # Bottom Certification Seal Note
    page.draw_rect(pymupdf.Rect(45, 710, 567, 750), color=(0.85, 0.88, 0.92), fill=(0.98, 0.98, 0.99), width=0.8)
    page.insert_text(pymupdf.Point(55, 725), "LEGAL & FORENSIC CERTIFICATION NOTICE:", fontsize=7, fontname="hebo", color=(0.2, 0.2, 0.2))
    page.insert_text(pymupdf.Point(55, 738), "This immutable digital audit certificate is generated directly by ApproveHub Cryptographic Vector Engine.", fontsize=6.8, fontname="helv", color=(0.4, 0.4, 0.4))
    
    cert_bytes = cert_doc.tobytes()
    cert_doc.close()
    
    return Response(
        cert_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ApproveHub_Audit_Certificate_Doc_{doc_id}.pdf"}
    )



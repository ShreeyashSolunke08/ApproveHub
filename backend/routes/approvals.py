import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, abort
from backend.models import db, Document, ApprovalStep, Timeline, User
from backend.utils.security import login_required, role_required, get_current_user
from backend.utils.hashing import verify_file, generate_record_hash
from backend.utils.stamping import stamp_final_document

approvals_bp = Blueprint("approvals", __name__)

@approvals_bp.route("/approver/inbox")
@login_required
@role_required("approver", "admin")
def approver_inbox():
    user = get_current_user()
    search_q = request.args.get("q", "").strip().lower()
    mark_filter = request.args.get("mark_type", "").strip()

    query = ApprovalStep.query.filter_by(
        approver_id=user.id,
        status="pending"
    )
    
    if mark_filter:
        query = query.filter_by(mark_type=mark_filter)
        
    all_pending = query.all()
    
    if search_q:
        pending_steps = [s for s in all_pending if (search_q in s.document.title.lower() or search_q in s.document.applicant.name.lower())]
    else:
        pending_steps = all_pending
    
    return render_template(
        "approver_inbox.html",
        user=user,
        pending_steps=pending_steps,
        search_q=search_q,
        mark_filter=mark_filter
    )

@approvals_bp.route("/approver/history")
@login_required
@role_required("approver", "admin")
def approver_history():
    user = get_current_user()
    search_q = request.args.get("q", "").strip().lower()

    query = ApprovalStep.query.filter(
        ApprovalStep.approver_id == user.id,
        ApprovalStep.status.in_(["approved", "compliance", "rejected"])
    ).order_by(ApprovalStep.acted_at.desc())

    all_steps = query.all()
    if search_q:
        history_steps = [s for s in all_steps if (search_q in s.document.title.lower() or (s.approval_no and search_q in s.approval_no.lower()))]
    else:
        history_steps = all_steps
    
    return render_template("approver_history.html", user=user, history_steps=history_steps, search_q=search_q)

@approvals_bp.route("/approvals/<int:step_id>/review")
@login_required
@role_required("approver", "admin")
def review_step(step_id):
    user = get_current_user()
    step = ApprovalStep.query.get_or_404(step_id)
    
    if step.approver_id != user.id and user.role != "admin":
        abort(403)
        
    document = step.document
    
    # Tamper detection prior to allowing review
    tamper_error = None
    if not verify_file(document.file_path, document.original_hash):
        tamper_error = "SECURITY ALERT: Cryptographic tamper detected on this file!"

    return render_template("review_approve.html", user=user, step=step, document=document, tamper_error=tamper_error)

@approvals_bp.route("/api/steps/<int:step_id>/action", methods=["POST"])
@login_required
@role_required("approver", "admin")
def take_approval_action(step_id):
    user = get_current_user()
    step = ApprovalStep.query.get_or_404(step_id)
    
    if step.approver_id != user.id and user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
        
    doc = step.document
    
    # Verify file integrity before acting
    if not verify_file(doc.file_path, doc.original_hash):
        tl = Timeline(
            document_id=doc.id,
            user_id=user.id,
            event="TAMPER_DETECTED",
            details="Cryptographic hash verification failed during approval attempt! Action blocked.",
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        return jsonify({"error": "File integrity check failed. Document appears modified on disk."}), 400

    data = request.get_json() or {}
    action = data.get("action")  # 'approve' | 'pending' | 'compliance' | 'reject'
    pin = data.get("pin", "")
    remark = data.get("remark", "").strip()
    reject_reason = data.get("reject_reason", "")
    
    now = datetime.now(timezone.utc)

    if action == "approve":
        # 1. Verify Approver PIN
        pin_valid, pin_msg = user.check_pin(pin)
        db.session.commit()
        if not pin_valid:
            return jsonify({"error": pin_msg}), 400
            
        step.status = "approved"
        step.remark = remark or "Approved with digital authority mark."
        step.acted_at = now
        step.record_hash = generate_record_hash(doc.id, step.step_order, user.id, step.approval_no, now.isoformat())
        
        # 2. Advance state machine
        next_step = ApprovalStep.query.filter_by(
            document_id=doc.id,
            step_order=step.step_order + 1
        ).first()
        
        if next_step:
            next_step.status = "pending"
            doc.current_step = next_step.step_order
            doc.status = "in_progress"
            event_text = f"Approved by {user.name} ({user.designation}). Forwarded to Step {next_step.step_order} ({next_step.approver.name})."
        else:
            # Final approval in chain: trigger PyMuPDF stamping engine!
            doc.status = "approved"
            base_url = request.host_url.rstrip("/")
            final_path, final_hash = stamp_final_document(doc, base_url=base_url)
            doc.final_path = final_path
            doc.final_hash = final_hash
            event_text = f"Final institutional approval granted by {user.name}. Official marks & QR verification stamped."

        tl = Timeline(
            document_id=doc.id,
            user_id=user.id,
            event="STEP_APPROVED",
            details=event_text,
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        
        return jsonify({"success": True, "status": doc.status, "message": "Approval recorded successfully."})

    elif action == "pending":
        step.remark = remark or "Under further review"
        tl = Timeline(
            document_id=doc.id,
            user_id=user.id,
            event="KEPT_PENDING",
            details=f"Kept pending by {user.name}: {step.remark}",
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        return jsonify({"success": True, "message": "Marked as pending."})

    elif action in ["compliance", "reject"]:
        step.status = "compliance" if action == "compliance" else "rejected"
        step.reject_reason = reject_reason or "Discrepancy in submission"
        step.remark = remark
        step.acted_at = now
        
        doc.status = "compliance" if action == "compliance" else "rejected"
        
        tl = Timeline(
            document_id=doc.id,
            user_id=user.id,
            event="COMPLIANCE_REQUESTED" if action == "compliance" else "REQUEST_REJECTED",
            details=f"Action by {user.name}: {step.reject_reason}. Notes: {remark}",
            ip_address=request.remote_addr
        )
        db.session.add(tl)
        db.session.commit()
        return jsonify({"success": True, "status": doc.status, "message": f"Document marked as {doc.status}."})

    return jsonify({"error": "Unknown action"}), 400

@approvals_bp.route("/api/documents/<int:doc_id>/fulfil", methods=["POST"])
@login_required
def fulfil_compliance(doc_id):
    user = get_current_user()
    doc = Document.query.get_or_404(doc_id)
    if doc.applicant_id != user.id and user.role != "admin":
        abort(403)
        
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
        
    safe_name = f"revised_doc_{doc.id}_{file.filename}"
    save_path = os.path.join(current_app.config["DOCS_FOLDER"], safe_name)
    file.save(save_path)
    
    new_hash = generate_record_hash(doc.id, 0, user.id, "REVISION", datetime.now(timezone.utc).isoformat())
    doc.file_path = save_path
    doc.original_hash = new_hash
    doc.status = "in_progress"
    
    current_step = ApprovalStep.query.filter_by(document_id=doc.id, step_order=doc.current_step).first()
    if current_step:
        current_step.status = "pending"
        
    tl = Timeline(
        document_id=doc.id,
        user_id=user.id,
        event="COMPLIANCE_FULFILLED",
        details="Applicant uploaded corrected document. Returned to current authority for review.",
        ip_address=request.remote_addr
    )
    db.session.add(tl)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Corrected file uploaded."})

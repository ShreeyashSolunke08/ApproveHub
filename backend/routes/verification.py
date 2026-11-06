import os
from flask import Blueprint, render_template, request, jsonify
from backend.models import Document, ApprovalStep, Timeline
from backend.utils.hashing import sha256_file

verification_bp = Blueprint("verification", __name__)

@verification_bp.route("/verify", methods=["GET"])
@verification_bp.route("/verify/<string:approval_no>", methods=["GET"])
def public_verify_page(approval_no=None):
    query_no = approval_no or request.args.get("number", "").strip()
    result = None
    not_found = False
    
    if query_no:
        step = ApprovalStep.query.filter_by(approval_no=query_no).first()
        if step and step.document:
            doc = step.document
            approved_steps = [s for s in doc.approval_steps if s.status == "approved"]
            result = {
                "approval_no": query_no,
                "document_title": doc.title,
                "status": doc.status,
                "institution_name": doc.institution.name if doc.institution else "VIT Pune",
                "original_hash": doc.original_hash,
                "final_hash": doc.final_hash or "Pending final signoff",
                "approved_steps": approved_steps,
                "created_at": doc.created_at.strftime("%d %b %Y, %H:%M UTC") if doc.created_at else ""
            }
        else:
            not_found = True
            
    return render_template("verify.html", query_no=query_no, result=result, not_found=not_found)

@verification_bp.route("/api/verify/check", methods=["POST"])
def api_verify_check():
    data = request.get_json() or {}
    number = (data.get("number") or data.get("approval_no") or data.get("code") or "").strip()
    
    step = ApprovalStep.query.filter_by(approval_no=number).first()
    if not step or not step.document:
        return jsonify({"valid": False, "message": "No official approval record found for this code."}), 404
        
    doc = step.document
    return jsonify({
        "valid": True,
        "title": doc.title,
        "status": doc.status,
        "institution": doc.institution.name if doc.institution else "VIT Pune",
        "final_hash": doc.final_hash,
        "approvers": [
            {
                "name": s.approver.name,
                "designation": s.approver.designation,
                "date": s.acted_at.strftime("%d %b %Y, %H:%M") if s.acted_at else "Pending"
            }
            for s in doc.approval_steps if s.status == "approved"
        ]
    })

@verification_bp.route("/api/verify/upload-hash", methods=["POST"])
def verify_uploaded_file():
    """
    Public 'Upload to verify' check: drops a PDF, compares hash against all final_hash entries.
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"valid": False, "error": "No file uploaded."}), 400
        
    temp_path = os.path.join("uploads", "docs", f"temp_verify_{file.filename}")
    file.save(temp_path)
    file_hash = sha256_file(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    matching_doc = Document.query.filter_by(final_hash=file_hash).first()
    if matching_doc:
        return jsonify({
            "valid": True,
            "message": "Cryptographic match confirmed! Document is authentic and unchanged.",
            "title": matching_doc.title,
            "hash": file_hash,
            "status": matching_doc.status
        })
    else:
        return jsonify({
            "valid": False,
            "message": "Hash does not match any approved document. File may have been edited, compressed, or forged.",
            "hash": file_hash
        }), 400

@verification_bp.route("/scan-qr")
def scan_qr_page():
    return render_template("scan_qr.html")

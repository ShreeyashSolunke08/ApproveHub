import os
import pymupdf  # PyMuPDF
import qrcode
from PIL import Image
from datetime import datetime, timezone
from backend.utils.hashing import sha256_file, verify_file

def generate_qr_code_image(approval_no, verify_url, output_path):
    """
    Generates a crisp QR code pointing to public verification endpoint.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b2530", back_color="#ffffff")
    img.save(output_path)
    return output_path

def stamp_final_document(document, base_url="http://127.0.0.1:5000"):
    """
    Applies vector marks, approver assets, and public verification QR code at user-defined coordinates.
    Guarantees that original file remains 100% pristine and unaltered.
    """
    # 1. Tamper check before stamping
    if not verify_file(document.file_path, document.original_hash):
        raise ValueError("Original file failed cryptographic tamper check! Stamping aborted.")

    # 2. Open fresh copy of pristine original PDF
    doc = pymupdf.open(document.file_path)
    total_pages = len(doc)
    
    # 3. Apply each approved authority's mark at their designated coordinates
    for step in document.approval_steps:
        if step.status != "approved":
            continue

        target_page_idx = min(max(0, step.page_no - 1), total_pages - 1)
        page = doc[target_page_idx]
        
        page_w = page.rect.width
        page_h = page.rect.height

        # Convert 0.0-1.0 fraction to PDF typographical points
        stamp_w = 140.0
        stamp_h = 50.0
        
        raw_x = step.pos_x * page_w
        raw_y = step.pos_y * page_h
        
        # Clamp coordinates to ensure mark remains entirely within page boundaries
        margin = 15.0
        x0 = min(max(margin, raw_x), page_w - stamp_w - margin)
        y0 = min(max(margin, raw_y), page_h - stamp_h - margin)
        x1 = x0 + stamp_w
        y1 = y0 + stamp_h

        approver = step.approver
        name_text = f"{approver.name}"

        # Resolve signature file path (supports relative, absolute, and fallback paths)
        sig_file = None
        if approver.signature_path:
            abs_p = os.path.abspath(approver.signature_path)
            if os.path.exists(abs_p):
                sig_file = abs_p
            elif os.path.exists(approver.signature_path):
                sig_file = approver.signature_path

        # Fallback check for user-specific sketch in assets folder
        if not sig_file:
            alt_path = os.path.abspath(os.path.join("uploads", "assets", f"sig_{approver.id}_sketch.png"))
            if os.path.exists(alt_path):
                sig_file = alt_path

        # Render ONLY the approver's signature and their name underneath - nothing else
        if sig_file:
            sig_rect = pymupdf.Rect(x0, y0, x0 + 115.0, y0 + 32.0)
            page.insert_image(sig_rect, filename=sig_file, keep_proportion=True)
        else:
            # Professional digital signature calligraphy stroke in fountain pen ink
            sig_base_y = y0 + 20.0
            shape = page.new_shape()
            shape.draw_bezier(
                pymupdf.Point(x0 + 4.0, sig_base_y),
                pymupdf.Point(x0 + 22.0, sig_base_y - 15.0),
                pymupdf.Point(x0 + 36.0, sig_base_y + 7.0),
                pymupdf.Point(x0 + 58.0, sig_base_y - 11.0)
            )
            shape.draw_bezier(
                pymupdf.Point(x0 + 58.0, sig_base_y - 11.0),
                pymupdf.Point(x0 + 74.0, sig_base_y + 5.0),
                pymupdf.Point(x0 + 90.0, sig_base_y - 13.0),
                pymupdf.Point(x0 + 110.0, sig_base_y - 2.0)
            )
            shape.draw_bezier(
                pymupdf.Point(x0 + 110.0, sig_base_y - 2.0),
                pymupdf.Point(x0 + 60.0, sig_base_y + 8.0),
                pymupdf.Point(x0 + 20.0, sig_base_y + 7.0),
                pymupdf.Point(x0 + 115.0, sig_base_y + 8.0)
            )
            shape.finish(color=(0.04, 0.12, 0.28), width=1.3)
            shape.commit()

        # Clean approver name printed underneath the signature (no box, no badge, no date, no code)
        page.insert_text(
            pymupdf.Point(x0 + 4.0, y0 + 42.0),
            name_text,
            fontsize=9.5,
            fontname="helv",
            color=(0.06, 0.10, 0.16)
        )

    # 4. Stamp Dynamic Public Verification QR Code at user-configured position
    qr_target_page_idx = min(max(0, document.qr_page_no - 1 if document.qr_page_no > 0 else total_pages - 1), total_pages - 1)
    qr_page = doc[qr_target_page_idx]
    lp_w = qr_page.rect.width
    lp_h = qr_page.rect.height
    
    primary_app_no = document.approval_steps[-1].approval_no if document.approval_steps else f"AH-2026-{document.id}"
    verify_url = f"{base_url}/verify/{primary_app_no}"
    
    qr_filename = f"qr_{primary_app_no.replace('/', '_')}.png"
    qr_path = os.path.join(os.path.dirname(document.file_path), "..", "qr", qr_filename)
    generate_qr_code_image(primary_app_no, verify_url, qr_path)
    
    # Position QR badge from user coordinates
    qr_size = 54.0
    qr_raw_x = (document.qr_pos_x or 0.78) * lp_w
    qr_raw_y = (document.qr_pos_y or 0.03) * lp_h

    # Safety clamp to prevent off-page bleed
    qr_x = min(max(18.0, qr_raw_x), lp_w - qr_size - 18.0)
    qr_y = min(max(18.0, qr_raw_y), lp_h - qr_size - 28.0)
    qr_rect = pymupdf.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size)
    
    # Draw background box for QR block
    bg_qr_rect = pymupdf.Rect(qr_x - 6.0, qr_y - 6.0, qr_x + qr_size + 6.0, qr_y + qr_size + 24.0)
    qr_page.draw_rect(bg_qr_rect, color=(0.88, 0.86, 0.82), fill=(1, 1, 1), width=0.8)
    qr_page.insert_image(qr_rect, filename=qr_path)
    qr_page.insert_text(pymupdf.Point(qr_x - 2.0, qr_y + qr_size + 8.0), "Scan to Verify", fontsize=6.5, fontname="helv", color=(0.06, 0.46, 0.43))
    qr_page.insert_text(pymupdf.Point(qr_x - 4.0, qr_y + qr_size + 17.0), "ApproveHub ✓", fontsize=6.0, fontname="helv", color=(0.4, 0.4, 0.4))

    # 5. Save stamped output as dedicated final PDF
    final_dir = os.path.join(os.path.dirname(document.file_path), "..", "final")
    os.makedirs(final_dir, exist_ok=True)
    final_filename = f"approved_doc_{document.id}_{primary_app_no}.pdf"
    final_output_path = os.path.join(final_dir, final_filename)
    
    doc.save(final_output_path)
    doc.close()

    # 6. Compute SHA-256 fingerprint of the final document
    final_hash = sha256_file(final_output_path)
    return final_output_path, final_hash

def restamp_user_approved_documents(user_id, base_url="http://127.0.0.1:5000"):
    """
    Automatically re-stamps all approved documents where user_id is an approver,
    ensuring newly drawn/updated signatures reflect immediately on all finalized documents.
    """
    from backend.models import db, Document, ApprovalStep
    try:
        steps = ApprovalStep.query.filter_by(approver_id=user_id, status="approved").all()
        doc_ids = set(s.document_id for s in steps)
        for doc_id in doc_ids:
            doc = Document.query.get(doc_id)
            if doc and doc.status == "approved":
                try:
                    final_path, final_hash = stamp_final_document(doc, base_url=base_url)
                    doc.final_path = final_path
                    doc.final_hash = final_hash
                except Exception as e:
                    print(f"[RE-STAMP] Could not restamp doc {doc_id}: {e}")
        db.session.commit()
    except Exception as e:
        print(f"[RE-STAMP] Error: {e}")

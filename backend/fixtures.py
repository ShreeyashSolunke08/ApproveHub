import os
import pymupdf
from datetime import datetime, timezone, timedelta
from backend.models import db, Institution, User, Document, ApprovalStep, Timeline
from backend.utils.hashing import sha256_file, generate_record_hash
from backend.utils.stamping import stamp_final_document

def create_sample_pdf(filepath):
    """
    Creates a clean official university template PDF using PyMuPDF.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # Standard A4 (points)

    # Draw header banner
    banner_rect = pymupdf.Rect(36, 36, 559, 105)
    page.draw_rect(banner_rect, color=(0.06, 0.46, 0.43), fill=(0.95, 0.98, 0.97), width=1.5)
    page.insert_text(pymupdf.Point(52, 64), "VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE", fontsize=13, fontname="helv", color=(0.04, 0.15, 0.19))
    page.insert_text(pymupdf.Point(52, 80), "Department of Information Technology — EDI Academic Office", fontsize=9.5, fontname="helv", color=(0.06, 0.46, 0.43))
    page.insert_text(pymupdf.Point(52, 94), "Official Document Approval & Tamper-Evident Verification Slip", fontsize=8.5, fontname="helv", color=(0.37, 0.44, 0.46))

    # Document body
    page.insert_text(pymupdf.Point(52, 145), "APPLICATION FOR BONAFIDE & NOC CERTIFICATE", fontsize=12, fontname="helv", color=(0.04, 0.15, 0.19))
    
    body_lines = [
        "To,",
        "The Head of Department / Academic Dean,",
        "Department of Information Technology, VIT Pune.",
        "",
        "Respected Sir/Madam,",
        "",
        "I am submitting this official request for institutional approval and issuance of my Bonafide",
        "Certificate for the academic year 2026. All required credentials and semester enrollment",
        "details have been verified against the college ERP records.",
        "",
        "Student Name   : Shreeyash Solunke",
        "PRN / Roll No  : 2026-IT-0412",
        "Branch / Class : B.Tech Information Technology (F.Y.)",
        "Purpose        : Industry Internship & Project Evaluation",
        "",
        "Kindly review, approve, and apply the official digital authority signatures and departmental stamps.",
        "",
        "Yours obediently,",
        "Shreeyash Solunke (Applicant)",
        "------------------------------------------------------------------------------------------------------------------"
    ]
    
    y = 175
    for line in body_lines:
        page.insert_text(pymupdf.Point(52, y), line, fontsize=9.5, fontname="helv", color=(0.15, 0.2, 0.25))
        y += 18
        
    # Printable marks area guideline
    footer_box = pymupdf.Rect(45, 620, 550, 780)
    page.draw_rect(footer_box, color=(0.7, 0.8, 0.8), width=0.8, dashes="[3 3]")
    page.insert_text(pymupdf.Point(55, 635), "AUTHORITY STAMPS & ENDORSEMENT ZONE (ApproveHub Protected)", fontsize=7.5, fontname="helv", color=(0.4, 0.5, 0.5))

    doc.save(filepath)
    doc.close()
    return filepath

def seed_database(app):
    """
    Populates database with initial institutional hierarchy, sample users, and demo workflow.
    """
    with app.app_context():
        db.create_all()
        
        # 1. Institution
        inst = Institution.query.first()
        if not inst:
            inst = Institution(
                name="Vishwakarma Institute of Technology, Pune",
                code="VITP",
                sequential_enforced=True,
                require_pin=True,
                auto_expire_days=14
            )
            db.session.add(inst)
            db.session.commit()
            
        # 2. Users
        if User.query.count() == 0:
            users_data = [
                {
                    "name": "Shreeyash Solunke",
                    "email": "shreeyash@vit.edu",
                    "role": "applicant",
                    "department": "Information Technology",
                    "designation": "Student (F.Y. B.Tech)"
                },
                {
                    "name": "Prof. Meera Kulkarni",
                    "email": "prof.kulkarni@vit.edu",
                    "role": "approver",
                    "department": "Information Technology",
                    "designation": "Professor"
                },
                {
                    "name": "Dr. R. Patil",
                    "email": "dr.patil@vit.edu",
                    "role": "approver",
                    "department": "Information Technology",
                    "designation": "HOD"
                },
                {
                    "name": "Dr. V. Rao",
                    "email": "dr.rao@vit.edu",
                    "role": "approver",
                    "department": "Computer Engineering",
                    "designation": "Dean Academics"
                },
                {
                    "name": "Institutional Admin",
                    "email": "admin@vit.edu",
                    "role": "admin",
                    "department": "Administration",
                    "designation": "System Controller"
                },
                {
                    "name": "Aditi Kulkarni",
                    "email": "aditi@vit.edu",
                    "role": "applicant",
                    "department": "Information Technology",
                    "designation": "Student (S.Y. B.Tech)"
                }
            ]
            
            created_users = {}
            for u in users_data:
                user_obj = User(
                    institution_id=inst.id,
                    name=u["name"],
                    email=u["email"],
                    role=u["role"],
                    department=u["department"],
                    designation=u["designation"]
                )
                user_obj.set_password("password123")
                user_obj.set_pin("1234")
                db.session.add(user_obj)
                created_users[u["email"]] = user_obj
                
            db.session.commit()
            
        # 3. Create sample document if none exists
        if Document.query.count() == 0:
            sample_pdf_path = os.path.join(app.config["DOCS_FOLDER"], "bonafide_request.pdf")
            create_sample_pdf(sample_pdf_path)
            orig_hash = sha256_file(sample_pdf_path)
            
            shreeyash = User.query.filter_by(email="shreeyash@vit.edu").first()
            prof = User.query.filter_by(email="prof.kulkarni@vit.edu").first()
            hod = User.query.filter_by(email="dr.patil@vit.edu").first()
            
            doc1 = Document(
                institution_id=inst.id,
                applicant_id=shreeyash.id,
                title="Bonafide Certificate Request",
                file_path=sample_pdf_path,
                original_hash=orig_hash,
                status="in_progress",
                current_step=2,
                total_steps=2
            )
            db.session.add(doc1)
            db.session.commit()
            
            now = datetime.now(timezone.utc)
            
            # Step 1: Approved by Prof. Meera Kulkarni
            step1 = ApprovalStep(
                document_id=doc1.id,
                approver_id=prof.id,
                step_order=1,
                mark_type="signature",
                page_no=1,
                pos_x=0.10,
                pos_y=0.77,
                status="approved",
                approval_no="AH-26-IT-0412-7KQ3",
                acted_at=now - timedelta(hours=2),
                remark="Verified academic eligibility. Approved."
            )
            step1.record_hash = generate_record_hash(doc1.id, 1, prof.id, step1.approval_no, (now - timedelta(hours=2)).isoformat())
            db.session.add(step1)
            
            # Step 2: Waiting for HOD (Dr. R. Patil)
            step2 = ApprovalStep(
                document_id=doc1.id,
                approver_id=hod.id,
                step_order=2,
                mark_type="stamp",
                page_no=1,
                pos_x=0.55,
                pos_y=0.77,
                status="pending",
                approval_no="AH-26-IT-0412-9LM4"
            )
            db.session.add(step2)
            
            # Timeline events
            tl1 = Timeline(
                document_id=doc1.id,
                user_id=shreeyash.id,
                event="DOCUMENT_UPLOADED",
                details=f"Document '{doc1.title}' submitted. Fingerprint: {orig_hash[:16]}...",
                timestamp=now - timedelta(hours=3)
            )
            tl2 = Timeline(
                document_id=doc1.id,
                user_id=prof.id,
                event="STEP_APPROVED",
                details=f"Approved by {prof.name} ({prof.designation}). Moved to HOD.",
                timestamp=now - timedelta(hours=2)
            )
            db.session.add_all([tl1, tl2])
            db.session.commit()
            print("Database successfully seeded with realistic fixtures!")

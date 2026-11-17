"""
ApproveHub — Demo Profile Reset Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wipes all test/junk users and documents, then resets the 6 canonical
demo profiles to a clean, presentation-ready state.

Run:  python reset_demo_profiles.py

Demo Credentials (all use password: demo1234 / PIN: 1234)
----------------------------------------------------------
  shreeyash@vit.edu   → Applicant  (F.Y. B.Tech student)
  aditi@vit.edu       → Applicant  (S.Y. B.Tech student)
  prof.kulkarni@vit.edu → Approver (Faculty Guide)
  dr.patil@vit.edu    → Approver   (HOD - IT)
  dr.rao@vit.edu      → Approver   (Dean Academics)
  admin@vit.edu       → Admin      (System Controller)
"""

import sys, os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from backend.models import db, User, Institution, Document, ApprovalStep, Timeline
from backend.utils.hashing import sha256_file, generate_record_hash
from datetime import datetime, timezone, timedelta

DEMO_PASSWORD = "demo1234"
DEMO_PIN      = "1234"

DEMO_PROFILES = [
    # ── Students ─────────────────────────────────────────────
    {
        "email": "shreeyash@vit.edu",
        "name": "Shreeyash Solunke",
        "role": "applicant",
        "department": "Information Technology",
        "designation": "Student (F.Y. B.Tech)",
    },
    {
        "email": "aditi@vit.edu",
        "name": "Aditi Kulkarni",
        "role": "applicant",
        "department": "Information Technology",
        "designation": "Student (S.Y. B.Tech)",
    },
    {
        "email": "rahul.sharma@vit.edu",
        "name": "Rahul Sharma",
        "role": "applicant",
        "department": "Information Technology",
        "designation": "Student (T.Y. B.Tech)",
    },
    {
        "email": "priya.desai@vit.edu",
        "name": "Priya Desai",
        "role": "applicant",
        "department": "Information Technology",
        "designation": "Student (B.E. Final Year)",
    },
    # ── Faculty ───────────────────────────────────────────────
    {
        "email": "prof.kulkarni@vit.edu",
        "name": "Prof. Meera Kulkarni",
        "role": "approver",
        "department": "Information Technology",
        "designation": "Professor",
    },
    {
        "email": "dr.patil@vit.edu",
        "name": "Dr. R. Patil",
        "role": "approver",
        "department": "Information Technology",
        "designation": "HOD",
    },
    {
        "email": "dr.rao@vit.edu",
        "name": "Dr. V. Rao",
        "role": "approver",
        "department": "Computer Engineering",
        "designation": "Dean Academics",
    },
    # ── Admin ─────────────────────────────────────────────────
    {
        "email": "admin@vit.edu",
        "name": "Institutional Admin",
        "role": "admin",
        "department": "Administration",
        "designation": "System Controller",
    },
]

DEMO_EMAILS = {p["email"] for p in DEMO_PROFILES}


def ensure_default_signature(user):
    """Creates a clean transparent PNG signature for approver/admin seed users."""
    from PIL import Image, ImageDraw
    upload_dir = os.path.join("uploads", "assets")
    os.makedirs(upload_dir, exist_ok=True)
    target_path = os.path.join(upload_dir, f"sig_{user.id}_default.png")
    # Always regenerate for a clean slate
    img = Image.new("RGBA", (260, 80), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    points1 = [(25, 45), (45, 22), (65, 52), (90, 26), (115, 48), (145, 24), (175, 50), (210, 32), (240, 44)]
    points2 = [(35, 58), (95, 60), (165, 59), (245, 56)]
    d.line(points1, fill=(15, 23, 42, 245), width=3, joint="curve")
    d.line(points2, fill=(15, 23, 42, 220), width=2, joint="curve")
    img.save(target_path, format="PNG")
    user.signature_path = target_path


def reset_demo():
    app = create_app()
    with app.app_context():
        print("\n" + "=" * 65)
        print("  ApproveHub — Demo Profile Reset")
        print("=" * 65)

        # ── 1. Remove junk / test users (keep only the 6 demo accounts)
        all_users = User.query.all()
        junk_users = [u for u in all_users if u.email not in DEMO_EMAILS]
        if junk_users:
            print(f"\n[1] Removing {len(junk_users)} test/junk user(s)...")
            for u in junk_users:
                # Remove their documents + steps + timeline first
                for doc in Document.query.filter_by(applicant_id=u.id).all():
                    db.session.delete(doc)
                # Also nuke any approval steps where they are the approver
                for step in ApprovalStep.query.filter_by(approver_id=u.id).all():
                    db.session.delete(step)
                print(f"   - Deleted: {u.name} ({u.email})")
                db.session.delete(u)
            db.session.commit()
        else:
            print("\n[1] No junk users found — already clean.")

        # ── 2. Wipe ALL existing documents (clean slate for demo)
        doc_count = Document.query.count()
        if doc_count:
            print(f"\n[2] Wiping {doc_count} existing document(s) for a clean demo state...")
            for doc in Document.query.all():
                db.session.delete(doc)
            db.session.commit()
        else:
            print("\n[2] No documents to wipe.")

        # ── 3. Reset / create the 6 canonical demo accounts
        print("\n[3] Resetting demo profiles...")
        inst = Institution.query.first()
        if not inst:
            print("    ERROR: No institution found. Run the app once first (python app.py).")
            return

        for profile in DEMO_PROFILES:
            user = User.query.filter_by(email=profile["email"]).first()
            if not user:
                user = User(
                    institution_id=inst.id,
                    email=profile["email"],
                )
                db.session.add(user)
            # Reset all editable fields
            user.name           = profile["name"]
            user.role           = profile["role"]
            user.department     = profile["department"]
            user.designation    = profile["designation"]
            user.institution_id = inst.id
            user.mobile         = None
            user.avatar_path    = None
            user.avatar_url     = None
            user.reset_token    = None
            user.reset_token_expiry = None
            user.failed_pin_attempts = 0
            user.locked_until   = None
            user.email_verified = True
            user.is_active      = True
            user.set_password(DEMO_PASSWORD)
            user.set_pin(DEMO_PIN)
            db.session.commit()

            if user.role in ("approver", "admin"):
                ensure_default_signature(user)
                db.session.commit()

            print(f"   ✓ {user.role.upper():9s} | {user.name:25s} | {user.email}")

        # ── 4. Seed a fresh demo document workflow
        print("\n[4] Seeding demo document workflow...")
        shreeyash = User.query.filter_by(email="shreeyash@vit.edu").first()
        prof      = User.query.filter_by(email="prof.kulkarni@vit.edu").first()
        hod       = User.query.filter_by(email="dr.patil@vit.edu").first()
        dean      = User.query.filter_by(email="dr.rao@vit.edu").first()
        aditi     = User.query.filter_by(email="aditi@vit.edu").first()

        from backend.fixtures import create_sample_pdf
        sample_pdf = os.path.join(app.config["DOCS_FOLDER"], "bonafide_request.pdf")
        if not os.path.exists(sample_pdf):
            create_sample_pdf(sample_pdf)
        orig_hash = sha256_file(sample_pdf)

        now = datetime.now(timezone.utc)

        # ─ Doc A: In-Progress (1 of 2 steps done) — Shreeyash
        docA = Document(
            institution_id=inst.id,
            applicant_id=shreeyash.id,
            title="Bonafide Certificate Request",
            document_type="bonafide",
            file_path=sample_pdf,
            original_hash=orig_hash,
            status="in_progress",
            current_step=2,
            total_steps=2,
        )
        db.session.add(docA)
        db.session.commit()

        stepA1 = ApprovalStep(
            document_id=docA.id,
            approver_id=prof.id,
            step_order=1,
            mark_type="signature",
            page_no=1, pos_x=0.10, pos_y=0.77,
            status="approved",
            approval_no="AH-26-IT-0412-7KQ3",
            acted_at=now - timedelta(hours=2),
            remark="Verified academic eligibility. Approved."
        )
        stepA1.record_hash = generate_record_hash(
            docA.id, 1, prof.id, stepA1.approval_no,
            (now - timedelta(hours=2)).isoformat()
        )
        stepA2 = ApprovalStep(
            document_id=docA.id,
            approver_id=hod.id,
            step_order=2,
            mark_type="stamp",
            page_no=1, pos_x=0.55, pos_y=0.77,
            status="pending",
            approval_no="AH-26-IT-0412-9LM4",
        )
        db.session.add_all([stepA1, stepA2])

        db.session.add_all([
            Timeline(document_id=docA.id, user_id=shreeyash.id,
                     event="DOCUMENT_UPLOADED",
                     details=f"Bonafide request submitted. Fingerprint: {orig_hash[:16]}...",
                     timestamp=now - timedelta(hours=3)),
            Timeline(document_id=docA.id, user_id=prof.id,
                     event="STEP_APPROVED",
                     details=f"Approved by {prof.name} ({prof.designation}). Moved to HOD.",
                     timestamp=now - timedelta(hours=2)),
        ])
        db.session.commit()
        print(f"   ✓ Doc A (in_progress): '{docA.title}' — Shreeyash → awaiting HOD")

        # ─ Doc B: Fully Approved (2 of 2 steps) — Aditi
        docB = Document(
            institution_id=inst.id,
            applicant_id=aditi.id,
            title="NOC for Industry Internship",
            document_type="noc_project",
            file_path=sample_pdf,
            original_hash=orig_hash,
            status="approved",
            current_step=2,
            total_steps=2,
        )
        db.session.add(docB)
        db.session.commit()

        from backend.utils.security import generate_random_approval_no
        codeB1 = generate_random_approval_no(docB.id, 1, "IT")
        codeB2 = generate_random_approval_no(docB.id, 2, "IT")

        stepB1 = ApprovalStep(
            document_id=docB.id,
            approver_id=prof.id,
            step_order=1,
            mark_type="signature",
            page_no=1, pos_x=0.10, pos_y=0.77,
            status="approved",
            approval_no=codeB1,
            acted_at=now - timedelta(days=1, hours=5),
            remark="Eligibility confirmed by faculty guide."
        )
        stepB1.record_hash = generate_record_hash(
            docB.id, 1, prof.id, codeB1,
            (now - timedelta(days=1, hours=5)).isoformat()
        )
        stepB2 = ApprovalStep(
            document_id=docB.id,
            approver_id=hod.id,
            step_order=2,
            mark_type="both",
            page_no=1, pos_x=0.55, pos_y=0.77,
            status="approved",
            approval_no=codeB2,
            acted_at=now - timedelta(days=1),
            remark="Department clearance granted. NOC issued."
        )
        stepB2.record_hash = generate_record_hash(
            docB.id, 2, hod.id, codeB2,
            (now - timedelta(days=1)).isoformat()
        )
        db.session.add_all([stepB1, stepB2])

        db.session.add_all([
            Timeline(document_id=docB.id, user_id=aditi.id,
                     event="DOCUMENT_UPLOADED",
                     details="NOC for internship submitted.",
                     timestamp=now - timedelta(days=1, hours=6)),
            Timeline(document_id=docB.id, user_id=prof.id,
                     event="STEP_APPROVED",
                     details=f"Tier 1 approved by {prof.name}.",
                     timestamp=now - timedelta(days=1, hours=5)),
            Timeline(document_id=docB.id, user_id=hod.id,
                     event="FINAL_APPROVED",
                     details=f"Final authorization by {hod.name}. Document fully approved.",
                     timestamp=now - timedelta(days=1)),
        ])
        db.session.commit()
        print(f"   ✓ Doc B (approved):    'NOC for Industry Internship' — Aditi (fully signed)")

        # ─ Doc C: Pending (fresh upload, awaiting Tier 1) — Shreeyash
        docC = Document(
            institution_id=inst.id,
            applicant_id=shreeyash.id,
            title="Research Grant Application (EDI)",
            document_type="grant_research",
            file_path=sample_pdf,
            original_hash=orig_hash,
            status="pending",
            current_step=1,
            total_steps=3,
        )
        db.session.add(docC)
        db.session.commit()

        codeC_step1 = generate_random_approval_no(docC.id, 1, "IT")

        stepC1 = ApprovalStep(
            document_id=docC.id,
            approver_id=prof.id,
            step_order=1,
            mark_type="signature",
            page_no=1, pos_x=0.08, pos_y=0.74,
            status="pending",
            approval_no=codeC_step1,
        )
        stepC2 = ApprovalStep(
            document_id=docC.id,
            approver_id=hod.id,
            step_order=2,
            mark_type="stamp",
            page_no=1, pos_x=0.42, pos_y=0.74,
            status="waiting",
        )
        stepC3 = ApprovalStep(
            document_id=docC.id,
            approver_id=dean.id,
            step_order=3,
            mark_type="both",
            page_no=1, pos_x=0.70, pos_y=0.74,
            status="waiting",
        )
        db.session.add_all([stepC1, stepC2, stepC3])

        db.session.add(Timeline(
            document_id=docC.id, user_id=shreeyash.id,
            event="DOCUMENT_UPLOADED",
            details="Research grant application submitted for 3-tier review.",
            timestamp=now - timedelta(minutes=30)
        ))
        db.session.commit()
        print(f"   ✓ Doc C (pending):     'Research Grant Application (EDI)' — 3-tier chain")

        # ── 5. Summary
        print("\n" + "=" * 65)
        print("  RESET COMPLETE — Demo credentials:")
        print("  Password : demo1234")
        print("  PIN      : 1234")
        print("=" * 65)
        print(f"\n  shreeyash@vit.edu   → Applicant (2 docs)")
        print(f"  aditi@vit.edu       → Applicant (1 approved doc)")
        print(f"  prof.kulkarni@vit.edu → Approver (1 pending inbox item)")
        print(f"  dr.patil@vit.edu    → Approver (1 inbox item)")
        print(f"  dr.rao@vit.edu      → Approver (waiting for chain)")
        print(f"  admin@vit.edu       → Admin")
        print()


if __name__ == "__main__":
    reset_demo()

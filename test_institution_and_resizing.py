import unittest
import os
import io
from app import create_app
from backend.models import db, User, Institution, Document, ApprovalStep
from backend.utils.stamping import stamp_final_document

class TestInstitutionAndResizing(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_institution_creation_and_joining(self):
        """Test establishing an institution and user joining via invite code."""
        # 1. Establish new Institution
        resp = self.client.post("/institution/create", data={
            "institution_name": "Indian Institute of Science, Bangalore",
            "institution_code": "IISCB",
            "admin_name": "Dr. Registrar",
            "admin_email": "registrar@iisc.ac.in",
            "admin_password": "securepassword123",
            "department": "Dean Office"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        inst = Institution.query.filter_by(code="IISCB").first()
        self.assertIsNotNone(inst)
        self.assertTrue(bool(inst.invite_code))

        # Logout admin before registering new user
        self.client.get("/logout", follow_redirects=True)

        # 2. Join via Invite Code
        join_resp = self.client.post("/institution/join", data={
            "code": inst.invite_code,
            "name": "Arya Stark",
            "email": "arya@iisc.ac.in",
            "password": "mypassword123",
            "role": "applicant",
            "department": "Computer Science"
        }, follow_redirects=True)
        self.assertEqual(join_resp.status_code, 200)

        new_user = User.query.filter_by(email="arya@iisc.ac.in").first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.institution_id, inst.id)

        # 3. Test QR code generation endpoint
        qr_resp = self.client.get(f"/institution/{inst.id}/qr")
        self.assertEqual(qr_resp.status_code, 200)
        self.assertEqual(qr_resp.mimetype, "image/png")

    def test_email_verification_and_google_linking(self):
        """Test email verification and Google account linking on user profile."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1  # Shreeyash

        # 1. Generate Email Verification code
        v_resp = self.client.post("/profile", data={
            "action": "send_email_verification"
        }, follow_redirects=True)
        self.assertEqual(v_resp.status_code, 200)

        u = User.query.get(1)
        self.assertIsNotNone(u.email_verification_token)

        # 2. Confirm verification code
        c_resp = self.client.post("/profile", data={
            "action": "verify_email_code",
            "verification_code": u.email_verification_token
        }, follow_redirects=True)
        self.assertEqual(c_resp.status_code, 200)

        u_verified = User.query.get(1)
        self.assertTrue(u_verified.email_verified)

        # 3. Link Google account
        g_resp = self.client.post("/profile", data={
            "action": "link_google_account",
            "google_email": "shreeyash.google@vit.edu"
        }, follow_redirects=True)
        self.assertEqual(g_resp.status_code, 200)

        u_google = User.query.get(1)
        self.assertEqual(u_google.google_email, "shreeyash.google@vit.edu")

    def test_document_page_rendering_and_custom_mark_sizes(self):
        """Test real PDF page rendering endpoint and custom mark width/height/qr sizing."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Use or create an independent document so document 1 remains intact
        user = User.query.get(1)
        doc = Document.query.filter(Document.id > 1).first()
        if not doc:
            doc = Document(
                institution_id=1,
                applicant_id=1,
                title="Test Custom Sizing Request",
                document_type="bonafide",
                file_path="uploads/docs/bonafide_request.pdf",
                original_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
                status="pending",
                current_step=1,
                total_steps=1,
                qr_pos_x=0.78,
                qr_pos_y=0.03,
                qr_page_no=1,
                qr_size=54.0
            )
            db.session.add(doc)
            db.session.commit()

        # 1. Test pages-info endpoint
        info_resp = self.client.get(f"/api/documents/{doc.id}/pages-info")
        self.assertEqual(info_resp.status_code, 200)
        info_json = info_resp.get_json()
        self.assertIn("total_pages", info_json)

        # 2. Test page rendering endpoint (returns PNG of real uploaded document)
        render_resp = self.client.get(f"/api/documents/{doc.id}/page/1/render")
        self.assertEqual(render_resp.status_code, 200)
        self.assertEqual(render_resp.mimetype, "image/png")
        self.assertGreater(len(render_resp.data), 1000)

        # 3. Test placing marks with custom width, height, and QR size
        approver = User.query.filter_by(role="approver").first()
        place_resp = self.client.post(f"/documents/{doc.id}/place", json={
            "steps": [{
                "approver_id": approver.id,
                "page_no": 1,
                "pos_x": 0.15,
                "pos_y": 0.65,
                "width_pts": 180.0,
                "height_pts": 65.0,
                "mark_type": "stamp"
            }],
            "qr_position": {
                "pos_x": 0.70,
                "pos_y": 0.05,
                "page_no": 1,
                "qr_size": 68.0
            }
        })
        self.assertEqual(place_resp.status_code, 200)

        updated_doc = Document.query.get(doc.id)
        self.assertEqual(updated_doc.qr_size, 68.0)
        step = ApprovalStep.query.filter_by(document_id=doc.id).first()
        self.assertEqual(step.width_pts, 180.0)
        self.assertEqual(step.height_pts, 65.0)

if __name__ == "__main__":
    unittest.main()

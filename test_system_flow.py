import os
import unittest
from app import create_app
from backend.models import db, User, Document, ApprovalStep, Timeline
from backend.utils.hashing import sha256_file, verify_file

class ApproveHubSystemTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_01_public_verify_seeded_document(self):
        """Test public verify portal returns valid status for sample approval code"""
        resp = self.client.get("/verify/AH-26-IT-0412-7KQ3")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Valid Institutional Approval", resp.data)

    def test_02_pin_brute_force_protection(self):
        """Test 5 failed PIN attempts triggers account lockout (Problem #6)"""
        with self.app.app_context():
            user = User.query.filter_by(email="prof.kulkarni@vit.edu").first()
            user.set_pin("1234")
            user.failed_pin_attempts = 0
            user.locked_until = None
            db.session.commit()

            # 4 wrong attempts
            for i in range(4):
                ok, msg = user.check_pin("9999")
                self.assertFalse(ok)
                self.assertIn("remaining", msg)

            # 5th wrong attempt triggers lock
            ok, msg = user.check_pin("9999")
            self.assertFalse(ok)
            self.assertIn("locked for 15 minutes", msg)

            # 6th attempt is blocked even if correct PIN is supplied
            ok, msg = user.check_pin("1234")
            self.assertFalse(ok)
            self.assertIn("Account locked", msg)

    def test_03_tamper_detection(self):
        """Test file alteration changes hash and triggers tamper alarm (Problem #4)"""
        test_path = "uploads/docs/test_tamper.txt"
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        with open(test_path, "w") as f:
            f.write("Original content for approval.")
        
        orig_hash = sha256_file(test_path)
        self.assertTrue(verify_file(test_path, orig_hash))

        # Alter one single byte
        with open(test_path, "w") as f:
            f.write("Altered content for approval.")

        # Verification must now fail!
        self.assertFalse(verify_file(test_path, orig_hash))
        if os.path.exists(test_path):
            os.remove(test_path)

    def test_04_full_approval_and_stamping_flow(self):
        """Test complete workflow: Approver 2 signs off and PyMuPDF stamps final document"""
        with self.app.app_context():
            doc = Document.query.filter_by(title="Bonafide Certificate Request").first()
            self.assertIsNotNone(doc)
            
            # Normalize path for local runner
            local_doc_path = os.path.join("uploads", "docs", "bonafide_request.pdf")
            if os.path.exists(local_doc_path):
                doc.file_path = os.path.abspath(local_doc_path)
                doc.original_hash = sha256_file(doc.file_path)
                
            step2 = ApprovalStep.query.filter_by(document_id=doc.id, step_order=2).first()
            self.assertIsNotNone(step2)
            step2.status = "pending"
            db.session.commit()

            hod = User.query.get(step2.approver_id)

            # Log in as HOD
            with self.client.session_transaction() as sess:
                sess["user_id"] = hod.id
                sess["user_name"] = hod.name
                sess["user_role"] = hod.role

            # Approve Step 2 with valid PIN
            resp = self.client.post(
                f"/api/steps/{step2.id}/action",
                json={
                    "action": "approve",
                    "pin": "1234",
                    "remark": "Approved by HOD with digital seal."
                }
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], "approved")

            # Check database for final stamped path and hash
            updated_doc = Document.query.get(doc.id)
            self.assertEqual(updated_doc.status, "approved")
            self.assertIsNotNone(updated_doc.final_path)
            self.assertTrue(os.path.exists(updated_doc.final_path))
            self.assertIsNotNone(updated_doc.final_hash)
            self.assertEqual(len(updated_doc.final_hash), 64)

            # Verify the final PDF file matches final_hash
            self.assertTrue(verify_file(updated_doc.final_path, updated_doc.final_hash))

if __name__ == "__main__":
    unittest.main()

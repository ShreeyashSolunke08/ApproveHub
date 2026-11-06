import unittest
import json
import time
from app import create_app
from backend.models import db, User, Document, ApprovalStep
from backend.utils.rate_limiter import clear_rate_limits
from backend.utils.mailer import get_latest_emails

class TestProductionFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clear_rate_limits()

    def tearDown(self):
        clear_rate_limits()
        self.app_context.pop()

    def test_email_dispatch_on_forgot_password(self):
        """Test transactional email is queued/sent on password reset request."""
        user = User.query.filter_by(role="applicant").first()
        self.assertIsNotNone(user)

        resp = self.client.post("/api/auth/forgot-password", json={
            "email": user.email
        })
        self.assertEqual(resp.status_code, 200)
        
        # Verify dispatched email buffer
        emails = get_latest_emails()
        self.assertTrue(len(emails) > 0)
        last_email = emails[0]
        self.assertEqual(last_email["to"], user.email)
        self.assertIn("Password Reset Request", last_email["subject"])
        self.assertIn("reset-password", last_email["html"])

    def test_rate_limiter_blocks_abuse(self):
        """Test IP rate limiter responds with HTTP 429 when request limits are exceeded."""
        clear_rate_limits()
        user = User.query.filter_by(role="applicant").first()
        
        # Send 15 rapid failed requests (limit is 15/min)
        hit_429 = False
        for _ in range(18):
            resp = self.client.post("/api/auth/login", json={
                "email": user.email,
                "password": "wrong_password_flood"
            })
            if resp.status_code == 429:
                hit_429 = True
                self.assertIn("Retry-After", resp.headers)
                break
                
        self.assertTrue(hit_429, "Rate limiter should have returned HTTP 429 for request flooding")

    def test_batch_approval_action(self):
        """Test approving multiple documents at once via /api/steps/batch-action."""
        approver = User.query.filter_by(role="approver").first()
        self.assertIsNotNone(approver)
        approver.set_pin("1234")
        db.session.commit()

        # Find pending steps for this approver
        pending_steps = ApprovalStep.query.filter_by(
            approver_id=approver.id,
            status="pending"
        ).limit(2).all()

        if pending_steps:
            step_ids = [s.id for s in pending_steps]

            # Log in as approver
            with self.client.session_transaction() as sess:
                sess["user_id"] = approver.id
                sess["user_name"] = approver.name
                sess["user_role"] = approver.role

            # 1. Test invalid PIN
            fail_resp = self.client.post("/api/steps/batch-action", json={
                "step_ids": step_ids,
                "action": "approve",
                "pin": "9999",
                "remark": "Batch test"
            })
            self.assertEqual(fail_resp.status_code, 400)

            # 2. Test valid PIN
            success_resp = self.client.post("/api/steps/batch-action", json={
                "step_ids": step_ids,
                "action": "approve",
                "pin": "1234",
                "remark": "Approved in batch by Department Authority"
            })
            self.assertEqual(success_resp.status_code, 200)
            data = success_resp.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(data["processed_count"], len(step_ids))

if __name__ == "__main__":
    unittest.main()

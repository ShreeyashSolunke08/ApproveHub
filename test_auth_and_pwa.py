import unittest
import json
import os
import io
from app import create_app
from backend.models import db, User, Institution, Document, ApprovalStep

class TestAuthAndPWA(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_pwa_assets_accessible(self):
        """Verify PWA manifest, service worker, and icons exist and are served."""
        res_manifest = self.client.get("/static/manifest.json")
        self.assertEqual(res_manifest.status_code, 200)
        manifest_data = json.loads(res_manifest.data)
        self.assertEqual(manifest_data["name"], "ApproveHub — Digital Document Approval System")
        self.assertEqual(manifest_data["display"], "standalone")

        res_sw = self.client.get("/static/sw.js")
        self.assertEqual(res_sw.status_code, 200)
        self.assertIn(b"approvehub-v1", res_sw.data)

        res_icon = self.client.get("/static/img/icon-192.png")
        self.assertEqual(res_icon.status_code, 200)
        self.assertEqual(res_icon.mimetype, "image/png")

    def test_avatar_endpoint_svg_fallback(self):
        """Verify /user/avatar/<id> produces crisp SVG monogram avatar."""
        user = User.query.first()
        self.assertIsNotNone(user)
        res = self.client.get(f"/user/avatar/{user.id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("image/svg+xml", res.mimetype)
        self.assertIn(b"<svg", res.data)

    def test_auth_api_login_and_me(self):
        """Verify REST API login and /api/auth/me session check."""
        user = User.query.filter_by(role="applicant").first()
        self.assertIsNotNone(user)

        # 1. Invalid login
        res_fail = self.client.post("/api/auth/login", json={
            "email": user.email,
            "password": "wrong_password_xyz"
        })
        self.assertEqual(res_fail.status_code, 401)
        self.assertFalse(res_fail.get_json()["success"])

        # 2. Valid login
        res_ok = self.client.post("/api/auth/login", json={
            "email": user.email,
            "password": "password123",
            "remember": True
        })
        self.assertEqual(res_ok.status_code, 200)
        data = res_ok.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], user.email)

        # 3. /api/auth/me check
        res_me = self.client.get("/api/auth/me")
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.get_json()["user"]["id"], user.id)

    def test_auth_api_register_and_password_lifecycle(self):
        """Verify registration, password change, forgot password, and reset password APIs."""
        test_email = f"student_test_{os.urandom(4).hex()}@vit.edu"

        # 1. Register API
        res_reg = self.client.post("/api/auth/register", json={
            "name": "Test Candidate",
            "email": test_email,
            "password": "initial_password_123",
            "mobile": "+91 9123456789",
            "role": "applicant",
            "department": "Computer Engineering",
            "designation": "S.Y. B.Tech"
        })
        self.assertEqual(res_reg.status_code, 201)
        reg_data = res_reg.get_json()
        self.assertTrue(reg_data["success"])
        new_user_id = reg_data["user"]["id"]

        # 2. Change password API
        res_change = self.client.post("/api/auth/change-password", json={
            "old_password": "initial_password_123",
            "new_password": "updated_secret_pwd_456"
        })
        self.assertEqual(res_change.status_code, 200)

        # Verify old password no longer works
        self.client.get("/api/auth/logout")
        res_fail_old = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "initial_password_123"
        })
        self.assertEqual(res_fail_old.status_code, 401)

        # 3. Forgot password API
        res_forgot = self.client.post("/api/auth/forgot-password", json={
            "email": test_email
        })
        self.assertEqual(res_forgot.status_code, 200)
        forgot_data = res_forgot.get_json()
        self.assertTrue(forgot_data["success"])
        reset_token = forgot_data["token"]
        self.assertTrue(bool(reset_token))

        # 4. Reset password API
        res_reset = self.client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "password": "final_brand_new_pwd_789"
        })
        self.assertEqual(res_reset.status_code, 200)

        # 5. Log in with reset password
        res_new_login = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "final_brand_new_pwd_789"
        })
        self.assertEqual(res_new_login.status_code, 200)
        self.assertTrue(res_new_login.get_json()["success"])

if __name__ == "__main__":
    unittest.main()

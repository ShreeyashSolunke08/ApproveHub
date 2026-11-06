import secrets
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class Institution(db.Model):
    __tablename__ = "institutions"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
    sequential_enforced = db.Column(db.Boolean, default=True)
    require_pin = db.Column(db.Boolean, default=True)
    auto_expire_days = db.Column(db.Integer, default=14)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    users = db.relationship("User", backref="institution", lazy=True)
    documents = db.relationship("Document", backref="institution", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "sequential_enforced": self.sequential_enforced,
            "require_pin": self.require_pin,
            "auto_expire_days": self.auto_expire_days
        }

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="applicant")  # applicant | approver | admin
    department = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    signature_path = db.Column(db.String(255), nullable=True)
    stamp_path = db.Column(db.String(255), nullable=True)
    seal_path = db.Column(db.String(255), nullable=True)
    pin_hash = db.Column(db.String(255), nullable=True)
    failed_pin_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    google_id = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    avatar_path = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationships
    submitted_documents = db.relationship("Document", backref="applicant", lazy=True, foreign_keys="Document.applicant_id")
    approval_steps = db.relationship("ApprovalStep", backref="approver", lazy=True, foreign_keys="ApprovalStep.approver_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(24)
        self.reset_token_expiry = utc_now() + timedelta(hours=2)
        return self.reset_token

    def verify_reset_token(self, token):
        if not self.reset_token or self.reset_token != token:
            return False
        if not self.reset_token_expiry:
            return False
        now = utc_now()
        exp = self.reset_token_expiry.replace(tzinfo=timezone.utc) if self.reset_token_expiry.tzinfo is None else self.reset_token_expiry
        return now <= exp

    def set_pin(self, pin_str):
        self.pin_hash = generate_password_hash(str(pin_str).strip())
        self.failed_pin_attempts = 0
        self.locked_until = None

    def check_pin(self, pin_str):
        now = utc_now()
        # Check lockout
        if self.locked_until:
            lock_time = self.locked_until.replace(tzinfo=timezone.utc) if self.locked_until.tzinfo is None else self.locked_until
            if lock_time > now:
                remaining_secs = int((lock_time - now).total_seconds())
                return False, f"Account locked due to too many failed PIN attempts. Try again in {remaining_secs // 60 + 1} minutes."
            else:
                self.failed_pin_attempts = 0
                self.locked_until = None

        if not self.pin_hash:
            return False, "No PIN has been configured for this account. Please set a PIN first."

        if check_password_hash(self.pin_hash, str(pin_str).strip()):
            self.failed_pin_attempts = 0
            self.locked_until = None
            return True, "PIN verified successfully."
        else:
            self.failed_pin_attempts += 1
            if self.failed_pin_attempts >= 5:
                self.locked_until = now + timedelta(minutes=15)
                return False, "5 consecutive incorrect attempts! Account locked for 15 minutes."
            remaining = 5 - self.failed_pin_attempts
            return False, f"Incorrect PIN. {remaining} attempt(s) remaining before temporary lockout."

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "mobile": self.mobile,
            "role": self.role,
            "department": self.department,
            "designation": self.designation,
            "avatar_url": self.avatar_url or f"/user/avatar/{self.id}",
            "has_pin": bool(self.pin_hash),
            "is_active": self.is_active,
            "institution_id": self.institution_id
        }

class Document(db.Model):
    __tablename__ = "documents"
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), default="bonafide", nullable=False)  # bonafide, leave_student, noc_project, leave_faculty, grant_research, purchase_indent, etc.
    file_path = db.Column(db.String(255), nullable=False)
    original_hash = db.Column(db.String(64), nullable=False)  # 64-char SHA-256
    final_path = db.Column(db.String(255), nullable=True)
    final_hash = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(30), default="pending", nullable=False)  # draft | pending | in_progress | approved | compliance | rejected
    current_step = db.Column(db.Integer, default=1)
    total_steps = db.Column(db.Integer, default=1)
    qr_pos_x = db.Column(db.Float, default=0.78, nullable=False)
    qr_pos_y = db.Column(db.Float, default=0.03, nullable=False)
    qr_page_no = db.Column(db.Integer, default=1, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    approval_steps = db.relationship("ApprovalStep", backref="document", lazy=True, cascade="all, delete-orphan", order_by="ApprovalStep.step_order")
    timeline_events = db.relationship("Timeline", backref="document", lazy=True, cascade="all, delete-orphan", order_by="Timeline.timestamp.asc()")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "document_type": self.document_type,
            "applicant_name": self.applicant.name if self.applicant else "Unknown",
            "applicant_id": self.applicant_id,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "original_hash": self.original_hash,
            "final_hash": self.final_hash,
            "has_final_pdf": bool(self.final_path),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ApprovalStep(db.Model):
    __tablename__ = "approval_steps"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    mark_type = db.Column(db.String(20), default="signature", nullable=False)  # signature | stamp | seal
    page_no = db.Column(db.Integer, default=1, nullable=False)
    pos_x = db.Column(db.Float, nullable=False, default=0.1)  # 0.0 to 1.0 fraction
    pos_y = db.Column(db.Float, nullable=False, default=0.8)  # 0.0 to 1.0 fraction
    status = db.Column(db.String(20), default="waiting", nullable=False)  # waiting | pending | approved | compliance | rejected
    approval_no = db.Column(db.String(30), unique=True, nullable=True)  # AH-2026-XXXXX
    record_hash = db.Column(db.String(64), nullable=True)  # Audit signature hash
    reject_reason = db.Column(db.String(100), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    acted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "approver_id": self.approver_id,
            "approver_name": self.approver.name if self.approver else "Unknown",
            "approver_designation": self.approver.designation if self.approver else "",
            "approver_department": self.approver.department if self.approver else "",
            "step_order": self.step_order,
            "mark_type": self.mark_type,
            "page_no": self.page_no,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "status": self.status,
            "approval_no": self.approval_no,
            "record_hash": self.record_hash,
            "reject_reason": self.reject_reason,
            "remark": self.remark,
            "acted_at": self.acted_at.isoformat() if self.acted_at else None
        }

class Timeline(db.Model):
    __tablename__ = "timeline"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now)

    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "actor_name": self.user.name if self.user else "System",
            "event": self.event,
            "details": self.details,
            "timestamp": self.timestamp.strftime("%d %b %Y, %H:%M UTC") if self.timestamp else None
        }

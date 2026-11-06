"""
ApproveHub — Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Centralised configuration for the ApproveHub platform. Supports both
local SQLite (development) and cloud PostgreSQL (production) databases
via the DATABASE_URL environment variable.

Environment Variables:
    SECRET_KEY          Flask session encryption key
    DATABASE_URL        PostgreSQL connection string (optional; defaults to SQLite)
"""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """Flask application configuration."""

    # Session & CSRF encryption key
    SECRET_KEY = os.environ.get("SECRET_KEY", "approvehub-super-secret-key-2026-edi")

    # Database configuration
    # Handles the postgres:// → postgresql:// scheme migration required by SQLAlchemy 2.x
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url and raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url or f"sqlite:///{os.path.join(BASE_DIR, 'approvehub.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload directory hierarchy
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    DOCS_FOLDER = os.path.join(UPLOAD_FOLDER, "docs")
    FINAL_FOLDER = os.path.join(UPLOAD_FOLDER, "final")
    ASSETS_FOLDER = os.path.join(UPLOAD_FOLDER, "assets")
    QR_FOLDER = os.path.join(UPLOAD_FOLDER, "qr")

    # File upload constraints
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024   # 10 MB maximum upload size
    ALLOWED_EXTENSIONS = {"pdf"}

    # Security parameters
    MAX_PIN_ATTEMPTS = 5                     # Account lockout after N failed PIN attempts
    PIN_LOCKOUT_MINUTES = 15                 # Lockout cooldown duration in minutes

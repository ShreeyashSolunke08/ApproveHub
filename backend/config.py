import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "approvehub-super-secret-key-2026-edi")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'approvehub.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    DOCS_FOLDER = os.path.join(UPLOAD_FOLDER, "docs")
    FINAL_FOLDER = os.path.join(UPLOAD_FOLDER, "final")
    ASSETS_FOLDER = os.path.join(UPLOAD_FOLDER, "assets")
    QR_FOLDER = os.path.join(UPLOAD_FOLDER, "qr")
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit (Problem #9)
    ALLOWED_EXTENSIONS = {"pdf"}
    
    # Security parameters
    MAX_PIN_ATTEMPTS = 5                   # Lock after 5 wrong PIN tries (Problem #6)
    PIN_LOCKOUT_MINUTES = 15

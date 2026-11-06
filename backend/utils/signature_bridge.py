"""
ApproveHub — Zero-Install Smartphone Signature Bridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Relays real-time touch signatures from mobile smartphone screens to desktop
workstations via secure ephemeral session tokens and dynamic QR optical handshakes.

Author: Shreeyash Solunke
Institution: VIT Pune, Department of Information Technology
"""

import os
import time
import socket
import secrets
import base64
from io import BytesIO
from datetime import datetime
import qrcode
from PIL import Image

# In-memory session registry for mobile real-time signing bridge
# token -> { "user_id": int, "created_at": float, "status": "pending" | "completed" }
_SESSIONS = {}

def get_lan_ip():
    """
    Auto-detects the host machine's Wi-Fi / Local Area Network IP address
    so mobile devices on the same Wi-Fi network can connect directly.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def create_mobile_session(user_id, port=5000):
    """
    Initializes a new mobile signature session, generates a secure URL,
    and returns both the mobile URL and an inline base64 QR code image.
    """
    token = secrets.token_urlsafe(16)
    lan_ip = get_lan_ip()
    
    mobile_url = f"http://{lan_ip}:{port}/mobile-sign/{token}"
    local_url = f"http://127.0.0.1:{port}/mobile-sign/{token}"

    # Generate high-contrast QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2
    )
    qr.add_data(mobile_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    qr_data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    _SESSIONS[token] = {
        "user_id": user_id,
        "created_at": time.time(),
        "status": "pending",
        "mobile_url": mobile_url,
        "local_url": local_url
    }

    return {
        "token": token,
        "mobile_url": mobile_url,
        "local_url": local_url,
        "qr_data_uri": qr_data_uri
    }

def get_session(token):
    return _SESSIONS.get(token)

def complete_mobile_session(token, signature_base64):
    """
    Saves transparent signature PNG from mobile sketch pad, sets user.signature_path,
    re-stamps approved documents, and marks session as completed.
    """
    session = _SESSIONS.get(token)
    if not session:
        return False, "Invalid or expired mobile signature session."

    user_id = session["user_id"]
    if not signature_base64 or "," not in signature_base64:
        return False, "No drawing data received from mobile device."

    try:
        from backend.models import db, User
        from backend.utils.stamping import restamp_user_approved_documents

        _, encoded = signature_base64.split(",", 1)
        file_bytes = base64.b64decode(encoded)

        upload_dir = os.path.join("uploads", "assets")
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"sig_{user_id}_sketch.png"
        target_path = os.path.join(upload_dir, filename)

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        user = User.query.get(user_id)
        if user:
            user.signature_path = target_path
            db.session.commit()
            
            # Immediately re-stamp any documents already approved by this user
            restamp_user_approved_documents(user_id)

        session["status"] = "completed"
        session["completed_at"] = time.time()
        return True, "Signature successfully uploaded and linked to institutional account!"
    except Exception as e:
        return False, f"Failed to save mobile signature: {str(e)}"

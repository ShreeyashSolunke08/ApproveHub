"""
ApproveHub — Real-Time SMTP Diagnostic & Test Utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verifies outbound email delivery with live SMTP credentials (Gmail, SendGrid, Resend, Zoho).

Usage:
    python test_smtp.py your-email@domain.com
"""

import sys
import os
from backend.utils.mailer import _send_email_worker, LATEST_SENT_EMAILS

def test_smtp_delivery(recipient_email):
    print("=" * 60)
    print("ApproveHub Live SMTP Delivery Test")
    print("=" * 60)

    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT", "587")
    user = os.environ.get("SMTP_USER")
    sender = os.environ.get("SMTP_SENDER", user)

    print(f"SMTP Host:   {host or '(Not configured - falling back to simulated memory buffer)'}")
    print(f"SMTP Port:   {port}")
    print(f"SMTP User:   {user or '(None)'}")
    print(f"SMTP Sender: {sender or '(None)'}")
    print(f"Recipient:   {recipient_email}")
    print("-" * 60)

    subject = "ApproveHub SMTP Test — Verification Notification"
    html = f"""
    <div style="font-family:sans-serif;max-width:540px;margin:0 auto;border:1px solid #E2E8F0;border-radius:16px;padding:32px;background:#FFFFFF;">
        <h2 style="color:#4F46E5;margin:0 0 12px;">ApproveHub Live Notification Test</h2>
        <p style="color:#334155;font-size:14px;line-height:1.6;">
            This email confirms that your ApproveHub live SMTP notification engine is operational.
        </p>
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:16px;border-radius:12px;margin:20px 0;">
            <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#0F172A;">System Specifications:</p>
            <ul style="margin:0;padding-left:20px;font-size:12.5px;color:#64748B;">
                <li>Platform: ApproveHub (EDI Capstone)</li>
                <li>Architect: Shreeyash Solunke</li>
                <li>Institution: VIT Pune</li>
                <li>Delivery Mode: {'Live SMTP Network Dispatch' if host else 'In-Memory Simulation'}</li>
            </ul>
        </div>
        <p style="font-size:12px;color:#94A3B8;margin:0;">
            Sent automatically by ApproveHub Notification Engine.
        </p>
    </div>
    """

    print("Dispatching test notification...")
    _send_email_worker(recipient_email, subject, html, "ApproveHub SMTP test message.")

    if LATEST_SENT_EMAILS:
        result = LATEST_SENT_EMAILS[-1]
        print(f"Dispatch Status: {result.get('status')}")
        if result.get("status") == "delivered":
            print("\nSUCCESS! Test email was accepted by SMTP server and delivered!")
        elif "failed" in result.get("status"):
            print(f"\nFAILED: {result.get('status')}")
            print("\nTroubleshooting tips:")
            print("1. If using Gmail, ensure 2-Step Verification is ON and use a 16-character App Password (not your normal password).")
            print("2. Ensure SMTP_HOST is smtp.gmail.com and SMTP_PORT is 587.")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_smtp.py <recipient-email-address>")
        sys.exit(1)
    test_smtp_delivery(sys.argv[1])

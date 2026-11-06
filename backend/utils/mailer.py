import os
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Thread-safe in-memory mailbox for local development & testing
LATEST_SENT_EMAILS = []

def get_latest_emails():
    return list(reversed(LATEST_SENT_EMAILS[-20:]))

def _send_email_worker(to_email, subject, html_content, text_content=None, attachment_path=None):
    smtp_host = os.environ.get("SMTP_HOST") or os.environ.get("MAIL_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT") or os.environ.get("MAIL_PORT") or 587)
    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("MAIL_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASS") or os.environ.get("MAIL_PASSWORD")
    smtp_sender = os.environ.get("SMTP_SENDER") or os.environ.get("MAIL_DEFAULT_SENDER") or "no-reply@approvehub.edu"
    use_tls = os.environ.get("SMTP_TLS", "true").lower() in ["true", "1", "yes"]

    # Record in debug memory buffer
    record = {
        "to": to_email,
        "subject": subject,
        "html": html_content,
        "has_attachment": bool(attachment_path),
        "status": "simulated"
    }

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"ApproveHub Notifications <{smtp_sender}>"
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if attachment_path and os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    msg.attach(part)

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_sender, [to_email], msg.as_string())
            server.quit()
            record["status"] = "delivered"
        except Exception as e:
            record["status"] = f"failed: {str(e)}"
    
    LATEST_SENT_EMAILS.append(record)

def send_async_email(to_email, subject, html_content, text_content=None, attachment_path=None):
    """
    Sends email asynchronously without blocking the user's HTTP request.
    """
    t = threading.Thread(
        target=_send_email_worker,
        args=(to_email, subject, html_content, text_content, attachment_path),
        daemon=True
    )
    t.start()

# ==========================================
# INSTITUTIONAL EMAIL TEMPLATES
# ==========================================

def send_password_reset_email(to_email, recipient_name, reset_url):
    subject = "ApproveHub — Password Reset Request"
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #0F172A; }}
  .box {{ max-width: 520px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; border: 1.5px solid #E2E8F0; padding: 32px; box-shadow: 0 10px 25px rgba(15,23,42,0.05); }}
  .badge {{ width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #4F46E5, #06B6D4); color: #FFF; font-size: 24px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }}
  .btn {{ display: inline-block; background: #4F46E5; color: #FFFFFF !important; padding: 13px 26px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 14px; margin-top: 18px; }}
  .footer {{ font-size: 12px; color: #64748B; margin-top: 28px; border-top: 1px solid #E2E8F0; padding-top: 16px; line-height: 1.5; }}
</style>
</head>
<body>
<div class="box">
  <div class="badge">✓</div>
  <h2 style="margin: 0 0 12px; font-size: 20px; font-weight: 800;">Password Reset Request</h2>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">Hello <b>{recipient_name}</b>,</p>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">We received a request to reset your institutional account password for ApproveHub. Click the button below to choose a new password:</p>
  <div style="text-align: center; margin: 24px 0;">
    <a href="{reset_url}" class="btn">Reset My Password →</a>
  </div>
  <p style="font-size: 12.5px; color: #64748B;">This secure token is valid for 2 hours. If you did not initiate this request, you can safely ignore this email.</p>
  <div class="footer">
    ApproveHub Digital Document Approval System • Official Institutional Dispatch
  </div>
</div>
</body>
</html>"""
    send_async_email(to_email, subject, html)

def send_approval_status_email(to_email, recipient_name, document_title, status, approver_name, notes="", view_url="", attachment_path=None):
    status_label = status.upper()
    status_color = "#059669" if status == "approved" else ("#D97706" if status == "compliance" else "#E11D48")
    status_desc = {
        "approved": "has received official institutional signoff and has been digitally stamped with QR verification.",
        "compliance": "requires corrections or additional details before it can proceed.",
        "rejected": "has been declined by the reviewing authority."
    }.get(status, "status has been updated.")

    subject = f"ApproveHub — Document {status_label}: {document_title}"
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #0F172A; }}
  .box {{ max-width: 540px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; border: 1.5px solid #E2E8F0; padding: 32px; box-shadow: 0 10px 25px rgba(15,23,42,0.05); }}
  .pill {{ display: inline-block; padding: 6px 14px; border-radius: 99px; font-weight: 800; font-size: 12px; color: #FFF; background: {status_color}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; }}
  .card-note {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid {status_color}; border-radius: 8px; padding: 12px 16px; margin: 16px 0; font-size: 13px; }}
  .btn {{ display: inline-block; background: #4F46E5; color: #FFFFFF !important; padding: 12px 24px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 13.5px; }}
  .footer {{ font-size: 12px; color: #64748B; margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 14px; }}
</style>
</head>
<body>
<div class="box">
  <span class="pill">{status_label}</span>
  <h2 style="margin: 0 0 8px; font-size: 20px; font-weight: 800;">{document_title}</h2>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">Hello <b>{recipient_name}</b>,</p>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">Your request <b>"{document_title}"</b> {status_desc}</p>
  
  <div class="card-note">
    <b>Reviewing Authority:</b> {approver_name}<br>
    {f"<b>Authority Remark:</b> {notes}" if notes else ""}
  </div>

  {f'<div style="margin: 20px 0;"><a href="{view_url}" class="btn">View Document Details →</a></div>' if view_url else ""}

  {f'<p style="font-size: 12.5px; color: #059669; font-weight: 600;">📎 Your officially stamped, QR-verified PDF is attached to this email.</p>' if attachment_path else ""}

  <div class="footer">
    ApproveHub Automated Institutional Workflow • Verified Cryptographic Audit Trail
  </div>
</div>
</body>
</html>"""
    send_async_email(to_email, subject, html, attachment_path=attachment_path)

def send_pending_review_email(to_email, recipient_name, document_title, applicant_name, step_num, review_url=""):
    subject = f"Action Required: Approval Request from {applicant_name}"
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #0F172A; }}
  .box {{ max-width: 520px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; border: 1.5px solid #E2E8F0; padding: 32px; box-shadow: 0 10px 25px rgba(15,23,42,0.05); }}
  .btn {{ display: inline-block; background: #4F46E5; color: #FFFFFF !important; padding: 12px 24px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 13.5px; margin-top: 14px; }}
  .footer {{ font-size: 12px; color: #64748B; margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 14px; }}
</style>
</head>
<body>
<div class="box">
  <div style="font-size: 11.5px; font-weight: 800; color: #4F46E5; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">Step {step_num} Approval Pending</div>
  <h2 style="margin: 0 0 10px; font-size: 20px; font-weight: 800;">Review Required</h2>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">Respected <b>{recipient_name}</b>,</p>
  <p style="font-size: 14px; line-height: 1.6; color: #334155;">A new document <b>"{document_title}"</b> submitted by <b>{applicant_name}</b> is pending your official signoff.</p>
  
  {f'<div style="text-align: center; margin: 20px 0;"><a href="{review_url}" class="btn">Open Approval Desk &amp; Sign →</a></div>' if review_url else ""}

  <div class="footer">
    ApproveHub Digital Workflow Engine
  </div>
</div>
</body>
</html>"""
    send_async_email(to_email, subject, html)

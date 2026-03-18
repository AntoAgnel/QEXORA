"""
QEXORA Email Service
Sends OTP for password reset and welcome emails.
Uses Flask-Mail with Gmail SMTP.

Setup in .env:
  MAIL_USERNAME=your-gmail@gmail.com
  MAIL_APP_PASSWORD=your-16-char-app-password

Gmail App Password setup:
  1. Go to myaccount.google.com → Security
  2. Enable 2-Step Verification
  3. Search "App passwords" → Create one for "Mail"
  4. Use the 16-char password as MAIL_APP_PASSWORD
"""

from flask_mail import Message
from extensions import mail


def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """Send OTP for password reset."""
    try:
        msg = Message(
            subject='QEXORA – Password Reset OTP',
            recipients=[to_email]
        )
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family:'Segoe UI',sans-serif;background:#f4f4f8;margin:0;padding:0;">
          <div style="max-width:480px;margin:40px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
            <div style="background:linear-gradient(135deg,#6c63ff,#00d4aa);padding:32px;text-align:center;">
              <h1 style="color:#fff;margin:0;font-size:28px;letter-spacing:2px;">QEXORA</h1>
              <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:13px;">Intelligent Academic Mapping System</p>
            </div>
            <div style="padding:36px 32px;">
              <h2 style="color:#0e0f14;margin:0 0 8px;font-size:20px;">Password Reset Request</h2>
              <p style="color:#6b7280;font-size:14px;margin:0 0 28px;">Hi {name}, use the OTP below to reset your password.</p>

              <div style="background:#f4f4f8;border-radius:10px;padding:24px;text-align:center;margin-bottom:28px;">
                <p style="color:#6b7280;font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 12px;">Your OTP</p>
                <div style="font-size:42px;font-weight:800;letter-spacing:12px;color:#6c63ff;">{otp}</div>
                <p style="color:#9ca3af;font-size:12px;margin:12px 0 0;">Valid for <strong>10 minutes</strong></p>
              </div>

              <p style="color:#9ca3af;font-size:12px;margin:0;">If you didn't request this, ignore this email. Your password will remain unchanged.</p>
            </div>
            <div style="background:#f9fafb;padding:16px 32px;text-align:center;border-top:1px solid #e5e7eb;">
              <p style="color:#9ca3af;font-size:11px;margin:0;">© 2025 QEXORA · Intelligent Academic Mapping System</p>
            </div>
          </div>
        </body>
        </html>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Mail] Error sending OTP: {e}")
        return False


def send_welcome_email(to_email: str, name: str) -> bool:
    """Send welcome email after registration."""
    try:
        msg = Message(
            subject='Welcome to QEXORA!',
            recipients=[to_email]
        )
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family:'Segoe UI',sans-serif;background:#f4f4f8;margin:0;padding:0;">
          <div style="max-width:480px;margin:40px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
            <div style="background:linear-gradient(135deg,#6c63ff,#00d4aa);padding:32px;text-align:center;">
              <h1 style="color:#fff;margin:0;font-size:28px;letter-spacing:2px;">QEXORA</h1>
            </div>
            <div style="padding:36px 32px;">
              <h2 style="color:#0e0f14;margin:0 0 8px;">Welcome, {name}! 🎉</h2>
              <p style="color:#6b7280;font-size:14px;">Your QEXORA account has been created. You can now log in and start managing your question bank and generating question papers.</p>
              <p style="color:#9ca3af;font-size:12px;margin-top:24px;">Your role and institution type will be assigned by your administrator.</p>
            </div>
          </div>
        </body>
        </html>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Mail] Error sending welcome email: {e}")
        return False

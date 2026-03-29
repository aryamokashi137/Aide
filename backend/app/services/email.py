import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings

def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> bool:
    """
    Sends an email using SMTP settings from config.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        print("SMTP settings are not fully configured. Email not sent.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach body
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))

        # Connect and send
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_verification_email(email: str, token: str):
    """
    Sends email verification link.
    """
    # In a real app, this would be a link to your frontend
    frontend_url = settings.SSO_FRONTEND_SUCCESS_URL or "http://localhost:2001"
    verification_link = f"{frontend_url}/verify-email?token={token}"
    
    subject = "Verify Your Aide Account"
    body = f"""
    <h2>Welcome to Aide!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <a href="{verification_link}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Verify Email</a>
    <p>Or copy and paste this link in your browser:</p>
    <p>{verification_link}</p>
    <p>This link will expire in 24 hours.</p>
    """
    return send_email(email, subject, body, is_html=True)

def send_password_reset_email(email: str, code: str):
    """
    Sends password reset verification code.
    """
    subject = "Reset Your Aide Password"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #2196F3;">Password Reset Request</h2>
        <p>You requested to reset your password. Please use the verification code below to proceed:</p>
        <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; text-align: center; padding: 20px; background-color: #f4f4f4; color: #333; border-radius: 5px;">
            {code}
        </div>
        <p>Enter this code on the password reset page. It will expire in 10 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
    </div>
    """
    return send_email(email, subject, body, is_html=True)

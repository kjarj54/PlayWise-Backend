import smtplib
import logging
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL]):
        logger.warning("SMTP not configured")
        return False
    
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.starttls()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


async def send_verification_email(email: str, username: str, verification_token: str) -> bool:
    body = f"Hi {username},\n\nYour verification code: {verification_token}\n\nEnter this code in the app to verify your email.\n\nExpires in 24h.\n\n- PlayWise"
    return await send_email(email, "Verify your PlayWise account", body)


async def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
    body = f"Hi {username},\n\nYour password reset code: {reset_token}\n\nEnter this code in the app to reset your password.\n\nExpires in 1h.\n\n- PlayWise"
    return await send_email(email, "Reset your PlayWise password", body)


async def send_welcome_email(email: str, username: str) -> bool:
    body = f"Hi {username},\n\nYour account is now active!\n\n- PlayWise"
    return await send_email(email, "Welcome to PlayWise", body)


async def send_otp_email(email: str, username: str, otp_code: str) -> bool:
    body = f"Hi {username},\n\nYour login code: {otp_code}\n\nExpires in 10 min.\n\n- PlayWise"
    return await send_email(email, "Your PlayWise login code", body)


async def send_activation_email(email: str, username: str, activation_token: str) -> bool:
    body = f"Hi {username},\n\nYour activation code: {activation_token}\n\nEnter this code in the app to activate your account.\n\nExpires in 24h.\n\n- PlayWise"
    return await send_email(email, "Activate your PlayWise account", body)

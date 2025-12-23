from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional)
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    if not all([
        settings.SMTP_HOST,
        settings.SMTP_USER,
        settings.SMTP_PASSWORD,
        settings.SMTP_FROM_EMAIL
    ]):
        logger.warning("SMTP not configured. Email not sent.")
        return False
    
    try:
        # Crear mensaje
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        # Agregar contenido
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Enviar email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        return False


async def send_verification_email(
    email: str,
    username: str,
    verification_token: str
) -> bool:
    """
    Send email verification email
    
    Args:
        email: User's email address
        username: User's username
        verification_token: Verification token
        
    Returns:
        True if email was sent successfully
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    subject = "Verify your PlayWise account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Welcome to PlayWise!</h1>
            </div>
            <div class="content">
                <h2>Hi {username}!</h2>
                <p>Thanks for signing up! Please verify your email address to activate your account.</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </p>
                <p>Or copy this link to your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2025 PlayWise. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to PlayWise!
    
    Hi {username}!
    
    Thanks for signing up! Please verify your email address by visiting:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, you can safely ignore this email.
    
    © 2025 PlayWise. All rights reserved.
    """
    
    return await send_email(email, subject, html_content, text_content)


async def send_password_reset_email(
    email: str,
    username: str,
    reset_token: str
) -> bool:
    """
    Send password reset email
    
    Args:
        email: User's email address
        username: User's username
        reset_token: Password reset token
        
    Returns:
        True if email was sent successfully
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "Reset your PlayWise password"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Password Reset</h1>
            </div>
            <div class="content">
                <h2>Hi {username}!</h2>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>Or copy this link to your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul>
                        <li>This link will expire in 1 hour</li>
                        <li>If you didn't request this, please ignore this email</li>
                        <li>Your password will remain unchanged</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 PlayWise. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset - PlayWise
    
    Hi {username}!
    
    We received a request to reset your password. Visit this link to create a new password:
    {reset_url}
    
    SECURITY NOTICE:
    - This link will expire in 1 hour
    - If you didn't request this, please ignore this email
    - Your password will remain unchanged
    
    © 2025 PlayWise. All rights reserved.
    """
    
    return await send_email(email, subject, html_content, text_content)


async def send_welcome_email(
    email: str,
    username: str
) -> bool:
    """
    Send welcome email after successful verification
    
    Args:
        email: User's email address
        username: User's username
        
    Returns:
        True if email was sent successfully
    """
    subject = "Welcome to PlayWise! 🎮"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .feature {{ margin: 15px 0; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to PlayWise!</h1>
            </div>
            <div class="content">
                <h2>Hi {username}!</h2>
                <p>Your account is now verified and ready to use! We're excited to have you join our gaming community.</p>
                
                <div class="features">
                    <h3>What you can do now:</h3>
                    <div class="feature">🎮 Discover and track your favorite games</div>
                    <div class="feature">⭐ Rate and review games</div>
                    <div class="feature">❤️ Create your wishlist</div>
                    <div class="feature">👥 Connect with friends</div>
                    <div class="feature">💬 Join the community discussions</div>
                    <div class="feature">🛒 Find the best deals on games</div>
                </div>
                
                <p style="text-align: center;">
                    <a href="{settings.FRONTEND_URL}" class="button">Start Exploring</a>
                </p>
                
                <p>Happy gaming! 🎮</p>
            </div>
            <div class="footer">
                <p>© 2025 PlayWise. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to PlayWise!
    
    Hi {username}!
    
    Your account is now verified and ready to use! We're excited to have you join our gaming community.
    
    What you can do now:
    - Discover and track your favorite games
    - Rate and review games
    - Create your wishlist
    - Connect with friends
    - Join the community discussions
    - Find the best deals on games
    
    Visit {settings.FRONTEND_URL} to start exploring!
    
    Happy gaming!
    
    © 2025 PlayWise. All rights reserved.
    """
    
    return await send_email(email, subject, html_content, text_content)

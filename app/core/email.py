import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


def get_email_template(title: str, content: str, button_text: str = None, button_url: str = None, button_code: str = None) -> str:
    """Generate a professional HTML email template with responsive design"""
    button_html = ""
    
    if button_url and button_text:
        # Botón con link
        button_html = f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 30px auto;">
            <tr>
                <td style="border-radius: 6px; background-color: #667eea;">
                    <a href="{button_url}" style="display: inline-block; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px;">
                        {button_text}
                    </a>
                </td>
            </tr>
        </table>
        """
    elif button_code:
        # Código de verificación
        button_html = f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 30px auto;">
            <tr>
                <td style="border-radius: 6px; background-color: #667eea; border: 2px solid #5568d3;">
                    <div style="font-family: 'Courier New', Consolas, monospace; font-size: 28px; font-weight: bold; color: #ffffff; padding: 18px 36px; letter-spacing: 6px; text-align: center;">
                        {button_code}
                    </div>
                </td>
            </tr>
        </table>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="es" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="x-apple-disable-message-reformatting">
        <title>{title}</title>
        <!--[if mso]>
        <style type="text/css">
            table {{border-collapse: collapse; border-spacing: 0; margin: 0;}}
            div, td {{padding: 0;}}
        </style>
        <![endif]-->
        <style type="text/css">
            @media only screen and (max-width: 600px) {{
                .container {{
                    width: 100% !important;
                    max-width: 100% !important;
                }}
                .content-padding {{
                    padding: 30px 20px !important;
                }}
                .header-padding {{
                    padding: 30px 20px !important;
                }}
                .footer-padding {{
                    padding: 20px 15px !important;
                }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f5; padding: 20px 0;">
            <tr>
                <td align="center" style="padding: 0;">
                    <!-- Container -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" class="container" style="max-width: 600px; width: 100%; background-color: #ffffff; margin: 0 auto;">
                        <!-- Header -->
                        <tr>
                            <td class="header-padding" style="background-color: #667eea; padding: 36px 30px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: 700; letter-spacing: -0.5px; line-height: 1.3;">
                                    PlayWise
                                </h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td class="content-padding" style="padding: 40px 40px;">
                                <div style="color: #18181b; font-size: 15px; line-height: 1.6;">
                                    {content}
                                </div>
                                {button_html}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td class="footer-padding" style="background-color: #fafafa; padding: 24px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                                <p style="margin: 0 0 8px 0; color: #71717a; font-size: 13px; line-height: 1.4;">
                                    © 2026 PlayWise. Todos los derechos reservados.
                                </p>
                                <p style="margin: 0; color: #a1a1aa; font-size: 12px; line-height: 1.4;">
                                    Este es un correo automático, por favor no responder.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def send_email(to_email: str, subject: str, body: str, html_body: str = None) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL]):
        logger.warning("SMTP not configured")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"PlayWise <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        
        # Attach plain text version
        msg.attach(MIMEText(body, "plain"))
        
        # Attach HTML version if provided
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        
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
    """
    Envía email de verificación. Si BACKEND_URL está configurado, incluye un link.
    Si no, solo envía el código.
    """
    if settings.BACKEND_URL:
        # Modo con link (recomendado para apps móviles)
        verification_url = f"{settings.BACKEND_URL}/verify-email?token={verification_token}"
        
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Gracias por registrarte en PlayWise. Para completar tu registro y comenzar a usar tu cuenta, necesitamos verificar tu dirección de correo electrónico.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Haz clic en el botón a continuación para verificar tu cuenta:</p>
        """
        
        html_body = get_email_template(
            "Verifica tu cuenta",
            content,
            button_text="Verificar mi cuenta",
            button_url=verification_url
        )
        
        html_body += f"""
        <div style="margin-top: 24px; padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 6px;">
            <p style="margin: 0 0 8px 0; color: #52525b; font-size: 13px; font-weight: 600;">
                Si el botón no funciona:
            </p>
            <p style="margin: 0; color: #667eea; font-size: 12px; word-break: break-all; font-family: monospace;">
                {verification_url}
            </p>
        </div>
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
            <p style="margin: 0; color: #92400e; font-size: 13px;">
                <strong>Importante:</strong> Este enlace expira en 24 horas por seguridad.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nGracias por registrarte en PlayWise.\n\nVerifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_url}\n\nO ingresa este código en la aplicación: {verification_token}\n\nEste enlace expira en 24 horas.\n\nSaludos,\nEquipo PlayWise"
    else:
        # Modo solo código (fallback)
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Gracias por registrarte en PlayWise. Para completar tu registro, necesitamos verificar tu correo electrónico.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Utiliza el siguiente código de verificación en la aplicación:</p>
        """
        
        html_body = get_email_template(
            "Verifica tu cuenta",
            content,
            button_code=verification_token
        )
        
        html_body += f"""
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
            <p style="margin: 0; color: #92400e; font-size: 13px;">
                <strong>Importante:</strong> Este código expira en 24 horas por seguridad.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nGracias por registrarte en PlayWise.\n\nCódigo de verificación: {verification_token}\n\nIngresa este código en la aplicación para verificar tu correo electrónico.\n\nEste código expira en 24 horas.\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(email, "Verifica tu cuenta de PlayWise", plain_body, html_body)


async def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
    """
    Envía email de recuperación de contraseña. Si BACKEND_URL está configurado, incluye un link.
    Si no, solo envía el código.
    """
    if settings.BACKEND_URL:
        # Modo con link (recomendado para apps móviles)
        reset_url = f"{settings.BACKEND_URL}/reset-password?token={reset_token}"
        
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Recibimos una solicitud para restablecer la contraseña de tu cuenta de PlayWise.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Haz clic en el botón a continuación para crear una nueva contraseña:</p>
        """
        
        html_body = get_email_template(
            "Restablece tu contraseña",
            content,
            button_text="Restablecer contraseña",
            button_url=reset_url
        )
        
        html_body += f"""
        <div style="margin-top: 24px; padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 6px;">
            <p style="margin: 0 0 8px 0; color: #52525b; font-size: 13px; font-weight: 600;">
                Si el botón no funciona:
            </p>
            <p style="margin: 0; color: #667eea; font-size: 12px; word-break: break-all; font-family: monospace;">
                {reset_url}
            </p>
        </div>
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fee2e2; border-left: 3px solid #dc2626; border-radius: 4px;">
            <p style="margin: 0 0 10px 0; color: #991b1b; font-size: 13px;">
                <strong>Importante:</strong> Este enlace expira en 1 hora por seguridad.
            </p>
            <p style="margin: 0; color: #991b1b; font-size: 13px;">
                Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nRecibimos una solicitud para restablecer tu contraseña.\n\nRestablece tu contraseña haciendo clic en el siguiente enlace:\n{reset_url}\n\nO ingresa este código en la aplicación: {reset_token}\n\nEste enlace expira en 1 hora por seguridad.\n\nSi no solicitaste este cambio, ignora este correo.\n\nSaludos,\nEquipo PlayWise"
    else:
        # Modo solo código (fallback)
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Recibimos una solicitud para restablecer la contraseña de tu cuenta de PlayWise.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Utiliza el siguiente código en la aplicación para crear una nueva contraseña:</p>
        """
        
        html_body = get_email_template(
            "Restablece tu contraseña",
            content,
            button_code=reset_token
        )
        
        html_body += f"""
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fee2e2; border-left: 3px solid #dc2626; border-radius: 4px;">
            <p style="margin: 0 0 10px 0; color: #991b1b; font-size: 13px;">
                <strong>Importante:</strong> Este código expira en 1 hora por seguridad.
            </p>
            <p style="margin: 0; color: #991b1b; font-size: 13px;">
                Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nRecibimos una solicitud para restablecer tu contraseña.\n\nCódigo de restablecimiento: {reset_token}\n\nIngresa este código en la aplicación para restablecer tu contraseña.\n\nEste código expira en 1 hora por seguridad.\n\nSi no solicitaste este cambio, ignora este correo.\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(email, "Restablece tu contraseña de PlayWise", plain_body, html_body)


async def send_welcome_email(email: str, username: str) -> bool:
    content = f"""
    <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Bienvenido a PlayWise, {username}</h2>
    <p style="margin: 0 0 20px 0; color: #3f3f46; font-size: 16px;">Tu cuenta ha sido activada exitosamente y ya puedes comenzar a usar la plataforma.</p>
    <p style="margin: 0 0 12px 0; color: #3f3f46; font-weight: 600;">Funciones disponibles:</p>
    <ul style="color: #52525b; line-height: 1.8; margin: 0 0 20px 0; padding-left: 20px;">
        <li>Descubre y explora nuevos juegos</li>
        <li>Califica y comenta tus juegos favoritos</li>
        <li>Conecta con otros jugadores</li>
        <li>Gestiona tu lista de deseos</li>
    </ul>
    <p style="margin: 0; color: #667eea; font-weight: 600;">
        ¡Disfruta de PlayWise!
    </p>
    """
    
    html_body = get_email_template(
        "Bienvenido a PlayWise",
        content
    )
    
    plain_body = f"Bienvenido a PlayWise, {username}\n\nTu cuenta ha sido activada exitosamente y ya puedes comenzar a usar la plataforma.\n\nFunciones disponibles:\n- Descubre y explora nuevos juegos\n- Califica y comenta tus juegos favoritos\n- Conecta con otros jugadores\n- Gestiona tu lista de deseos\n\n¡Disfruta de PlayWise!\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(email, "Bienvenido a PlayWise", plain_body, html_body)


async def send_otp_email(email: str, username: str, otp_code: str) -> bool:
    content = f"""
    <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
    <p style="margin: 0 0 16px 0; color: #3f3f46;">Recibimos una solicitud de inicio de sesión para tu cuenta de PlayWise.</p>
    <p style="margin: 0 0 16px 0; color: #3f3f46;">Utiliza el siguiente código para completar el inicio de sesión:</p>
    """
    
    html_body = get_email_template(
        "Código de inicio de sesión",
        content,
        button_code=otp_code
    )
    
    plain_body = f"Hola {username},\n\nCódigo de inicio de sesión: {otp_code}\n\nIngresa este código en la aplicación para iniciar sesión.\n\nEste código expira en 10 minutos.\n\nPor tu seguridad, nunca compartas este código.\n\nSaludos,\nEquipo PlayWise"
    
    html_body += f"""
    <div style="margin-top: 20px; padding: 14px 16px; background-color: #dbeafe; border-left: 3px solid #2563eb; border-radius: 4px;">
        <p style="margin: 0 0 10px 0; color: #1e40af; font-size: 13px;">
            <strong>Importante:</strong> Este código expira en 10 minutos por seguridad.
        </p>
        <p style="margin: 0; color: #1e40af; font-size: 13px;">
            Nunca compartas este código con nadie.
        </p>
    </div>
    """
    
    return await send_email(email, "Código de inicio de sesión - PlayWise", plain_body, html_body)


async def send_activation_email(email: str, username: str, activation_token: str) -> bool:
    """
    Envía email de activación. Si BACKEND_URL está configurado, incluye un link.
    Si no, solo envía el código.
    """
    if settings.BACKEND_URL:
        # Modo con link (recomendado para apps móviles)
        activation_url = f"{settings.BACKEND_URL}/verify-email?token={activation_token}"
        
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Tu cuenta de PlayWise necesita ser activada para poder acceder a todas las funciones.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Haz clic en el botón a continuación para activar tu cuenta:</p>
        """
        
        html_body = get_email_template(
            "Activa tu cuenta",
            content,
            button_text="Activar mi cuenta",
            button_url=activation_url
        )
        
        html_body += f"""
        <div style="margin-top: 24px; padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 6px;">
            <p style="margin: 0 0 8px 0; color: #52525b; font-size: 13px; font-weight: 600;">
                Si el botón no funciona:
            </p>
            <p style="margin: 0; color: #667eea; font-size: 12px; word-break: break-all; font-family: monospace;">
                {activation_url}
            </p>
        </div>
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #dcfce7; border-left: 3px solid #16a34a; border-radius: 4px;">
            <p style="margin: 0; color: #166534; font-size: 13px;">
                <strong>Importante:</strong> Este enlace expira en 24 horas por seguridad.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nActiva tu cuenta haciendo clic en el siguiente enlace:\n{activation_url}\n\nO ingresa este código en la aplicación: {activation_token}\n\nEste enlace expira en 24 horas.\n\nSaludos,\nEquipo PlayWise"
    else:
        # Modo solo código (fallback)
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Tu cuenta de PlayWise necesita ser activada para poder acceder a todas las funciones.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Utiliza el siguiente código de activación en la aplicación:</p>
        """
        
        html_body = get_email_template(
            "Activa tu cuenta",
            content,
            button_code=activation_token
        )
        
        html_body += f"""
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #dcfce7; border-left: 3px solid #16a34a; border-radius: 4px;">
            <p style="margin: 0; color: #166534; font-size: 13px;">
                <strong>Importante:</strong> Este código expira en 24 horas por seguridad.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nCódigo de activación: {activation_token}\n\nIngresa este código en la aplicación para activar tu cuenta.\n\nEste código expira en 24 horas.\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(email, "Activa tu cuenta de PlayWise", plain_body, html_body)


async def send_email_change_verification(new_email: str, username: str, verification_token: str) -> bool:
    """
    Envía email de verificación para cambio de correo electrónico.
    El usuario debe confirmar el nuevo email antes de que se actualice.
    """
    if settings.BACKEND_URL:
        # Modo con link
        verification_url = f"{settings.BACKEND_URL}/verify-email-change?token={verification_token}"
        
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Recibimos una solicitud para cambiar el correo electrónico de tu cuenta de PlayWise.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;"><strong>Nuevo correo:</strong> {new_email}</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Haz clic en el botón a continuación para confirmar este cambio:</p>
        """
        
        html_body = get_email_template(
            "Confirma el cambio de correo",
            content,
            button_text="Confirmar nuevo correo",
            button_url=verification_url
        )
        
        html_body += f"""
        <div style="margin-top: 24px; padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 6px;">
            <p style="margin: 0 0 8px 0; color: #52525b; font-size: 13px; font-weight: 600;">
                Si el botón no funciona:
            </p>
            <p style="margin: 0; color: #667eea; font-size: 12px; word-break: break-all; font-family: monospace;">
                {verification_url}
            </p>
        </div>
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
            <p style="margin: 0 0 10px 0; color: #92400e; font-size: 13px;">
                <strong>Importante:</strong> Tu cuenta ha sido temporalmente desactivada hasta que confirmes este cambio.
            </p>
            <p style="margin: 0; color: #92400e; font-size: 13px;">
                Este enlace expira en 24 horas. Si no solicitaste este cambio, contacta con soporte inmediatamente.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nRecibimos una solicitud para cambiar tu correo electrónico a: {new_email}\n\nConfirma haciendo clic en el siguiente enlace:\n{verification_url}\n\nO ingresa este código en la aplicación: {verification_token}\n\nTu cuenta ha sido temporalmente desactivada hasta que confirmes este cambio.\nEste enlace expira en 24 horas.\n\nSi no solicitaste este cambio, contacta con soporte.\n\nSaludos,\nEquipo PlayWise"
    else:
        # Modo solo código
        content = f"""
        <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Recibimos una solicitud para cambiar el correo electrónico de tu cuenta de PlayWise.</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;"><strong>Nuevo correo:</strong> {new_email}</p>
        <p style="margin: 0 0 16px 0; color: #3f3f46;">Utiliza el siguiente código en la aplicación para confirmar este cambio:</p>
        """
        
        html_body = get_email_template(
            "Confirma el cambio de correo",
            content,
            button_code=verification_token
        )
        
        html_body += f"""
        <div style="margin-top: 20px; padding: 14px 16px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
            <p style="margin: 0 0 10px 0; color: #92400e; font-size: 13px;">
                <strong>Importante:</strong> Tu cuenta ha sido temporalmente desactivada hasta que confirmes este cambio.
            </p>
            <p style="margin: 0; color: #92400e; font-size: 13px;">
                Este código expira en 24 horas. Si no solicitaste este cambio, contacta con soporte inmediatamente.
            </p>
        </div>
        """
        
        plain_body = f"Hola {username},\n\nRecibimos una solicitud para cambiar tu correo electrónico a: {new_email}\n\nCódigo de confirmación: {verification_token}\n\nIngresa este código en la aplicación para confirmar el cambio.\n\nTu cuenta ha sido temporalmente desactivada hasta que confirmes este cambio.\nEste código expira en 24 horas.\n\nSi no solicitaste este cambio, contacta con soporte.\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(new_email, "Confirma el cambio de correo - PlayWise", plain_body, html_body)


async def send_email_changed_notification(old_email: str, username: str) -> bool:
    """
    Envía notificación al correo anterior informando que el email fue cambiado exitosamente.
    """
    content = f"""
    <h2 style="color: #18181b; margin: 0 0 20px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">Hola, {username}</h2>
    <p style="margin: 0 0 16px 0; color: #3f3f46;">El correo electrónico asociado a tu cuenta de PlayWise ha sido cambiado exitosamente.</p>
    <p style="margin: 0 0 16px 0; color: #3f3f46;">Tu cuenta ha sido reactivada y ya puedes iniciar sesión con tu nuevo correo electrónico.</p>
    <div style="margin-top: 20px; padding: 14px 16px; background-color: #fee2e2; border-left: 3px solid #dc2626; border-radius: 4px;">
        <p style="margin: 0 0 10px 0; color: #991b1b; font-size: 13px;">
            <strong>¿No autorizaste este cambio?</strong>
        </p>
        <p style="margin: 0; color: #991b1b; font-size: 13px;">
            Si no realizaste este cambio, contacta inmediatamente con nuestro equipo de soporte para proteger tu cuenta.
        </p>
    </div>
    """
    
    html_body = get_email_template(
        "Correo electrónico actualizado",
        content
    )
    
    plain_body = f"Hola {username},\n\nEl correo electrónico asociado a tu cuenta de PlayWise ha sido cambiado exitosamente.\n\nTu cuenta ha sido reactivada y ya puedes iniciar sesión con tu nuevo correo electrónico.\n\n¿No autorizaste este cambio?\nSi no realizaste este cambio, contacta inmediatamente con nuestro equipo de soporte.\n\nSaludos,\nEquipo PlayWise"
    
    return await send_email(old_email, "Correo electrónico actualizado - PlayWise", plain_body, html_body)



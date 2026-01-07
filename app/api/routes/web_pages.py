from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from app.db import get_session
from app.services import AuthService

router = APIRouter(tags=["Web Pages"])


def get_base_html(title: str, content: str) -> str:
    """Plantilla HTML base para las páginas web"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - PlayWise</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 500px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }}
            
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            
            h1 {{
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #666;
                font-size: 16px;
                margin-bottom: 30px;
            }}
            
            .icon {{
                font-size: 80px;
                margin: 20px 0;
            }}
            
            .success {{
                color: #28a745;
            }}
            
            .error {{
                color: #dc3545;
            }}
            
            .warning {{
                color: #ffc107;
            }}
            
            .message {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                font-size: 16px;
                line-height: 1.6;
                color: #333;
            }}
            
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                padding: 15px 40px;
                border-radius: 25px;
                font-weight: bold;
                margin-top: 20px;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }}
            
            .form-container {{
                margin: 30px 0;
            }}
            
            .input-group {{
                margin-bottom: 20px;
                text-align: left;
            }}
            
            label {{
                display: block;
                color: #333;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            input {{
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }}
            
            input:focus {{
                outline: none;
                border-color: #667eea;
            }}
            
            .submit-btn {{
                width: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .submit-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }}
            
            .submit-btn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
            }}
            
            .error-message {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
                padding: 12px;
                margin-top: 15px;
                display: none;
            }}
            
            .error-message.show {{
                display: block;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                color: #666;
                font-size: 14px;
            }}
            
            .password-requirements {{
                text-align: left;
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                font-size: 14px;
            }}
            
            .password-requirements ul {{
                margin-top: 10px;
                padding-left: 20px;
            }}
            
            .password-requirements li {{
                margin: 5px 0;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎮</div>
            <h1>PlayWise</h1>
            {content}
        </div>
    </body>
    </html>
    """


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page(
    token: str,
    session: Session = Depends(get_session)
):
    """
    Página de verificación de email - se abre desde el link en el correo
    """
    try:
        # Verificar el email usando el token
        result = await AuthService.verify_email(session, token)
        
        content = f"""
        <div class="subtitle">Verificación de Email</div>
        <div class="icon success">✅</div>
        <div class="message">
            <strong>¡Cuenta verificada exitosamente!</strong><br><br>
            {result["message"]}<br><br>
            Ya puedes iniciar sesión en la aplicación PlayWise.
        </div>
        <div class="footer">
            Abre tu aplicación PlayWise y comienza a disfrutar de todas las funciones.
        </div>
        """
        
    except Exception as e:
        error_msg = str(e)
        content = f"""
        <div class="subtitle">Verificación de Email</div>
        <div class="icon error">❌</div>
        <div class="message">
            <strong>Error al verificar el email</strong><br><br>
            {error_msg}<br><br>
            Por favor, solicita un nuevo código de verificación desde la aplicación.
        </div>
        <div class="footer">
            Si el problema persiste, contacta con soporte.
        </div>
        """
    
    return get_base_html("Verificación de Email", content)


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(token: str):
    """
    Página de restablecimiento de contraseña - formulario HTML
    """
    content = f"""
    <div class="subtitle">Restablece tu Contraseña</div>
    <div class="icon warning">🔑</div>
    
    <div class="password-requirements">
        <strong>⚠️ Requisitos de la contraseña:</strong>
        <ul>
            <li>Mínimo 8 caracteres</li>
            <li>Al menos una letra mayúscula</li>
            <li>Al menos una letra minúscula</li>
            <li>Al menos un número</li>
        </ul>
    </div>
    
    <form id="resetForm" class="form-container">
        <input type="hidden" id="token" value="{token}">
        
        <div class="input-group">
            <label for="password">Nueva Contraseña</label>
            <input type="password" id="password" name="password" required 
                   minlength="8" placeholder="Ingresa tu nueva contraseña">
        </div>
        
        <div class="input-group">
            <label for="confirmPassword">Confirmar Contraseña</label>
            <input type="password" id="confirmPassword" name="confirmPassword" required 
                   minlength="8" placeholder="Confirma tu nueva contraseña">
        </div>
        
        <button type="submit" class="submit-btn" id="submitBtn">
            Restablecer Contraseña
        </button>
        
        <div class="error-message" id="errorMessage"></div>
    </form>
    
    <div class="footer">
        Después de cambiar tu contraseña, podrás iniciar sesión en la app.
    </div>
    
    <script>
        document.getElementById('resetForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const errorMessage = document.getElementById('errorMessage');
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const token = document.getElementById('token').value;
            
            // Limpiar mensajes previos
            errorMessage.classList.remove('show');
            errorMessage.textContent = '';
            
            // Validar que las contraseñas coincidan
            if (password !== confirmPassword) {{
                errorMessage.textContent = 'Las contraseñas no coinciden';
                errorMessage.classList.add('show');
                return;
            }}
            
            // Validar longitud mínima
            if (password.length < 8) {{
                errorMessage.textContent = 'La contraseña debe tener al menos 8 caracteres';
                errorMessage.classList.add('show');
                return;
            }}
            
            // Validar mayúsculas
            if (!/[A-Z]/.test(password)) {{
                errorMessage.textContent = 'La contraseña debe contener al menos una letra mayúscula';
                errorMessage.classList.add('show');
                return;
            }}
            
            // Validar minúsculas
            if (!/[a-z]/.test(password)) {{
                errorMessage.textContent = 'La contraseña debe contener al menos una letra minúscula';
                errorMessage.classList.add('show');
                return;
            }}
            
            // Validar números
            if (!/[0-9]/.test(password)) {{
                errorMessage.textContent = 'La contraseña debe contener al menos un número';
                errorMessage.classList.add('show');
                return;
            }}
            
            // Deshabilitar botón durante la petición
            submitBtn.disabled = true;
            submitBtn.textContent = 'Procesando...';
            
            try {{
                const response = await fetch('/api/auth/reset-password', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        token: token,
                        new_password: password
                    }})
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    // Éxito - redirigir a página de éxito
                    window.location.href = '/reset-password-success';
                }} else {{
                    errorMessage.textContent = data.detail || 'Error al restablecer la contraseña';
                    errorMessage.classList.add('show');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Restablecer Contraseña';
                }}
            }} catch (error) {{
                errorMessage.textContent = 'Error de conexión. Por favor, intenta nuevamente.';
                errorMessage.classList.add('show');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Restablecer Contraseña';
            }}
        }});
    </script>
    """
    
    return get_base_html("Restablecer Contraseña", content)


@router.get("/reset-password-success", response_class=HTMLResponse)
async def reset_password_success():
    """
    Página de éxito después de restablecer la contraseña
    """
    content = """
    <div class="subtitle">Contraseña Restablecida</div>
    <div class="icon success">✅</div>
    <div class="message">
        <strong>¡Contraseña restablecida exitosamente!</strong><br><br>
        Tu contraseña ha sido actualizada correctamente.<br><br>
        Ya puedes iniciar sesión en la aplicación PlayWise con tu nueva contraseña.
    </div>
    <div class="footer">
        Abre tu aplicación PlayWise y accede con tus nuevas credenciales.
    </div>
    """
    
    return get_base_html("Contraseña Restablecida", content)

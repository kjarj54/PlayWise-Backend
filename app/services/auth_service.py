from sqlmodel import Session
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, status
from datetime import timedelta
from app.models import User, UserCreate, UserCreateGoogle, OTPVerifyRequest, LoginWithOTPResponse
from app.core import (
    verify_password, create_access_token, create_refresh_token,
    Token, verify_google_token, extract_google_user_data,
    send_verification_email, send_welcome_email, send_password_reset_email,
    send_activation_email
)
from app.services.user_service import UserService
from app.services.otp_service import OTPService


class AuthService:
    """Servicio para operaciones de autenticación"""
    
    @staticmethod
    async def register(session: Session, user_data: UserCreate) -> Dict[str, Any]:
        """
        Registrar nuevo usuario
        
        Returns:
            Dict con usuario y mensaje
        """
        # Crear usuario (inactivo hasta que active por email)
        user = UserService.create_user(session, user_data)
        
        # Enviar email de activación de cuenta
        await send_activation_email(
            email=user.email,
            username=user.username,
            activation_token=user.verification_token
        )
        
        return {
            "user": user,
            "message": "User created successfully. Please check your email to activate your account."
        }
    
    @staticmethod
    async def login(
        session: Session, 
        email: str, 
        password: str,
        device_id: Optional[str] = None
    ) -> Union[Token, LoginWithOTPResponse]:
        """
        Login con email y contraseña
        
        Args:
            session: Sesión de base de datos
            email: Email del usuario
            password: Contraseña
            device_id: ID único del dispositivo (para verificar si es de confianza)
        
        Returns:
            Token si no requiere OTP o LoginWithOTPResponse si requiere OTP
        """
        # Buscar usuario
        user = UserService.get_by_email(session, email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verificar que tenga password (no usuarios de Google sin password)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please login with Google"
            )
        
        # Verificar contraseña
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verificar que la cuenta esté activada por email
        if not user.is_email_activated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not activated. Please check your email to activate your account."
            )
        
        # Verificar que esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Verificar si necesita OTP
        needs_otp = False
        
        if not user.otp_verified_once:
            # Primera vez que inicia sesión después de activar
            needs_otp = True
        elif device_id:
            # Verificar si el dispositivo es de confianza
            if not OTPService.is_device_trusted(session, user.id, device_id):
                needs_otp = True
        else:
            # Sin device_id, siempre requiere OTP si ya verificó una vez
            # (esto previene bypass del OTP)
            needs_otp = True
        
        if needs_otp:
            # Enviar OTP por email
            await OTPService.send_login_otp(session, user)
            
            return LoginWithOTPResponse(
                otp_required=True,
                message="OTP code sent to your email. Please verify to continue."
            )
        
        # Actualizar último login
        UserService.update_last_login(session, user.id)
        
        # Crear tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def verify_login_otp(
        session: Session,
        otp_data: OTPVerifyRequest
    ) -> Token:
        """
        Verificar OTP y completar login
        
        Args:
            session: Sesión de base de datos
            otp_data: Datos de verificación OTP
            
        Returns:
            Token de acceso
        """
        # Buscar usuario por email
        user = UserService.get_by_email(session, otp_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Verificar OTP
        OTPService.verify_otp(session, user.id, otp_data.otp_code, "login")
        
        # Marcar que el usuario ya verificó OTP al menos una vez
        if not user.otp_verified_once:
            user.otp_verified_once = True
            session.commit()
        
        # Si el usuario quiere recordar el dispositivo, agregarlo
        if otp_data.remember_device and otp_data.device_id:
            OTPService.add_trusted_device(
                session,
                user.id,
                otp_data.device_id,
                otp_data.device_name,
                otp_data.device_type
            )
        
        # Actualizar último login
        UserService.update_last_login(session, user.id)
        
        # Crear tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def resend_otp(session: Session, email: str) -> Dict[str, str]:
        """
        Reenviar código OTP
        
        Args:
            session: Sesión de base de datos
            email: Email del usuario
            
        Returns:
            Dict con mensaje
        """
        user = UserService.get_by_email(session, email)
        
        if not user:
            # No revelar si el email existe
            return {"message": "If the email exists, a new OTP has been sent."}
        
        if not user.is_email_activated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not activated. Please activate your account first."
            )
        
        # Enviar nuevo OTP
        await OTPService.send_login_otp(session, user)
        
        return {"message": "If the email exists, a new OTP has been sent."}
    
    @staticmethod
    async def google_login(session: Session, id_token: str) -> Token:
        """
        Login o registro con Google OAuth
        
        Args:
            id_token: Google ID token
            
        Returns:
            Token con access_token y refresh_token
        """
        # Verificar token con Google
        google_data = await verify_google_token(id_token)
        
        if not google_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        # Extraer datos del usuario
        user_data = extract_google_user_data(google_data)
        
        # Buscar o crear usuario
        user = UserService.get_by_google_id(session, user_data["google_id"])
        
        if not user:
            # Crear nuevo usuario
            google_user_data = UserCreateGoogle(
                email=user_data["email"],
                username=user_data["username"],
                google_id=user_data["google_id"],
                profile_picture=user_data.get("profile_picture")
            )
            user = UserService.create_google_user(session, google_user_data)
            
            # Enviar email de bienvenida
            await send_welcome_email(
                email=user.email,
                username=user.username
            )
        
        # Verificar que esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Actualizar último login
        UserService.update_last_login(session, user.id)
        
        # Crear tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def verify_email(session: Session, token: str) -> Dict[str, Any]:
        """
        Verificar email con token (activación de cuenta)
        
        Returns:
            Dict con usuario y mensaje
        """
        user = UserService.activate_account(session, token)
        
        # Enviar email de bienvenida
        await send_welcome_email(
            email=user.email,
            username=user.username
        )
        
        return {
            "user": user,
            "message": "Account activated successfully! You can now log in."
        }
    
    @staticmethod
    async def resend_activation_email(session: Session, email: str) -> Dict[str, str]:
        """
        Reenviar email de activación
        
        Args:
            session: Sesión de base de datos
            email: Email del usuario
            
        Returns:
            Dict con mensaje
        """
        user = UserService.get_by_email(session, email)
        
        if not user:
            # No revelar si el email existe
            return {"message": "If the email exists, an activation link has been sent."}
        
        if user.is_email_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated."
            )
        
        # Generar nuevo token si es necesario
        user = UserService.regenerate_activation_token(session, user.id)
        
        # Enviar email de activación
        await send_activation_email(
            email=user.email,
            username=user.username,
            activation_token=user.verification_token
        )
        
        return {"message": "If the email exists, an activation link has been sent."}
    
    @staticmethod
    async def request_password_reset(session: Session, email: str) -> Dict[str, str]:
        """
        Solicitar reset de contraseña
        
        Returns:
            Dict con mensaje
        """
        user = UserService.request_password_reset(session, email)
        
        # Enviar email de reset
        await send_password_reset_email(
            email=user.email,
            username=user.username,
            reset_token=user.reset_password_token
        )
        
        return {
            "message": "If the email exists, a reset link has been sent"
        }
    
    @staticmethod
    def reset_password(session: Session, token: str, new_password: str) -> Dict[str, str]:
        """
        Resetear contraseña con token
        
        Returns:
            Dict con mensaje
        """
        UserService.reset_password(session, token, new_password)
        
        return {
            "message": "Password reset successfully"
        }
    
    @staticmethod
    def refresh_access_token(session: Session, user_id: int) -> Token:
        """
        Refrescar access token
        
        Returns:
            Nuevo Token
        """
        user = UserService.get_by_id(session, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )
        
        # Crear nuevos tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

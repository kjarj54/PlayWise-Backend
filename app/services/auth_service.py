from sqlmodel import Session
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import timedelta
from app.models import User, UserCreate, UserCreateGoogle
from app.core import (
    verify_password, create_access_token, create_refresh_token,
    Token, verify_google_token, extract_google_user_data,
    send_verification_email, send_welcome_email, send_password_reset_email
)
from app.services.user_service import UserService


class AuthService:
    """Servicio para operaciones de autenticación"""
    
    @staticmethod
    async def register(session: Session, user_data: UserCreate) -> Dict[str, Any]:
        """
        Registrar nuevo usuario
        
        Returns:
            Dict con usuario y mensaje
        """
        # Crear usuario
        user = UserService.create_user(session, user_data)
        
        # Enviar email de verificación
        await send_verification_email(
            email=user.email,
            username=user.username,
            verification_token=user.verification_token
        )
        
        return {
            "user": user,
            "message": "User created successfully. Please check your email to verify your account."
        }
    
    @staticmethod
    def login(session: Session, email: str, password: str) -> Token:
        """
        Login con email y contraseña
        
        Returns:
            Token con access_token y refresh_token
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
        Verificar email con token
        
        Returns:
            Dict con usuario y mensaje
        """
        user = UserService.verify_email(session, token)
        
        # Enviar email de bienvenida
        await send_welcome_email(
            email=user.email,
            username=user.username
        )
        
        return {
            "user": user,
            "message": "Email verified successfully"
        }
    
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

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Dict, Any
from app.db import get_session
from app.services import AuthService
from app.models import UserCreate, UserRead, UserResetPassword
from app.core import Token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Registrar nuevo usuario
    
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    - **age**: Edad (opcional)
    - **gender**: Género (opcional)
    """
    result = await AuthService.register(session, user_data)
    return {
        "message": result["message"],
        "user": UserRead.model_validate(result["user"])
    }


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login con email y contraseña
    
    - **username**: Email del usuario (FastAPI usa 'username' por estándar OAuth2)
    - **password**: Contraseña
    
    Retorna access_token y refresh_token
    """
    return AuthService.login(session, form_data.username, form_data.password)


@router.post("/google", response_model=Token)
async def google_login(
    id_token: str,
    session: Session = Depends(get_session)
):
    """
    Login o registro con Google OAuth2
    
    - **id_token**: Google ID token obtenido del cliente
    
    Retorna access_token y refresh_token
    """
    return await AuthService.google_login(session, id_token)


@router.post("/verify-email", response_model=Dict[str, str])
async def verify_email(
    token: str,
    session: Session = Depends(get_session)
):
    """
    Verificar email con token
    
    - **token**: Token de verificación enviado por email
    """
    result = await AuthService.verify_email(session, token)
    return {"message": result["message"]}


@router.post("/request-password-reset", response_model=Dict[str, str])
async def request_password_reset(
    email: str,
    session: Session = Depends(get_session)
):
    """
    Solicitar reset de contraseña
    
    - **email**: Email de la cuenta
    
    Envía un email con el link de reset
    """
    return await AuthService.request_password_reset(session, email)


@router.post("/reset-password", response_model=Dict[str, str])
def reset_password(
    reset_data: UserResetPassword,
    session: Session = Depends(get_session)
):
    """
    Resetear contraseña con token
    
    - **token**: Token de reset recibido por email
    - **new_password**: Nueva contraseña
    """
    return AuthService.reset_password(session, reset_data.token, reset_data.new_password)


@router.post("/refresh", response_model=Token)
def refresh_token(
    user_id: int,
    session: Session = Depends(get_session)
):
    """
    Refrescar access token
    
    - **user_id**: ID del usuario
    """
    return AuthService.refresh_access_token(session, user_id)

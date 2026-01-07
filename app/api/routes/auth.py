from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Dict, Any, Optional, Union
from app.db import get_session
from app.services import AuthService, OTPService
from app.models import (
    UserCreate, UserRead, UserResetPassword, 
    OTPVerifyRequest, LoginWithOTPResponse, TrustedDeviceRead
)
from app.core import Token, get_current_user
from app.models import User


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


@router.post("/login", response_model=Union[Token, LoginWithOTPResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    device_id: Optional[str] = Header(None, alias="X-Device-ID"),
    session: Session = Depends(get_session)
):
    """
    Login con email y contraseña
    
    - **username**: Email del usuario (FastAPI usa 'username' por estándar OAuth2)
    - **password**: Contraseña
    - **X-Device-ID**: (Header opcional) ID único del dispositivo para verificar si es de confianza
    
    Retorna:
    - access_token y refresh_token si el login es exitoso y no requiere OTP
    - otp_required=true si necesita verificar OTP (primer login o dispositivo no confiable)
    """
    return await AuthService.login(session, form_data.username, form_data.password, device_id)


@router.post("/verify-otp", response_model=Token)
async def verify_otp(
    otp_data: OTPVerifyRequest,
    session: Session = Depends(get_session)
):
    """
    Verificar código OTP para completar login
    
    - **email**: Email del usuario
    - **otp_code**: Código OTP de 6 dígitos recibido por email
    - **device_id**: ID único del dispositivo
    - **device_name**: (Opcional) Nombre descriptivo del dispositivo
    - **device_type**: (Opcional) Tipo de dispositivo (android, ios, web)
    - **remember_device**: Si es true, el dispositivo se guardará como confiable
    
    Retorna access_token y refresh_token
    """
    return await AuthService.verify_login_otp(session, otp_data)


@router.post("/resend-otp", response_model=Dict[str, str])
async def resend_otp(
    email: str,
    session: Session = Depends(get_session)
):
    """
    Reenviar código OTP
    
    - **email**: Email del usuario
    """
    return await AuthService.resend_otp(session, email)


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
    Activar cuenta con token de email
    
    - **token**: Token de activación enviado por email
    """
    result = await AuthService.verify_email(session, token)
    return {"message": result["message"]}


@router.post("/resend-activation", response_model=Dict[str, str])
async def resend_activation(
    email: str,
    session: Session = Depends(get_session)
):
    """
    Reenviar email de activación de cuenta
    
    - **email**: Email de la cuenta
    """
    return await AuthService.resend_activation_email(session, email)


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


# =========================
# TRUSTED DEVICES ENDPOINTS
# =========================

@router.get("/devices", response_model=list[TrustedDeviceRead])
def get_trusted_devices(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Obtener lista de dispositivos de confianza del usuario actual
    
    Requiere autenticación
    """
    return OTPService.get_user_trusted_devices(session, current_user.id)


@router.delete("/devices/{device_id}", response_model=Dict[str, str])
def remove_trusted_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Eliminar un dispositivo de confianza
    
    - **device_id**: ID del dispositivo a eliminar
    
    Requiere autenticación
    """
    OTPService.remove_trusted_device(session, current_user.id, device_id)
    return {"message": "Device removed successfully"}


@router.delete("/devices", response_model=Dict[str, Any])
def remove_all_trusted_devices(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Eliminar todos los dispositivos de confianza del usuario
    
    Requiere autenticación
    """
    count = OTPService.remove_all_trusted_devices(session, current_user.id)
    return {"message": f"Removed {count} trusted devices", "count": count}

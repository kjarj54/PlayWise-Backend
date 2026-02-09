from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from typing import List
from app.db import get_session
from app.services import UserService
from app.models import (
    User, UserRead, UserReadPrivate, UserUpdate, 
    UserUpdatePassword, UserRole, UserSearchResult
)
from app.core import (
    get_current_user, get_current_active_user, 
    get_admin_user
)
from app.core.email import (
    send_email_change_verification,
    send_email_changed_notification
)
from pydantic import BaseModel, EmailStr


router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# SCHEMAS
# =========================
class EmailChangeRequest(BaseModel):
    """Schema para solicitar cambio de email"""
    new_email: EmailStr


class EmailChangeVerification(BaseModel):
    """Schema para verificar cambio de email"""
    token: str


# =========================
# USER PROFILE ROUTES
# =========================
@router.get("/me", response_model=UserReadPrivate)
def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener perfil del usuario actual (datos privados)
    
    Requiere autenticación
    """
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtener usuario por ID (datos públicos)
    
    - **user_id**: ID del usuario
    """
    user = UserService.get_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/username/{username}", response_model=UserRead)
def get_user_by_username(
    username: str,
    session: Session = Depends(get_session)
):
    """
    Obtener usuario por username (datos públicos)
    
    - **username**: Username del usuario
    """
    user = UserService.get_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/search/", response_model=List[UserSearchResult])
def search_users(
    search: str,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Buscar usuarios por username (datos públicos)
    
    - **search**: Término de búsqueda (username)
    - **limit**: Número máximo de resultados (default: 20)
    
    Requiere autenticación
    """
    from app.models import Friend, FriendStatus
    
    statement = select(User).where(
        User.is_active == True,
        col(User.username).ilike(f"%{search}%")
    ).limit(limit)
    
    users = session.exec(statement).all()
    
    # Add friendship status for each user
    results = []
    for user in users:
        # Check friendship status
        friendship = session.exec(
            select(Friend).where(
                (
                    ((Friend.requester_id == current_user.id) & (Friend.receiver_id == user.id)) |
                    ((Friend.requester_id == user.id) & (Friend.receiver_id == current_user.id))
                )
            )
        ).first()
        
        status = None
        if friendship:
            if friendship.status == FriendStatus.ACCEPTED:
                status = "accepted"
            elif friendship.status == FriendStatus.PENDING:
                # Determine if current user sent or received the request
                if friendship.requester_id == current_user.id:
                    status = "sent_pending"
                else:
                    status = "pending"
        
        user_dict = user.dict()
        user_dict['friendship_status'] = status
        results.append(UserSearchResult(**user_dict))
    
    return results


@router.put("/me", response_model=UserRead)
def update_my_profile(
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualizar perfil del usuario actual
    
    - **username**: Nuevo username (opcional)
    - **email**: Nuevo email (opcional, requiere re-verificación)
    - **age**: Nueva edad (opcional)
    - **gender**: Nuevo género (opcional)
    - **profile_picture**: Nueva foto de perfil (opcional)
    
    Requiere autenticación
    """
    return UserService.update_user(session, current_user.id, user_data)


@router.put("/me/password")
def change_password(
    password_data: UserUpdatePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cambiar contraseña del usuario actual
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña
    
    Requiere autenticación
    """
    UserService.update_password(session, current_user.id, password_data)
    return {"message": "Password updated successfully"}


# =========================
# EMAIL CHANGE ROUTES
# =========================
@router.post("/me/request-email-change")
async def request_email_change(
    email_data: EmailChangeRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Solicitar cambio de correo electrónico
    
    Este endpoint:
    1. Valida que el nuevo email no esté en uso
    2. Desactiva temporalmente la cuenta por seguridad
    3. Envía un email de verificación al nuevo correo
    4. El usuario debe confirmar mediante el link recibido
    
    - **new_email**: Nuevo correo electrónico
    
    Requiere autenticación
    """
    # Solicitar cambio de email
    user = UserService.request_email_change(
        session, 
        current_user.id, 
        email_data.new_email
    )
    
    # Enviar email de verificación al nuevo correo
    email_sent = await send_email_change_verification(
        user.pending_email,
        user.username,
        user.email_change_token
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {
        "message": "Verification email sent. Please check your new email to confirm the change.",
        "new_email": user.pending_email,
        "expires_at": user.email_change_expires
    }


@router.post("/verify-email-change")
async def verify_email_change(
    verification_data: EmailChangeVerification,
    session: Session = Depends(get_session)
):
    """
    Confirmar cambio de correo electrónico
    
    Este endpoint:
    1. Valida el token de verificación
    2. Actualiza el email a la nueva dirección
    3. Reactiva la cuenta
    4. Envía notificación al correo anterior
    
    - **token**: Token de verificación recibido por email
    
    No requiere autenticación (se usa el token)
    """
    # Confirmar cambio de email
    user = UserService.confirm_email_change(session, verification_data.token)
    
    # Enviar notificación al correo anterior
    old_email = getattr(user, '_old_email', None)
    if old_email:
        await send_email_changed_notification(old_email, user.username)
    
    return {
        "message": "Email changed successfully. Your account has been reactivated.",
        "new_email": user.email
    }


@router.post("/me/cancel-email-change")
def cancel_email_change(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # Permite usuarios inactivos
):
    """
    Cancelar cambio de correo electrónico pendiente
    
    Este endpoint:
    1. Cancela el cambio de email pendiente
    2. Reactiva la cuenta
    
    Útil si el usuario cambió de opinión o cometió un error.
    
    Requiere autenticación
    """
    user = UserService.cancel_email_change(session, current_user.id)
    
    return {
        "message": "Email change cancelled successfully. Your account has been reactivated.",
        "email": user.email
    }


# =========================
# ACCOUNT DELETION ROUTES
# =========================
@router.delete("/me")
def deactivate_my_account(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desactivar cuenta del usuario actual (soft delete)
    
    La cuenta será desactivada pero los datos permanecerán en el sistema.
    Para eliminar permanentemente la cuenta, usa el endpoint /me/delete-permanently
    
    Requiere autenticación
    """
    UserService.delete_user(session, current_user.id)
    return {"message": "Account deactivated successfully"}


@router.delete("/me/delete-permanently")
async def delete_account_permanently(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar cuenta permanentemente (hard delete)
    
    ⚠️ **ADVERTENCIA: Esta acción es IRREVERSIBLE** ⚠️
    
    Este endpoint eliminará completamente:
    - Tu perfil de usuario
    - Todas tus listas de deseos (wishlists)
    - Todas tus solicitudes de amistad (enviadas y recibidas)
    - Todas tus calificaciones de juegos
    - Todos tus comentarios
    - Todos tus dispositivos de confianza
    - Todos tus códigos OTP
    
    No podrás recuperar estos datos después de la eliminación.
    
    Requiere autenticación
    """
    success = UserService.delete_account_permanently(session, current_user.id)
    
    if success:
        return {
            "message": "Account and all associated data deleted permanently. We're sorry to see you go!"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


# =========================
# ADMIN ROUTES
# =========================
@router.get("/", response_model=List[UserRead])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    """
    Obtener lista de usuarios (solo admin)
    
    - **skip**: Número de usuarios a saltar (paginación)
    - **limit**: Número máximo de usuarios a retornar
    - **is_active**: Filtrar por estado activo (opcional)
    
    Requiere rol de administrador
    """
    return UserService.get_all(session, skip, limit, is_active)


@router.delete("/{user_id}")
def delete_user_admin(
    user_id: int,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    """
    Desactivar usuario (solo admin)
    
    - **user_id**: ID del usuario a desactivar
    
    Requiere rol de administrador
    """
    UserService.delete_user(session, user_id)
    return {"message": "User deactivated successfully"}

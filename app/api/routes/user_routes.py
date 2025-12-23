from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from app.db import get_session
from app.services import UserService
from app.models import (
    User, UserRead, UserReadPrivate, UserUpdate, 
    UserUpdatePassword, UserRole
)
from app.core import (
    get_current_user, get_current_active_user, 
    get_admin_user
)


router = APIRouter(prefix="/users", tags=["Users"])


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


@router.delete("/me")
def delete_my_account(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desactivar cuenta del usuario actual (soft delete)
    
    Requiere autenticación
    """
    UserService.delete_user(session, current_user.id)
    return {"message": "Account deactivated successfully"}


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

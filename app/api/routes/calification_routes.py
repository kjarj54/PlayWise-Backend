from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List
from app.db import get_session
from app.services import CalificationService
from app.models import (
    User, CalificationGame, CalificationCreate, 
    CalificationRead, CalificationUpdate
)
from app.core import get_current_active_user


router = APIRouter(prefix="/califications", tags=["Califications"])


@router.get("/me", response_model=List[CalificationRead])
def get_my_califications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener mis calificaciones
    
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (1-100)
    
    Requiere autenticación
    """
    return CalificationService.get_user_califications(
        session, current_user.id, skip, limit
    )


@router.get("/game/{game_id}", response_model=List[CalificationRead])
def get_game_califications(
    game_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Obtener calificaciones de un juego
    
    - **game_id**: ID del juego
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (1-100)
    """
    return CalificationService.get_game_califications(
        session, game_id, skip, limit
    )


@router.get("/game/{game_id}/average", response_model=dict)
def get_game_average_rating(
    game_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtener promedio de calificaciones de un juego
    
    - **game_id**: ID del juego
    
    Retorna:
    - **game_id**: ID del juego
    - **average_score**: Puntuación promedio (0-10)
    - **total_ratings**: Total de calificaciones
    """
    return CalificationService.get_game_average_rating(session, game_id)


@router.get("/game/{game_id}/me", response_model=CalificationRead)
def get_my_game_calification(
    game_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener mi calificación de un juego específico
    
    - **game_id**: ID del juego
    
    Requiere autenticación
    """
    calification = CalificationService.get_user_game_calification(
        session, current_user.id, game_id
    )
    if not calification:
        return None
    return calification


@router.post("/", response_model=CalificationRead, status_code=status.HTTP_201_CREATED)
def create_calification(
    calification_data: CalificationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crear calificación para un juego
    
    - **game_id**: ID del juego (requerido)
    - **score**: Puntuación 1-10 (requerido)
    - **review**: Reseña opcional (max 1000 caracteres)
    
    Requiere autenticación
    """
    return CalificationService.create_calification(
        session, current_user.id, calification_data
    )


@router.put("/{calification_id}", response_model=CalificationRead)
def update_calification(
    calification_id: int,
    calification_data: CalificationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualizar mi calificación
    
    - **calification_id**: ID de la calificación a actualizar
    - **score**: Nueva puntuación 1-10 (opcional)
    - **review**: Nueva reseña (opcional)
    
    Requiere autenticación
    """
    return CalificationService.update_calification(
        session, current_user.id, calification_id, calification_data
    )


@router.delete("/{calification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calification(
    calification_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar mi calificación
    
    - **calification_id**: ID de la calificación a eliminar
    
    Requiere autenticación
    """
    CalificationService.delete_calification(
        session, current_user.id, calification_id
    )
    return None

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
from app.db import get_session
from app.services import GameService
from app.models import User, Game, GameCreate, GameRead, GameUpdate
from app.core import get_current_user, get_admin_user, get_current_user_optional


router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/", response_model=List[GameRead])
def get_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    search: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Obtener lista de juegos
    
    - **skip**: Número de juegos a saltar (paginación)
    - **limit**: Número máximo de juegos (1-100)
    - **genre**: Filtrar por género (opcional)
    - **search**: Buscar en nombre y descripción (opcional)
    """
    return GameService.get_all(session, skip, limit, genre, search)


@router.get("/search", response_model=List[GameRead])
def search_games(
    q: str = Query(..., min_length=1, description="Texto de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Buscar juegos por nombre o descripción
    
    - **q**: Texto de búsqueda
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (1-100)
    """
    return GameService.search_games(session, q, skip, limit)


@router.get("/{game_id}", response_model=GameRead)
def get_game(
    game_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtener juego por ID
    
    - **game_id**: ID del juego
    """
    game = GameService.get_by_id(session, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game


@router.post("/", response_model=GameRead, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_game(
    game_data: GameCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crear nuevo juego (solo admin)
    
    - **name**: Nombre del juego (requerido)
    - **genre**: Género (opcional)
    - **api_id**: ID de API externa (opcional)
    - **description**: Descripción (opcional)
    - **cover_image**: URL de portada (opcional)
    - **release_date**: Fecha de lanzamiento (opcional)
    - **platforms**: Plataformas (opcional)
    - **developer**: Desarrollador (opcional)
    - **publisher**: Distribuidor (opcional)
    
    Requiere rol de administrador
    """
    return GameService.create_game(session, game_data)


@router.get("/by-api-id/{api_id}", response_model=GameRead)
def get_game_by_api_id(
    api_id: str,
    session: Session = Depends(get_session)
):
    """Obtener juego por api_id externo"""
    game = GameService.get_by_api_id(session, api_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game


@router.put("/{game_id}", response_model=GameRead)
def update_game(
    game_id: int,
    game_data: GameUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    """
    Actualizar juego (solo admin)
    
    - **game_id**: ID del juego a actualizar
    
    Requiere rol de administrador
    """
    return GameService.update_game(session, game_id, game_data)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    """
    Eliminar juego (solo admin)
    
    - **game_id**: ID del juego a eliminar
    
    Requiere rol de administrador
    """
    GameService.delete_game(session, game_id)
    return None

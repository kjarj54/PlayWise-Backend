from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List
from app.db import get_session
from app.services import WishListService
from app.models import User, WishList, WishListCreate, WishListRead
from app.core import get_current_active_user


base_router = APIRouter(tags=["Wishlist"])


@base_router.get("/", response_model=List[dict])
def get_my_wishlist(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    game_id: int | None = Query(None, description="Filtrar por game_id"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener wishlist del usuario actual con información completa del juego
    
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (1-100)
    
    Requiere autenticación
    """
    return WishListService.get_user_wishlist(
        session,
        current_user.id,
        skip,
        limit,
        game_id=game_id,
    )


@base_router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    wishlist_data: WishListCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Agregar juego a wishlist
    
    - **game_id**: ID del juego a agregar (requerido)
    - **url**: URL de la tienda (opcional)
    
    Requiere autenticación
    """
    return WishListService.add_to_wishlist(session, current_user.id, wishlist_data)


@base_router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    wishlist_id: str,  # Aceptar como string para preservar precisión con números grandes
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar juego de wishlist usando el ID del item de wishlist
    
    - **wishlist_id**: ID del item de wishlist a eliminar
    
    Requiere autenticación
    """
    WishListService.remove_from_wishlist(session, current_user.id, int(wishlist_id))
    return None


@base_router.get("/check/{game_id}", response_model=dict)
def check_in_wishlist(
    game_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verificar si un juego está en wishlist
    
    - **game_id**: ID del juego a verificar
    
    Requiere autenticación
    """
    in_wishlist = WishListService.is_in_wishlist(session, current_user.id, game_id)
    return {"in_wishlist": in_wishlist}


@base_router.get("/common/{friend_user_id}", response_model=List[dict])
def get_common_wishlist_games(
    friend_user_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener juegos en común en wishlist entre el usuario actual y otro usuario
    
    - **friend_user_id**: ID del otro usuario
    
    Requiere autenticación
    """
    return WishListService.get_common_wishlist_games(
        session,
        current_user.id,
        int(friend_user_id)
    )


# Exponer con prefijos plural y singular para compatibilidad
router = APIRouter(prefix="/wishlists", tags=["Wishlist"])
router.include_router(base_router)

legacy_router = APIRouter(prefix="/wishlist", tags=["Wishlist"])
legacy_router.include_router(base_router)

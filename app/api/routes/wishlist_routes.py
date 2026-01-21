from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List, Optional
from app.db import get_session
from app.services import WishListService
from app.models import User, WishList, WishListCreate, WishListRead
from app.core import get_current_active_user


router = APIRouter(prefix="/wishlist", tags=["Wishlist"])
router_plural = APIRouter(prefix="/wishlists", tags=["Wishlist"])


def register_routes(r: APIRouter) -> None:
    @r.get("/", response_model=List[WishListRead])
    def get_my_wishlist(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        game_id: Optional[int] = Query(None, description="Filtrar por game_id"),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
    ):
        """
        Obtener wishlist del usuario actual. Permite filtrar por game_id.
        """
        return WishListService.get_user_wishlist(session, current_user.id, skip, limit, game_id)

    @r.post("/", response_model=WishListRead, status_code=status.HTTP_201_CREATED)
    def add_to_wishlist(
        wishlist_data: WishListCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
    ):
        """Agregar juego a wishlist"""
        return WishListService.add_to_wishlist(session, current_user.id, wishlist_data)

    @r.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
    def remove_from_wishlist(
        wishlist_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
    ):
        """Eliminar juego de wishlist"""
        WishListService.remove_from_wishlist(session, current_user.id, wishlist_id)
        return None

    @r.get("/check/{game_id}", response_model=dict)
    def check_in_wishlist(
        game_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
    ):
        """Verificar si un juego está en wishlist"""
        in_wishlist = WishListService.is_in_wishlist(session, current_user.id, game_id)
        return {"in_wishlist": in_wishlist}


register_routes(router)
register_routes(router_plural)

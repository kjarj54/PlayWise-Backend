from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.models import WishList, WishListCreate
from app.services.game_service import GameService


class WishListService:
    """Servicio para operaciones de WishList"""
    
    @staticmethod
    def get_user_wishlist(
        session: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        game_id: Optional[int] = None,
    ) -> List[WishList]:
        """Obtener wishlist de un usuario"""
        statement = select(WishList).where(WishList.user_id == user_id)

        if game_id:
            statement = statement.where(WishList.game_id == game_id)

        statement = statement.offset(skip).limit(limit)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    def add_to_wishlist(
        session: Session,
        user_id: int,
        wishlist_data: WishListCreate
    ) -> WishList:
        """Agregar juego a wishlist"""
        # Verificar que el juego existe
        game = GameService.get_by_id(session, wishlist_data.game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        # Verificar que no esté ya en wishlist
        statement = select(WishList).where(
            (WishList.user_id == user_id) &
            (WishList.game_id == wishlist_data.game_id)
        )
        existing = session.exec(statement).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game already in wishlist"
            )
        
        wishlist_item = WishList(
            user_id=user_id,
            game_id=wishlist_data.game_id,
            url=wishlist_data.url
        )
        
        session.add(wishlist_item)
        session.commit()
        session.refresh(wishlist_item)
        
        return wishlist_item
    
    @staticmethod
    def remove_from_wishlist(
        session: Session,
        user_id: int,
        wishlist_id: int
    ) -> bool:
        """Eliminar juego de wishlist"""
        wishlist_item = session.get(WishList, wishlist_id)
        
        if not wishlist_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist item not found"
            )
        
        # Verificar que sea del usuario
        if wishlist_item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item"
            )
        
        session.delete(wishlist_item)
        session.commit()
        
        return True
    
    @staticmethod
    def is_in_wishlist(session: Session, user_id: int, game_id: int) -> bool:
        """Verificar si un juego está en wishlist"""
        statement = select(WishList).where(
            (WishList.user_id == user_id) &
            (WishList.game_id == game_id)
        )
        return session.exec(statement).first() is not None

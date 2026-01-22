from sqlmodel import Session, select
from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from app.models import WishList, WishListCreate, Game
from app.services.game_service import GameService


class WishListService:
    """Servicio para operaciones de WishList"""
    
    @staticmethod
    def get_user_wishlist(
        session: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        game_id: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Obtener wishlist de un usuario con datos completos del juego"""
        statement = select(WishList).where(WishList.user_id == user_id)

        if game_id is not None:
            statement = statement.where(WishList.game_id == game_id)

        statement = statement.offset(skip).limit(limit)
        
        wishlist_items = list(session.exec(statement).all())
        
        # Enriquecer con datos del juego
        result = []
        for item in wishlist_items:
            game = GameService.get_by_id(session, item.game_id)
            if game:
                result.append({
                    "id": item.id,
                    "game_id": item.game_id,
                    "user_id": item.user_id,
                    "url": item.url,
                    "added_at": item.added_at,
                    "game_name": game.name,
                    "game_genre": game.genre,
                    "game_api_id": game.api_id,
                    "game_description": game.description,
                    "game_api_rating": game.api_rating,
                    "game_cover_image": game.cover_image,
                    "game_release_date": game.release_date,
                    "game_platforms": game.platforms,
                    "game_developer": game.developer,
                    "game_publisher": game.publisher,
                })
        
        return result
    
    @staticmethod
    def add_to_wishlist(
        session: Session,
        user_id: int,
        wishlist_data: WishListCreate
    ) -> WishList:
        """Agregar juego a wishlist usando api_id"""
        # Buscar el juego por api_id en lugar de ID numérico
        print(f"🔍 Buscando juego por api_id={wishlist_data.api_id}")
        game = GameService.get_by_api_id(session, wishlist_data.api_id)
        if not game:
            print(f"❌ Juego con api_id={wishlist_data.api_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with api_id {wishlist_data.api_id} not found. Create it first."
            )
        print(f"✅ Juego encontrado: {game.name} (ID={game.id}, api_id={game.api_id})")
        
        # Verificar que no esté ya en wishlist (usar game.id que acabamos de obtener)
        statement = select(WishList).where(
            (WishList.user_id == user_id) &
            (WishList.game_id == game.id)
        )
        existing = session.exec(statement).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game already in wishlist"
            )
        
        wishlist_item = WishList(
            user_id=user_id,
            game_id=game.id,  # Usar el ID del juego encontrado
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

from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from app.models import Game, GameCreate, GameUpdate


class GameService:
    """Servicio para operaciones CRUD de juegos"""
    
    @staticmethod
    def get_by_id(session: Session, game_id: int) -> Optional[Game]:
        """Obtener juego por ID"""
        return session.get(Game, game_id)
    
    @staticmethod
    def get_by_api_id(session: Session, api_id: str) -> Optional[Game]:
        """Obtener juego por API ID"""
        statement = select(Game).where(Game.api_id == api_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        genre: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Game]:
        """Obtener lista de juegos con filtros"""
        statement = select(Game)
        
        if genre:
            statement = statement.where(Game.genre.contains(genre))
        
        if search:
            statement = statement.where(
                (Game.name.contains(search)) | 
                (Game.description.contains(search))
            )
        
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    def create_game(session: Session, game_data: GameCreate) -> Game:
        """Crear nuevo juego. Si ya existe por api_id, retorna el existente (idempotente)."""
        if game_data.api_id:
            existing_game = GameService.get_by_api_id(session, game_data.api_id)
            if existing_game:
                return existing_game

        game = Game(**game_data.model_dump())
        session.add(game)
        session.commit()
        session.refresh(game)

        return game

    @staticmethod
    def ensure_by_api_id(session: Session, game_data: GameCreate) -> Game:
        """Obtener o crear juego usando api_id como clave única."""
        if not game_data.api_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="api_id is required to ensure game record"
            )

        existing = GameService.get_by_api_id(session, game_data.api_id)
        if existing:
            return existing

        return GameService.create_game(session, game_data)
    
    @staticmethod
    def update_game(
        session: Session,
        game_id: int,
        game_data: GameUpdate
    ) -> Game:
        """Actualizar juego"""
        game = GameService.get_by_id(session, game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        # Actualizar solo campos no nulos
        update_data = game_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(game, key, value)
        
        game.updated_at = datetime.utcnow()
        
        session.add(game)
        session.commit()
        session.refresh(game)
        
        return game
    
    @staticmethod
    def delete_game(session: Session, game_id: int) -> bool:
        """Eliminar juego"""
        game = GameService.get_by_id(session, game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        session.delete(game)
        session.commit()
        
        return True
    
    @staticmethod
    def search_games(
        session: Session,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Game]:
        """Buscar juegos por nombre o descripción"""
        statement = select(Game).where(
            (Game.name.ilike(f"%{query}%")) |
            (Game.description.ilike(f"%{query}%"))
        ).offset(skip).limit(limit)
        
        return list(session.exec(statement).all())

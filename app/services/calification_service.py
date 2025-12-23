from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.models import CalificationGame, CalificationCreate, CalificationUpdate
from app.services.game_service import GameService


class CalificationService:
    """Servicio para operaciones de calificaciones"""
    
    @staticmethod
    def get_user_califications(
        session: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalificationGame]:
        """Obtener calificaciones de un usuario"""
        statement = select(CalificationGame).where(
            CalificationGame.user_id == user_id
        ).offset(skip).limit(limit)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_game_califications(
        session: Session,
        game_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalificationGame]:
        """Obtener calificaciones de un juego"""
        statement = select(CalificationGame).where(
            CalificationGame.game_id == game_id
        ).offset(skip).limit(limit)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_user_game_calification(
        session: Session,
        user_id: int,
        game_id: int
    ) -> Optional[CalificationGame]:
        """Obtener calificación específica de un usuario para un juego"""
        statement = select(CalificationGame).where(
            (CalificationGame.user_id == user_id) &
            (CalificationGame.game_id == game_id)
        )
        return session.exec(statement).first()
    
    @staticmethod
    def create_calification(
        session: Session,
        user_id: int,
        calification_data: CalificationCreate
    ) -> CalificationGame:
        """Crear calificación"""
        # Verificar que el juego existe
        game = GameService.get_by_id(session, calification_data.game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        # Verificar que no haya calificado antes
        existing = CalificationService.get_user_game_calification(
            session, user_id, calification_data.game_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already rated this game. Use update instead."
            )
        
        calification = CalificationGame(
            user_id=user_id,
            game_id=calification_data.game_id,
            score=calification_data.score,
            review=calification_data.review
        )
        
        session.add(calification)
        session.commit()
        session.refresh(calification)
        
        return calification
    
    @staticmethod
    def update_calification(
        session: Session,
        user_id: int,
        calification_id: int,
        calification_data: CalificationUpdate
    ) -> CalificationGame:
        """Actualizar calificación"""
        calification = session.get(CalificationGame, calification_id)
        
        if not calification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calification not found"
            )
        
        # Verificar que sea del usuario
        if calification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this calification"
            )
        
        # Actualizar campos
        if calification_data.score is not None:
            calification.score = calification_data.score
        if calification_data.review is not None:
            calification.review = calification_data.review
        
        calification.updated_at = datetime.utcnow()
        
        session.add(calification)
        session.commit()
        session.refresh(calification)
        
        return calification
    
    @staticmethod
    def delete_calification(
        session: Session,
        user_id: int,
        calification_id: int
    ) -> bool:
        """Eliminar calificación"""
        calification = session.get(CalificationGame, calification_id)
        
        if not calification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calification not found"
            )
        
        # Verificar que sea del usuario
        if calification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this calification"
            )
        
        session.delete(calification)
        session.commit()
        
        return True
    
    @staticmethod
    def get_game_average_rating(session: Session, game_id: int) -> dict:
        """Obtener promedio de calificaciones de un juego"""
        statement = select(
            func.avg(CalificationGame.score).label("average"),
            func.count(CalificationGame.id).label("count")
        ).where(CalificationGame.game_id == game_id)
        
        result = session.exec(statement).first()
        
        return {
            "game_id": game_id,
            "average_score": float(result[0]) if result[0] else 0.0,
            "total_ratings": result[1] if result[1] else 0
        }

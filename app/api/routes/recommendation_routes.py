"""
Rutas para el sistema de recomendaciones con IA
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Dict, Optional
from app.db.database import get_session
from app.core.auth import get_current_user
from app.models.user import User
from app.services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/me", response_model=Dict)
async def get_my_recommendations(
    count: Optional[int] = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Obtiene recomendaciones personalizadas para el usuario actual
    
    - **count**: Número de recomendaciones (1-20, default: 5)
    
    Usa IA (Google Gemini) para generar recomendaciones basadas en:
    - Juegos calificados positivamente
    - Juegos en wishlist
    - Géneros favoritos
    """
    try:
        recommendation_service = RecommendationService()
        recommendations = recommendation_service.generate_recommendations(
            session=session,
            user_id=current_user.id,
            count=count
        )
        
        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendaciones: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=Dict)
async def get_user_recommendations(
    user_id: int,
    count: Optional[int] = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session)
):
    """
    Obtiene recomendaciones para cualquier usuario (público)
    
    - **user_id**: ID del usuario
    - **count**: Número de recomendaciones (1-20, default: 5)
    """
    try:
        recommendation_service = RecommendationService()
        recommendations = recommendation_service.generate_recommendations(
            session=session,
            user_id=user_id,
            count=count
        )
        
        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations,
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendaciones: {str(e)}"
        )


@router.get("/popular", response_model=Dict)
async def get_popular_recommendations(
    count: Optional[int] = Query(default=10, ge=1, le=50),
    session: Session = Depends(get_session)
):
    """
    Obtiene los juegos más populares (sin personalización)
    
    - **count**: Número de juegos (1-50, default: 10)
    
    Útil para usuarios nuevos sin historial
    """
    try:
        recommendation_service = RecommendationService()
        popular = recommendation_service.get_popular_games(
            session=session,
            count=count
        )
        
        return {
            "success": True,
            "count": len(popular),
            "recommendations": popular
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo juegos populares: {str(e)}"
        )


@router.get("/history/me", response_model=Dict)
async def get_my_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Obtiene el historial analizado del usuario actual
    
    Muestra qué datos usa la IA para generar recomendaciones:
    - Juegos con calificación alta
    - Juegos en wishlist
    - Géneros favoritos
    """
    try:
        history = RecommendationService.get_user_history(
            session=session,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )

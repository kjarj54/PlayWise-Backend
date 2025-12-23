from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


# =========================
# CALIFICATION BASE MODELS
# =========================
class CalificationGameBase(SQLModel):
    """Campos compartidos entre modelos de calificación"""
    game_id: int = Field(foreign_key="games.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    score: int = Field(ge=1, le=10)  # Puntuación del 1 al 10


class CalificationGame(CalificationGameBase, table=True):
    """Modelo de tabla CalificationGame en la base de datos"""
    __tablename__ = "calification_games"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Campos adicionales
    review: Optional[str] = Field(default=None, max_length=1000)  # Reseña opcional
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # user: Optional["User"] = Relationship(back_populates="califications")
    # game: Optional["Game"] = Relationship(back_populates="califications")


# =========================
# CALIFICATION SCHEMAS (DTOs)
# =========================
class CalificationCreate(SQLModel):
    """Schema para crear una calificación"""
    game_id: int
    score: int = Field(ge=1, le=10)
    review: Optional[str] = Field(default=None, max_length=1000)


class CalificationRead(SQLModel):
    """Schema para leer una calificación (respuesta API)"""
    id: int
    game_id: int
    user_id: int
    score: int
    review: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CalificationReadWithDetails(CalificationRead):
    """Schema para leer calificación con detalles del juego y usuario"""
    game_name: Optional[str] = None
    username: Optional[str] = None


class CalificationUpdate(SQLModel):
    """Schema para actualizar una calificación"""
    score: Optional[int] = Field(default=None, ge=1, le=10)
    review: Optional[str] = Field(default=None, max_length=1000)


class GameCalificationStats(SQLModel):
    """Schema para estadísticas de calificación de un juego"""
    game_id: int
    average_score: float
    total_ratings: int
    score_distribution: dict  # {1: count, 2: count, ..., 10: count}

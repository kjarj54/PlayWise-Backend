from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


# =========================
# GAME BASE MODELS
# =========================
class GameBase(SQLModel):
    """Campos compartidos entre modelos de juegos"""
    name: str = Field(index=True, max_length=255)
    genre: Optional[str] = Field(default=None, max_length=100)
    api_id: Optional[str] = Field(default=None, unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)
    api_rating: Optional[str] = Field(default=None, max_length=10)


class Game(GameBase, table=True):
    """Modelo de tabla Games en la base de datos"""
    __tablename__ = "games"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Campos adicionales
    cover_image: Optional[str] = Field(default=None, max_length=500)
    release_date: Optional[str] = Field(default=None, max_length=50)
    platforms: Optional[str] = Field(default=None, max_length=500)  # JSON string
    developer: Optional[str] = Field(default=None, max_length=255)
    publisher: Optional[str] = Field(default=None, max_length=255)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (se definirán después)
    # wishlists: List["WishList"] = Relationship(back_populates="game")
    # califications: List["CalificationGame"] = Relationship(back_populates="game")
    # comments: List["CommentUser"] = Relationship(back_populates="game")
    # stores: List["Store"] = Relationship(back_populates="game")


# =========================
# GAME SCHEMAS (DTOs)
# =========================
class GameCreate(SQLModel):
    """Schema para crear un juego"""
    name: str = Field(min_length=1, max_length=255)
    genre: Optional[str] = None
    api_id: Optional[str] = None
    description: Optional[str] = None
    api_rating: Optional[str] = None
    cover_image: Optional[str] = None
    release_date: Optional[str] = None
    platforms: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameRead(GameBase):
    """Schema para leer un juego (respuesta API)"""
    id: int
    cover_image: Optional[str] = None
    release_date: Optional[str] = None
    platforms: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    created_at: datetime


class GameUpdate(SQLModel):
    """Schema para actualizar un juego"""
    name: Optional[str] = Field(default=None, max_length=255)
    genre: Optional[str] = None
    description: Optional[str] = None
    api_rating: Optional[str] = None
    cover_image: Optional[str] = None
    release_date: Optional[str] = None
    platforms: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameSearch(SQLModel):
    """Schema para búsqueda de juegos"""
    query: Optional[str] = None
    genre: Optional[str] = None
    platform: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

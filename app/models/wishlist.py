from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


# =========================
# WISHLIST BASE MODELS
# =========================
class WishListBase(SQLModel):
    """Campos compartidos entre modelos de wishlist"""
    url: Optional[str] = Field(default=None, max_length=500)
    game_id: int = Field(foreign_key="games.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)


class WishList(WishListBase, table=True):
    """Modelo de tabla WishList en la base de datos"""
    __tablename__ = "wishlists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # user: Optional["User"] = Relationship(back_populates="wishlists")
    # game: Optional["Game"] = Relationship(back_populates="wishlists")


# =========================
# WISHLIST SCHEMAS (DTOs)
# =========================
class WishListCreate(SQLModel):
    """Schema para agregar a wishlist"""
    game_id: int
    url: Optional[str] = None


class WishListRead(SQLModel):
    """Schema para leer wishlist (respuesta API)"""
    id: int
    game_id: int
    user_id: int
    url: Optional[str] = None
    added_at: datetime


class WishListReadWithGame(WishListRead):
    """Schema para leer wishlist con datos del juego"""
    game_name: Optional[str] = None
    game_cover: Optional[str] = None
    game_genre: Optional[str] = None

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


# =========================
# STORE BASE MODELS
# =========================
class StoreBase(SQLModel):
    """Campos compartidos entre modelos de tiendas"""
    name: str = Field(max_length=100, index=True)
    game_id: int = Field(foreign_key="games.id", index=True)


class Store(StoreBase, table=True):
    """Modelo de tabla Stores en la base de datos"""
    __tablename__ = "stores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Campos adicionales
    store_url: Optional[str] = Field(default=None, max_length=500)
    store_logo: Optional[str] = Field(default=None, max_length=500)
    price: Optional[str] = Field(default=None, max_length=50)
    currency: Optional[str] = Field(default=None, max_length=10)
    discount_percent: Optional[int] = Field(default=None)
    original_price: Optional[str] = Field(default=None, max_length=50)
    views: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # game: Optional["Game"] = Relationship(back_populates="stores")


# =========================
# STORE SCHEMAS (DTOs)
# =========================
class StoreCreate(SQLModel):
    """Schema para crear una tienda"""
    name: str = Field(min_length=1, max_length=100)
    game_id: int
    store_url: Optional[str] = None
    store_logo: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    discount_percent: Optional[int] = None
    original_price: Optional[str] = None


class StoreRead(SQLModel):
    """Schema para leer una tienda (respuesta API)"""
    id: int
    name: str
    game_id: int
    store_url: Optional[str] = None
    store_logo: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    discount_percent: Optional[int] = None
    original_price: Optional[str] = None
    views: int
    created_at: datetime


class StoreReadWithGame(StoreRead):
    """Schema para leer tienda con datos del juego"""
    game_name: Optional[str] = None
    game_cover: Optional[str] = None


class StoreUpdate(SQLModel):
    """Schema para actualizar una tienda"""
    name: Optional[str] = Field(default=None, max_length=100)
    store_url: Optional[str] = None
    store_logo: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    discount_percent: Optional[int] = None
    original_price: Optional[str] = None

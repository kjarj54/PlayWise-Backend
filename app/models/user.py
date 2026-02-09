from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
from pydantic import field_serializer


class UserRole(str, Enum):
    """Roles de usuario disponibles"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AuthProvider(str, Enum):
    """Proveedores de autenticación"""
    LOCAL = "local"
    GOOGLE = "google"


# =========================
# USER BASE MODELS
# =========================
class UserBase(SQLModel):
    """Campos compartidos entre modelos de usuario"""
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=255)
    age: Optional[str] = Field(default=None, max_length=10)
    gender: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """Modelo de tabla Users en la base de datos"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(default=None, max_length=255)
    
    # OAuth2 fields
    auth_provider: AuthProvider = Field(default=AuthProvider.LOCAL)
    google_id: Optional[str] = Field(default=None, unique=True, index=True, max_length=255)
    profile_picture: Optional[str] = Field(default=None, max_length=500)
    
    # Security fields
    is_verified: bool = Field(default=False)
    is_email_activated: bool = Field(default=False)  # Activación por email
    otp_verified_once: bool = Field(default=False)  # Si ya verificó OTP al menos una vez
    verification_token: Optional[str] = Field(default=None, max_length=255)
    reset_password_token: Optional[str] = Field(default=None, max_length=255)
    reset_password_expires: Optional[datetime] = Field(default=None)
    
    # Email change fields
    pending_email: Optional[str] = Field(default=None, max_length=255)  # Nuevo email pendiente
    email_change_token: Optional[str] = Field(default=None, max_length=255)  # Token de confirmación
    email_change_expires: Optional[datetime] = Field(default=None)  # Expiración del token
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default=None)
    
    # Relationships (se importarán después para evitar circular imports)
    # wishlists: List["WishList"] = Relationship(back_populates="user")
    # califications: List["CalificationGame"] = Relationship(back_populates="user")
    # comments: List["CommentUser"] = Relationship(back_populates="user")
    # sent_friend_requests: List["Friend"] = Relationship(back_populates="requester")
    # received_friend_requests: List["Friend"] = Relationship(back_populates="receiver")


# =========================
# USER SCHEMAS (DTOs)
# =========================
class UserCreate(SQLModel):
    """Schema para crear un usuario (registro local)"""
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    age: Optional[str] = None
    gender: Optional[str] = None


class UserCreateGoogle(SQLModel):
    """Schema para crear un usuario desde Google OAuth"""
    email: str
    username: str
    google_id: str
    profile_picture: Optional[str] = None


class UserRead(SQLModel):
    """Schema para leer un usuario (respuesta API pública)"""
    id: int
    username: str
    email: str
    age: Optional[str] = None
    gender: Optional[str] = None
    role: UserRole
    profile_picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    auth_provider: AuthProvider
    created_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: int, _info):
        """Serialize ID as string to prevent JavaScript precision loss"""
        return str(value)


class UserReadPrivate(UserRead):
    """Schema para leer datos privados del usuario (solo el propio usuario)"""
    last_login: Optional[datetime] = None
    updated_at: datetime


class UserSearchResult(UserRead):
    """Schema para resultados de búsqueda con estado de relación"""
    friendship_status: Optional[str] = None  # None, 'pending', 'accepted', 'sent_pending'


class UserUpdate(SQLModel):
    """Schema para actualizar un usuario"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    age: Optional[str] = None
    gender: Optional[str] = None
    profile_picture: Optional[str] = None


class UserUpdatePassword(SQLModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


class UserResetPassword(SQLModel):
    """Schema para resetear contraseña"""
    token: str
    new_password: str = Field(min_length=8, max_length=100)

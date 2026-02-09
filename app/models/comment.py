from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from pydantic import field_serializer


# =========================
# COMMENT BASE MODELS
# =========================
class CommentUserBase(SQLModel):
    """Campos compartidos entre modelos de comentarios"""
    user_id: int = Field(foreign_key="users.id", index=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    content: str = Field(max_length=2000)


class CommentUser(CommentUserBase, table=True):
    """Modelo de tabla CommentUser en la base de datos"""
    __tablename__ = "comment_users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Campos adicionales
    is_public: bool = Field(default=True)
    is_edited: bool = Field(default=False)
    parent_comment_id: Optional[int] = Field(default=None, foreign_key="comment_users.id")  # Para respuestas
    likes_count: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    # user: Optional["User"] = Relationship(back_populates="comments")
    # game: Optional["Game"] = Relationship(back_populates="comments")
    # parent: Optional["CommentUser"] = Relationship(back_populates="replies")
    # replies: List["CommentUser"] = Relationship(back_populates="parent")


# =========================
# COMMENT SCHEMAS (DTOs)
# =========================
class CommentCreate(SQLModel):
    """Schema para crear un comentario"""
    game_id: int
    content: str = Field(min_length=1, max_length=2000)
    is_public: bool = True
    parent_comment_id: Optional[int] = None


class CommentCreateRequest(SQLModel):
    """Schema para crear un comentario con api_id o game_id"""
    api_id: Optional[str] = None  # RAWG game ID
    game_id: Optional[int] = None  # Internal DB game ID
    game_name: Optional[str] = None  # Game name for auto-creation
    content: str = Field(min_length=1, max_length=2000)
    is_public: bool = True
    parent_comment_id: Optional[int] = None


class CommentRead(SQLModel):
    """Schema para leer un comentario (respuesta API)"""
    id: int
    user_id: int
    game_id: int
    content: str
    is_public: bool
    is_edited: bool
    parent_comment_id: Optional[int] = None
    likes_count: int
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('id', 'user_id', 'game_id', 'parent_comment_id')
    def serialize_ids(self, value: Optional[int]) -> Optional[str]:
        """Convert large IDs to strings for JavaScript compatibility"""
        return str(value) if value is not None else None


class CommentReadWithUser(CommentRead):
    """Schema para leer comentario con datos del usuario"""
    username: str
    user_profile_picture: Optional[str] = None


class CommentReadWithReplies(CommentReadWithUser):
    """Schema para leer comentario con respuestas"""
    replies: list["CommentReadWithUser"] = []


class CommentUpdate(SQLModel):
    """Schema para actualizar un comentario"""
    content: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    is_public: Optional[bool] = None

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class CommentLike(SQLModel, table=True):
    """Modelo para rastrear likes de usuarios en comentarios"""
    __tablename__ = "comment_likes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    comment_id: int = Field(foreign_key="comment_users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        # Crear índice único compuesto para evitar likes duplicados
        table_args = (
            {"sqlite_autoincrement": True},
        )

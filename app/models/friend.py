from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class FriendStatus(str, Enum):
    """Estados posibles de una solicitud de amistad"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


# =========================
# FRIEND BASE MODELS
# =========================
class FriendBase(SQLModel):
    """Campos compartidos entre modelos de amigos"""
    requester_id: int = Field(foreign_key="users.id", index=True)
    receiver_id: int = Field(foreign_key="users.id", index=True)
    status: FriendStatus = Field(default=FriendStatus.PENDING)


class Friend(FriendBase, table=True):
    """Modelo de tabla Friends en la base de datos"""
    __tablename__ = "friends"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamps
    request_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_date: Optional[datetime] = Field(default=None)
    
    # Relationships
    # requester: Optional["User"] = Relationship(
    #     back_populates="sent_friend_requests",
    #     sa_relationship_kwargs={"foreign_keys": "[Friend.requester_id]"}
    # )
    # receiver: Optional["User"] = Relationship(
    #     back_populates="received_friend_requests",
    #     sa_relationship_kwargs={"foreign_keys": "[Friend.receiver_id]"}
    # )


# =========================
# FRIEND SCHEMAS (DTOs)
# =========================
class FriendRequestCreate(SQLModel):
    """Schema para enviar solicitud de amistad"""
    receiver_id: int


class FriendRequestResponse(SQLModel):
    """Schema para responder a solicitud de amistad"""
    status: FriendStatus = Field(description="accepted, rejected, or blocked")


class FriendRead(SQLModel):
    """Schema para leer una relación de amistad (respuesta API)"""
    id: int
    requester_id: int
    receiver_id: int
    status: FriendStatus
    request_date: datetime
    response_date: Optional[datetime] = None


class FriendReadWithUser(FriendRead):
    """Schema para leer amistad con datos del usuario"""
    friend_username: str
    friend_profile_picture: Optional[str] = None
    friend_is_active: bool = True


class FriendListResponse(SQLModel):
    """Schema para listar amigos"""
    friends: list[FriendReadWithUser] = []
    total: int = 0


class PendingRequestsResponse(SQLModel):
    """Schema para listar solicitudes pendientes"""
    sent_requests: list[FriendReadWithUser] = []
    received_requests: list[FriendReadWithUser] = []


class BlockedUsersResponse(SQLModel):
    """Schema para listar usuarios bloqueados"""
    blocked_users: list[FriendReadWithUser] = []
    total: int = 0

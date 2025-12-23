from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
from app.db import get_session
from app.services import FriendService
from app.models import (
    User, Friend, FriendRead, FriendRequestCreate, 
    FriendRequestResponse
)
from app.core import get_current_active_user


router = APIRouter(prefix="/friends", tags=["Friends"])


@router.get("/", response_model=List[FriendRead])
def get_my_friends(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista de amigos aceptados
    
    Requiere autenticación
    """
    return FriendService.get_friends(session, current_user.id)


@router.get("/pending", response_model=dict)
def get_pending_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener solicitudes de amistad pendientes
    
    Retorna:
    - **received**: Solicitudes recibidas
    - **sent**: Solicitudes enviadas
    
    Requiere autenticación
    """
    return FriendService.get_pending_requests(session, current_user.id)


@router.post("/request", response_model=FriendRead, status_code=status.HTTP_201_CREATED)
def send_friend_request(
    request_data: FriendRequestCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Enviar solicitud de amistad
    
    - **receiver_id**: ID del usuario a quien enviar la solicitud
    
    Requiere autenticación
    """
    return FriendService.send_friend_request(
        session, current_user.id, request_data
    )


@router.put("/request/{request_id}", response_model=FriendRead)
def respond_to_friend_request(
    request_id: int,
    response: FriendRequestResponse,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Responder a solicitud de amistad
    
    - **request_id**: ID de la solicitud
    - **status**: Estado de respuesta (accepted, rejected, blocked)
    
    Requiere autenticación
    """
    return FriendService.respond_friend_request(
        session, current_user.id, request_id, response
    )


@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_friend(
    friend_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar amigo
    
    - **friend_id**: ID del usuario a eliminar de amigos
    
    Requiere autenticación
    """
    FriendService.remove_friend(session, current_user.id, friend_id)
    return None


@router.post("/block/{user_id}", response_model=FriendRead)
def block_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Bloquear usuario
    
    - **user_id**: ID del usuario a bloquear
    
    Requiere autenticación
    """
    return FriendService.block_user(session, current_user.id, user_id)


@router.get("/check/{user_id}", response_model=dict)
def check_friendship(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verificar si dos usuarios son amigos
    
    - **user_id**: ID del otro usuario
    
    Requiere autenticación
    """
    are_friends = FriendService.are_friends(session, current_user.id, user_id)
    return {"are_friends": are_friends}

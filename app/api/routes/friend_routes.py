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


@router.get("/", response_model=List[dict])
def get_my_friends(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista de amigos aceptados con información del usuario
    
    Requiere autenticación
    """
    from app.models import UserRead
    
    friends = FriendService.get_friends(session, current_user.id)
    
    # Enrich with user data
    result = []
    for friend in friends:
        # Determine which user is the friend
        friend_id = friend.receiver_id if friend.requester_id == current_user.id else friend.requester_id
        friend_user = session.get(User, friend_id)
        
        if friend_user:
            result.append({
                "id": friend.id,
                "requester_id": str(friend.requester_id),
                "receiver_id": str(friend.receiver_id),
                "status": friend.status,
                "request_date": friend.request_date,
                "response_date": friend.response_date,
                "friend_user": {
                    "id": str(friend_user.id),
                    "username": friend_user.username,
                    "profile_picture": friend_user.profile_picture,
                }
            })
    
    return result


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
    pending = FriendService.get_pending_requests(session, current_user.id)
    
    # Enrich received requests with user data
    received_enriched = []
    for req in pending["received"]:
        requester = session.get(User, req.requester_id)
        if requester:
            received_enriched.append({
                "id": str(req.id),  # Convert to string
                "from_user": {
                    "id": str(requester.id),
                    "username": requester.username,
                    "profile_picture": requester.profile_picture,
                },
                "to_user": {
                    "id": str(current_user.id),
                    "username": current_user.username,
                },
                "status": req.status,
                "created_at": req.request_date.isoformat() if req.request_date else None,
            })
    
    # Enrich sent requests with user data
    sent_enriched = []
    for req in pending["sent"]:
        receiver = session.get(User, req.receiver_id)
        if receiver:
            sent_enriched.append({
                "id": str(req.id),  # Convert to string
                "from_user": {
                    "id": str(current_user.id),
                    "username": current_user.username,
                },
                "to_user": {
                    "id": str(receiver.id),
                    "username": receiver.username,
                    "profile_picture": receiver.profile_picture,
                },
                "status": req.status,
                "created_at": req.request_date.isoformat() if req.request_date else None,
            })
    
    return {
        "received": received_enriched,
        "sent": sent_enriched
    }


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

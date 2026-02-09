from sqlmodel import Session, select
from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from app.models import Friend, FriendStatus, FriendRequestCreate, FriendRequestResponse


class FriendService:
    """Servicio para sistema de amigos"""
    
    @staticmethod
    def get_friends(session: Session, user_id: int) -> List[Friend]:
        """Obtener lista de amigos aceptados"""
        statement = select(Friend).where(
            ((Friend.requester_id == user_id) | (Friend.receiver_id == user_id)) &
            (Friend.status == FriendStatus.ACCEPTED)
        )
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_pending_requests(session: Session, user_id: int) -> dict:
        """Obtener solicitudes pendientes (enviadas y recibidas)"""
        # Solicitudes recibidas
        received_statement = select(Friend).where(
            (Friend.receiver_id == user_id) &
            (Friend.status == FriendStatus.PENDING)
        )
        received = list(session.exec(received_statement).all())
        
        # Solicitudes enviadas
        sent_statement = select(Friend).where(
            (Friend.requester_id == user_id) &
            (Friend.status == FriendStatus.PENDING)
        )
        sent = list(session.exec(sent_statement).all())
        
        return {
            "received": received,
            "sent": sent
        }
    
    @staticmethod
    def send_friend_request(
        session: Session,
        requester_id: int,
        request_data: FriendRequestCreate
    ) -> Friend:
        """Enviar solicitud de amistad"""
        receiver_id = request_data.receiver_id
        
        # No puede enviarse solicitud a sí mismo
        if requester_id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send friend request to yourself"
            )
        
        # Verificar que el usuario receptor existe
        from app.models import User
        receiver = session.get(User, receiver_id)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verificar si ya existe una relación
        statement = select(Friend).where(
            ((Friend.requester_id == requester_id) & (Friend.receiver_id == receiver_id)) |
            ((Friend.requester_id == receiver_id) & (Friend.receiver_id == requester_id))
        )
        existing = session.exec(statement).first()
        
        if existing:
            if existing.status == FriendStatus.ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already friends"
                )
            elif existing.status == FriendStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Friend request already pending"
                )
            elif existing.status == FriendStatus.BLOCKED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot send friend request"
                )
        
        # Crear solicitud
        friend_request = Friend(
            requester_id=requester_id,
            receiver_id=receiver_id,
            status=FriendStatus.PENDING
        )
        
        session.add(friend_request)
        session.commit()
        session.refresh(friend_request)
        
        return friend_request
    
    @staticmethod
    def respond_friend_request(
        session: Session,
        user_id: int,
        request_id: int,
        response: FriendRequestResponse
    ) -> Friend:
        """Responder a solicitud de amistad"""
        friend_request = session.get(Friend, request_id)
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found"
            )
        
        # Verificar que sea el receptor
        if friend_request.receiver_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to respond to this request"
            )
        
        # Verificar que esté pendiente
        if friend_request.status != FriendStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request is not pending"
            )
        
        # Actualizar estado
        friend_request.status = response.status
        friend_request.response_date = datetime.utcnow()
        
        session.add(friend_request)
        session.commit()
        session.refresh(friend_request)
        
        return friend_request
    
    @staticmethod
    def remove_friend(session: Session, user_id: int, friend_id: int) -> bool:
        """Eliminar amigo"""
        statement = select(Friend).where(
            ((Friend.requester_id == user_id) & (Friend.receiver_id == friend_id)) |
            ((Friend.requester_id == friend_id) & (Friend.receiver_id == user_id))
        )
        friendship = session.exec(statement).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friendship not found"
            )
        
        session.delete(friendship)
        session.commit()
        
        return True
    
    @staticmethod
    def block_user(session: Session, user_id: int, target_user_id: int) -> Friend:
        """Bloquear usuario"""
        # Buscar relación existente
        statement = select(Friend).where(
            ((Friend.requester_id == user_id) & (Friend.receiver_id == target_user_id)) |
            ((Friend.requester_id == target_user_id) & (Friend.receiver_id == user_id))
        )
        relationship = session.exec(statement).first()
        
        if relationship:
            # Actualizar a bloqueado
            relationship.status = FriendStatus.BLOCKED
            relationship.response_date = datetime.utcnow()
            session.add(relationship)
        else:
            # Crear nueva relación bloqueada
            relationship = Friend(
                requester_id=user_id,
                receiver_id=target_user_id,
                status=FriendStatus.BLOCKED
            )
            session.add(relationship)
        
        session.commit()
        session.refresh(relationship)
        
        return relationship
    
    @staticmethod
    def are_friends(session: Session, user_id_1: int, user_id_2: int) -> bool:
        """Verificar si dos usuarios son amigos"""
        statement = select(Friend).where(
            ((Friend.requester_id == user_id_1) & (Friend.receiver_id == user_id_2)) |
            ((Friend.requester_id == user_id_2) & (Friend.receiver_id == user_id_1))
        ).where(Friend.status == FriendStatus.ACCEPTED)
        
        return session.exec(statement).first() is not None

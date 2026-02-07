from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models import (
    User, UserCreate, UserCreateGoogle, UserUpdate, 
    UserUpdatePassword, AuthProvider
)
from app.core import (
    hash_password, verify_password, validate_password_strength,
    generate_verification_token, generate_reset_password_token
)


class UserService:
    """Servicio para operaciones CRUD de usuarios"""
    
    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return session.get(User, user_id)
    
    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def get_by_username(session: Session, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()
    
    @staticmethod
    def get_by_google_id(session: Session, google_id: str) -> Optional[User]:
        """Obtener usuario por Google ID"""
        statement = select(User).where(User.google_id == google_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(
        session: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Obtener lista de usuarios con paginación"""
        statement = select(User).offset(skip).limit(limit)
        
        if is_active is not None:
            statement = statement.where(User.is_active == is_active)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    def create_user(session: Session, user_data: UserCreate) -> User:
        """Crear nuevo usuario con validaciones"""
        # Validar que el email no exista
        if UserService.get_by_email(session, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validar que el username no exista
        if UserService.get_by_username(session, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Validar fortaleza de contraseña
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Crear usuario
        user = User(
            username=user_data.username,
            email=user_data.email,
            age=user_data.age,
            gender=user_data.gender,
            hashed_password=hash_password(user_data.password),
            auth_provider=AuthProvider.LOCAL,
            verification_token=generate_verification_token(),
            is_verified=False
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def create_google_user(session: Session, user_data: UserCreateGoogle) -> User:
        """Crear usuario desde Google OAuth"""
        # Verificar si ya existe por email o google_id
        existing_user = UserService.get_by_email(session, user_data.email)
        if existing_user:
            # Si existe y ya tiene google_id, retornar
            if existing_user.google_id:
                return existing_user
            # Si existe pero no tiene google_id, vincular cuenta
            existing_user.google_id = user_data.google_id
            existing_user.auth_provider = AuthProvider.GOOGLE
            existing_user.is_verified = True
            existing_user.profile_picture = user_data.profile_picture
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        
        # Verificar username único
        base_username = user_data.username
        username = base_username
        counter = 1
        while UserService.get_by_username(session, username):
            username = f"{base_username}{counter}"
            counter += 1
        
        # Crear nuevo usuario
        user = User(
            username=username,
            email=user_data.email,
            google_id=user_data.google_id,
            profile_picture=user_data.profile_picture,
            auth_provider=AuthProvider.GOOGLE,
            is_verified=True,  # Google ya verificó el email
            hashed_password=None  # No tiene password local
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def update_user(
        session: Session, 
        user_id: int, 
        user_data: UserUpdate
    ) -> User:
        """Actualizar datos del usuario"""
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validar email único si se está cambiando
        if user_data.email and user_data.email != user.email:
            if UserService.get_by_email(session, user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = user_data.email
            user.is_verified = False  # Requerir nueva verificación
            user.verification_token = generate_verification_token()
        
        # Validar username único si se está cambiando
        if user_data.username and user_data.username != user.username:
            if UserService.get_by_username(session, user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username
        
        # Actualizar otros campos
        if user_data.age is not None:
            user.age = user_data.age
        if user_data.gender is not None:
            user.gender = user_data.gender
        if user_data.profile_picture is not None:
            user.profile_picture = user_data.profile_picture
        
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def update_password(
        session: Session,
        user_id: int,
        password_data: UserUpdatePassword
    ) -> bool:
        """Cambiar contraseña del usuario"""
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verificar que tenga password (no usuarios de Google)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change password for Google accounts"
            )
        
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Validar nueva contraseña
        is_valid, error_msg = validate_password_strength(password_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Actualizar contraseña
        user.hashed_password = hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        return True
    
    @staticmethod
    def verify_email(session: Session, token: str) -> User:
        """Verificar email con token (legacy - usar activate_account)"""
        return UserService.activate_account(session, token)
    
    @staticmethod
    def activate_account(session: Session, token: str) -> User:
        """Activar cuenta con token de email"""
        statement = select(User).where(User.verification_token == token)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid activation token"
            )
        
        if user.is_email_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated"
            )
        
        user.is_verified = True
        user.is_email_activated = True
        user.verification_token = None
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def regenerate_activation_token(session: Session, user_id: int) -> User:
        """Regenerar token de activación"""
        user = UserService.get_by_id(session, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_email_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated"
            )
        
        user.verification_token = generate_verification_token()
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def request_password_reset(session: Session, email: str) -> User:
        """Solicitar reset de contraseña"""
        user = UserService.get_by_email(session, email)
        if not user:
            # Por seguridad, no revelar si el email existe
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="If the email exists, a reset link will be sent"
            )
        
        # Generar token de reset
        user.reset_password_token = generate_reset_password_token()
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def reset_password(session: Session, token: str, new_password: str) -> bool:
        """Resetear contraseña con token"""
        statement = select(User).where(User.reset_password_token == token)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Verificar que no haya expirado
        if user.reset_password_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Validar nueva contraseña
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Actualizar contraseña
        user.hashed_password = hash_password(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        return True
    
    @staticmethod
    def delete_user(session: Session, user_id: int) -> bool:
        """Eliminar usuario (soft delete)"""
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        return True
    
    @staticmethod
    def update_last_login(session: Session, user_id: int) -> None:
        """Actualizar fecha de último login"""
        user = UserService.get_by_id(session, user_id)
        if user:
            user.last_login = datetime.utcnow()
            session.add(user)
            session.commit()
    
    @staticmethod
    def request_email_change(session: Session, user_id: int, new_email: str) -> User:
        """
        Solicitar cambio de email.
        Desactiva la cuenta y envía email de verificación al nuevo correo.
        """
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validar que el nuevo email sea diferente al actual
        if new_email.lower() == user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New email must be different from current email"
            )
        
        # Validar que el nuevo email no esté en uso
        existing_user = UserService.get_by_email(session, new_email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another account"
            )
        
        # Desactivar cuenta temporalmente
        user.is_active = False
        user.pending_email = new_email
        user.email_change_token = generate_verification_token()
        user.email_change_expires = datetime.utcnow() + timedelta(hours=24)
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def confirm_email_change(session: Session, token: str) -> User:
        """
        Confirmar cambio de email con token.
        Actualiza el email y reactiva la cuenta.
        """
        from sqlmodel import select
        
        statement = select(User).where(User.email_change_token == token)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Verificar que no haya expirado
        if user.email_change_expires and user.email_change_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )
        
        # Verificar que haya un email pendiente
        if not user.pending_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email change request found"
            )
        
        # Guardar el email anterior para notificación
        old_email = user.email
        
        # Actualizar email
        user.email = user.pending_email
        user.pending_email = None
        user.email_change_token = None
        user.email_change_expires = None
        user.is_active = True  # Reactivar cuenta
        user.is_verified = True  # Mantener verificado
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Guardar el email anterior para enviar notificación después
        user._old_email = old_email
        
        return user
    
    @staticmethod
    def cancel_email_change(session: Session, user_id: int) -> User:
        """
        Cancelar cambio de email pendiente y reactivar cuenta.
        """
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.pending_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email change request found"
            )
        
        # Cancelar cambio y reactivar
        user.pending_email = None
        user.email_change_token = None
        user.email_change_expires = None
        user.is_active = True
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def delete_account_permanently(session: Session, user_id: int) -> bool:
        """
        Eliminar cuenta permanentemente con todos los datos relacionados.
        Este es un borrado físico (hard delete), no un soft delete.
        """
        from sqlmodel import select, delete
        from app.models import WishList, Friend, CalificationGame, CommentUser
        from app.models.device import TrustedDevice, OTPCode
        
        user = UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        try:
            # 1. Eliminar wishlist items
            session.exec(delete(WishList).where(WishList.user_id == user_id))
            
            # 2. Eliminar solicitudes de amistad (enviadas y recibidas)
            session.exec(delete(Friend).where(
                (Friend.requester_id == user_id) | (Friend.receiver_id == user_id)
            ))
            
            # 3. Eliminar calificaciones
            session.exec(delete(CalificationGame).where(CalificationGame.user_id == user_id))
            
            # 4. Eliminar comentarios
            session.exec(delete(CommentUser).where(CommentUser.user_id == user_id))
            
            # 5. Eliminar dispositivos de confianza
            session.exec(delete(TrustedDevice).where(TrustedDevice.user_id == user_id))
            
            # 6. Eliminar códigos OTP
            session.exec(delete(OTPCode).where(OTPCode.user_id == user_id))
            
            # 7. Finalmente, eliminar el usuario
            session.delete(user)
            
            # Commit todas las eliminaciones
            session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting account: {str(e)}"
            )


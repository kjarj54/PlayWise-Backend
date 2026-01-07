from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.models import TrustedDevice, OTPCode, User
from app.core import generate_otp_code, send_otp_email


class OTPService:
    """Servicio para operaciones de OTP y dispositivos de confianza"""
    
    # Configuración
    OTP_EXPIRY_MINUTES = 10
    MAX_OTP_ATTEMPTS = 5
    DEVICE_TRUST_DAYS = 30  # Días que un dispositivo permanece como confianza
    
    @staticmethod
    def create_otp(session: Session, user_id: int, purpose: str = "login") -> OTPCode:
        """
        Crear un nuevo código OTP para el usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            purpose: Propósito del OTP (login, etc.)
            
        Returns:
            OTPCode creado
        """
        # Invalidar OTPs anteriores del mismo usuario y propósito
        OTPService.invalidate_user_otps(session, user_id, purpose)
        
        # Crear nuevo OTP
        otp = OTPCode(
            user_id=user_id,
            code=generate_otp_code(),
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTPService.OTP_EXPIRY_MINUTES)
        )
        
        session.add(otp)
        session.commit()
        session.refresh(otp)
        
        return otp
    
    @staticmethod
    def invalidate_user_otps(session: Session, user_id: int, purpose: str = "login") -> None:
        """Invalidar todos los OTPs activos del usuario"""
        statement = select(OTPCode).where(
            OTPCode.user_id == user_id,
            OTPCode.purpose == purpose,
            OTPCode.is_used == False
        )
        otps = session.exec(statement).all()
        
        for otp in otps:
            otp.is_used = True
        
        session.commit()
    
    @staticmethod
    def verify_otp(session: Session, user_id: int, code: str, purpose: str = "login") -> bool:
        """
        Verificar código OTP
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            code: Código OTP a verificar
            purpose: Propósito del OTP
            
        Returns:
            True si el OTP es válido
            
        Raises:
            HTTPException si el OTP es inválido o expirado
        """
        statement = select(OTPCode).where(
            OTPCode.user_id == user_id,
            OTPCode.purpose == purpose,
            OTPCode.is_used == False
        ).order_by(OTPCode.created_at.desc())
        
        otp = session.exec(statement).first()
        
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid OTP found. Please request a new one."
            )
        
        # Verificar expiración
        if datetime.now(timezone.utc) > otp.expires_at:
            otp.is_used = True
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one."
            )
        
        # Verificar intentos
        if otp.attempts >= OTPService.MAX_OTP_ATTEMPTS:
            otp.is_used = True
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many attempts. Please request a new OTP."
            )
        
        # Verificar código
        if otp.code != code:
            otp.attempts += 1
            session.commit()
            remaining = OTPService.MAX_OTP_ATTEMPTS - otp.attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OTP code. {remaining} attempts remaining."
            )
        
        # Marcar como usado
        otp.is_used = True
        session.commit()
        
        return True
    
    @staticmethod
    async def send_login_otp(session: Session, user: User) -> OTPCode:
        """
        Crear y enviar OTP para login
        
        Args:
            session: Sesión de base de datos
            user: Usuario que intenta iniciar sesión
            
        Returns:
            OTPCode creado
        """
        otp = OTPService.create_otp(session, user.id, "login")
        
        # Enviar email
        await send_otp_email(
            email=user.email,
            username=user.username,
            otp_code=otp.code
        )
        
        return otp
    
    # ========================
    # TRUSTED DEVICES
    # ========================
    
    @staticmethod
    def is_device_trusted(session: Session, user_id: int, device_id: str) -> bool:
        """
        Verificar si un dispositivo es de confianza para el usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            device_id: ID único del dispositivo
            
        Returns:
            True si el dispositivo es de confianza
        """
        statement = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_id == device_id
        )
        device = session.exec(statement).first()
        
        if not device:
            return False
        
        # Verificar expiración si existe
        if device.expires_at and datetime.now(timezone.utc) > device.expires_at:
            # Eliminar dispositivo expirado
            session.delete(device)
            session.commit()
            return False
        
        # Actualizar último uso
        device.last_used_at = datetime.now(timezone.utc)
        session.commit()
        
        return True
    
    @staticmethod
    def add_trusted_device(
        session: Session,
        user_id: int,
        device_id: str,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None
    ) -> TrustedDevice:
        """
        Agregar un dispositivo de confianza
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            device_id: ID único del dispositivo
            device_name: Nombre descriptivo del dispositivo
            device_type: Tipo de dispositivo (android, ios, web)
            
        Returns:
            TrustedDevice creado o actualizado
        """
        # Verificar si ya existe
        statement = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_id == device_id
        )
        existing = session.exec(statement).first()
        
        if existing:
            # Actualizar
            existing.device_name = device_name or existing.device_name
            existing.device_type = device_type or existing.device_type
            existing.last_used_at = datetime.now(timezone.utc)
            existing.expires_at = datetime.now(timezone.utc) + timedelta(days=OTPService.DEVICE_TRUST_DAYS)
            session.commit()
            session.refresh(existing)
            return existing
        
        # Crear nuevo
        device = TrustedDevice(
            user_id=user_id,
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            expires_at=datetime.now(timezone.utc) + timedelta(days=OTPService.DEVICE_TRUST_DAYS)
        )
        
        session.add(device)
        session.commit()
        session.refresh(device)
        
        return device
    
    @staticmethod
    def remove_trusted_device(session: Session, user_id: int, device_id: str) -> bool:
        """
        Eliminar un dispositivo de confianza
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            device_id: ID del dispositivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        statement = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_id == device_id
        )
        device = session.exec(statement).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trusted device not found"
            )
        
        session.delete(device)
        session.commit()
        
        return True
    
    @staticmethod
    def get_user_trusted_devices(session: Session, user_id: int) -> List[TrustedDevice]:
        """
        Obtener todos los dispositivos de confianza del usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Lista de dispositivos de confianza
        """
        statement = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id
        ).order_by(TrustedDevice.last_used_at.desc())
        
        return list(session.exec(statement).all())
    
    @staticmethod
    def remove_all_trusted_devices(session: Session, user_id: int) -> int:
        """
        Eliminar todos los dispositivos de confianza del usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Número de dispositivos eliminados
        """
        statement = select(TrustedDevice).where(TrustedDevice.user_id == user_id)
        devices = session.exec(statement).all()
        
        count = len(devices)
        for device in devices:
            session.delete(device)
        
        session.commit()
        
        return count
    
    @staticmethod
    def cleanup_expired_otps(session: Session) -> int:
        """
        Limpiar OTPs expirados (para mantenimiento)
        
        Returns:
            Número de OTPs eliminados
        """
        statement = select(OTPCode).where(
            OTPCode.expires_at < datetime.now(timezone.utc)
        )
        expired = session.exec(statement).all()
        
        count = len(expired)
        for otp in expired:
            session.delete(otp)
        
        session.commit()
        
        return count

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class TrustedDevice(SQLModel, table=True):
    """Modelo para dispositivos de confianza del usuario"""
    __tablename__ = "trusted_devices"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    device_id: str = Field(max_length=255, index=True)  # UUID único del dispositivo
    device_name: Optional[str] = Field(default=None, max_length=255)  # Nombre descriptivo del dispositivo
    device_type: Optional[str] = Field(default=None, max_length=50)  # "android", "ios", "web"
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Expiración (opcional)
    expires_at: Optional[datetime] = Field(default=None)


class OTPCode(SQLModel, table=True):
    """Modelo para almacenar códigos OTP temporales"""
    __tablename__ = "otp_codes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    code: str = Field(max_length=6)  # Código OTP de 6 dígitos
    purpose: str = Field(max_length=50)  # "login", "password_reset", etc.
    
    # Estado
    is_used: bool = Field(default=False)
    attempts: int = Field(default=0)  # Intentos fallidos
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(index=True)  # Expiración del código


# =========================
# SCHEMAS (DTOs)
# =========================
class OTPVerifyRequest(SQLModel):
    """Schema para verificar código OTP"""
    email: str
    otp_code: str
    device_id: str  # ID único del dispositivo
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    remember_device: bool = False  # Si desea recordar el dispositivo


class OTPResponse(SQLModel):
    """Schema para respuesta de OTP"""
    message: str
    otp_required: bool = False
    

class LoginWithOTPResponse(SQLModel):
    """Schema para respuesta de login que puede requerir OTP"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    otp_required: bool = False
    message: Optional[str] = None


class TrustedDeviceRead(SQLModel):
    """Schema para leer dispositivos de confianza"""
    id: int
    device_id: str
    device_name: Optional[str]
    device_type: Optional[str]
    created_at: datetime
    last_used_at: datetime

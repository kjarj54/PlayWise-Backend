from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from app.core.security import decode_token, TokenData
from app.core.config import settings
from app.db import get_session
from app.models import User, UserRole


# =========================
# OAUTH2 SCHEME
# =========================
# Scheme para autenticación con bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Scheme alternativo para Bearer en header
security = HTTPBearer()

# Scheme opcional que no requiere token
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# =========================
# DEPENDENCIES
# =========================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT
    
    Args:
        token: JWT token from Authorization header
        session: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Verificar tipo de token
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer datos del usuario
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    statement = select(User).where(User.id == int(user_id))
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para verificar que el usuario está activo
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para verificar que el usuario está verificado
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return current_user


# =========================
# ROLE BASED DEPENDENCIES
# =========================
def require_role(required_role: UserRole):
    """
    Factory function para crear una dependency que verifica el rol del usuario
    
    Args:
        required_role: Role required to access the endpoint
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    
    return role_checker


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para verificar que el usuario es admin
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Admin user object
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    return current_user


async def get_moderator_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para verificar que el usuario es moderador o admin
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Moderator or admin user object
        
    Raises:
        HTTPException: If user is not moderator or admin
    """
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Moderator or admin privileges required."
        )
    return current_user


# =========================
# OPTIONAL AUTH
# =========================
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Dependency opcional para obtener el usuario si está autenticado
    Útil para endpoints que pueden funcionar con o sin autenticación
    No requiere el header Authorization (auto_error=False)
    
    Args:
        token: Optional JWT token from Authorization header
        session: Database session
        
    Returns:
        Current user object or None if not authenticated
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token, session)
    except HTTPException:
        return None

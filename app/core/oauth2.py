from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings


# =========================
# OAUTH2 CONFIGURATION
# =========================
oauth = OAuth()

# Configurar Google OAuth2
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


# =========================
# GOOGLE OAUTH2 FUNCTIONS
# =========================
async def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a Google OAuth token and get user info
    
    Args:
        token: Google OAuth token (ID token)
        
    Returns:
        User info dict or None if invalid
        
    Raises:
        HTTPException: If token verification fails
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    try:
        # Verificar el token con Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            token_info = response.json()
            
            # Verificar que el token es para nuestra aplicación
            if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not for this application"
                )
            
            return token_info
            
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying Google token"
        )


async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Google using access token
    
    Args:
        access_token: Google OAuth access token
        
    Returns:
        User info dict or None if request fails
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                return None
            
            return response.json()
            
    except httpx.HTTPError:
        return None


def extract_google_user_data(google_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract relevant user data from Google OAuth response
    
    Args:
        google_data: Raw data from Google OAuth
        
    Returns:
        Formatted user data dict
    """
    return {
        "email": google_data.get("email", ""),
        "google_id": google_data.get("sub") or google_data.get("id", ""),
        "username": google_data.get("name", "").replace(" ", "_").lower(),
        "profile_picture": google_data.get("picture", ""),
        "is_verified": google_data.get("email_verified", False)
    }


# =========================
# AUTHORIZATION URL
# =========================
def get_google_authorization_url(redirect_uri: str) -> str:
    """
    Generate Google OAuth authorization URL
    
    Args:
        redirect_uri: Where Google should redirect after authorization
        
    Returns:
        Authorization URL
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"


async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access token
    
    Args:
        code: Authorization code from Google
        redirect_uri: Redirect URI used in authorization
        
    Returns:
        Token response dict or None if exchange fails
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                return None
            
            return response.json()
            
    except httpx.HTTPError:
        return None

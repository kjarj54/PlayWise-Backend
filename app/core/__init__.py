"""
Core module exports
"""

from .config import settings, Settings
from .security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    generate_reset_password_token,
    generate_otp_code,
    generate_device_token,
    Token,
    TokenData,
    pwd_context
)
from .auth import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_admin_user,
    get_moderator_user,
    get_current_user_optional,
    require_role,
    oauth2_scheme
)
from .oauth2 import (
    verify_google_token,
    get_google_user_info,
    extract_google_user_data,
    get_google_authorization_url,
    exchange_code_for_token,
    oauth
)
from .email import (
    send_email,
    send_verification_email,
    send_password_reset_email,
    send_welcome_email,
    send_otp_email,
    send_activation_email
)


__all__ = [
    # Config
    "settings",
    "Settings",
    
    # Security
    "hash_password",
    "verify_password",
    "validate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "generate_verification_token",
    "generate_reset_password_token",
    "generate_otp_code",
    "generate_device_token",
    "Token",
    "TokenData",
    "pwd_context",
    
    # Auth Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_admin_user",
    "get_moderator_user",
    "get_current_user_optional",
    "require_role",
    "oauth2_scheme",
    
    # OAuth2
    "verify_google_token",
    "get_google_user_info",
    "extract_google_user_data",
    "get_google_authorization_url",
    "exchange_code_for_token",
    "oauth",
    
    # Email
    "send_email",
    "send_verification_email",
    "send_password_reset_email",
    "send_welcome_email",
    "send_otp_email",
    "send_activation_email",
]

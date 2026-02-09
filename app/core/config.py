from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # Application
    PROJECT_NAME: str = "PlayWise API"
    APP_NAME: str = "PlayWise API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Security & JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False
    

    BACKEND_URL: Optional[str] = None  # URL del backend para enlaces en correos electrónicos

    # OAuth2 - Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # Email (para verificación y reset password)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None
    
    # CORS - Configurado según ambiente
    # En producción, especificar solo los dominios permitidos
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # Desarrollo frontend web
        "http://localhost:8081",  # Expo local
        "https://playwise.com",   # Producción web (cambiar según tu dominio)
        # Agregar más dominios según sea necesario
    ]
    
    # External Game APIs
    RAWG_API_KEY: Optional[str] = None  # https://rawg.io/apidocs
    CHEAPSHARK_API_URL: str = "https://www.cheapshark.com/api/1.0"  # No API key needed
    
    # AI / Recommendations
    GROQ_API_KEY: Optional[str] = None  # Groq API for AI recommendations (FREE)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Instancia global de settings
settings = Settings()

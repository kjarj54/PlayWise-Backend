from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app.db import init_db
from app.core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar la base de datos al arrancar la app"""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for PlayWise - Game tracking and social platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar rutas
from app.api.routes import (
    auth_router,
    user_router,
    game_router,
    wishlist_router,
    wishlist_legacy_router,
    calification_router,
    friend_router,
    web_pages_router
)

# Incluir routers con prefijo /api
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(game_router, prefix="/api")
app.include_router(wishlist_router, prefix="/api")
app.include_router(wishlist_legacy_router, prefix="/api")
app.include_router(calification_router, prefix="/api")
app.include_router(friend_router, prefix="/api")

# Incluir rutas web sin prefijo (para páginas HTML)
app.include_router(web_pages_router)


@app.get("/")
def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "Welcome to PlayWise API 🎮",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "games": "/api/games",
            "wishlist": "/api/wishlist",
            "califications": "/api/califications",
            "friends": "/api/friends"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }
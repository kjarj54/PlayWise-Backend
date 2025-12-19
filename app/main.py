from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar la base de datos al arrancar la app"""
    init_db()
    yield


app = FastAPI(
    title="PLAYWISE API",
    description="Una API de PLAYWISE",
    version="0.1.0",
    lifespan=lifespan
)

# Importar rutas
from app.api.routes import hello, users

# Incluir routers
app.include_router(hello.router)
app.include_router(users.router)

@app.get("/")
def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "Bienvenido a PLAYWISE API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
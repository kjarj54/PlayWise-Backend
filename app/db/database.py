from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os

# Obtener la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Configuración del engine
engine = create_engine(
    DATABASE_URL, 
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=300,    # Reciclar conexiones cada 5 minutos
)


def init_db():
    """Crear todas las tablas en la base de datos"""
    # Importar todos los modelos para que SQLModel los registre
    from app.models import (
        User, Game, WishList, CalificationGame, 
        CommentUser, CommentLike, Store, Friend
    )
    SQLModel.metadata.create_all(engine)
 

def get_session() -> Generator[Session, None, None]:
    """Dependency para obtener una sesión de base de datos"""
    with Session(engine) as session:
        yield session


# Alias para compatibilidad
def get_db() -> Generator[Session, None, None]:
    """Alias de get_session para compatibilidad"""
    return get_session()

from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os

# Obtener la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Crear el engine de conexión
# Para CockroachDB se recomienda usar el driver psycopg2
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Crear todas las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency para obtener una sesión de base de datos"""
    with Session(engine) as session:
        yield session

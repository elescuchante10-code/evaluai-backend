"""
Configuración de base de datos con SQLAlchemy
Soporta SQLite (local) y PostgreSQL (Railway)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Determinar URL de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/evaluai.db")

# Configurar engine según tipo de BD
if DATABASE_URL.startswith("sqlite"):
    # SQLite - para desarrollo local
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL - para Railway
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verificar conexiones antes de usar
        pool_size=5,
        max_overflow=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas"""
    Base.metadata.create_all(bind=engine)

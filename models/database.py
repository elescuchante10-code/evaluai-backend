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
# Railway provee DATABASE_URL con PostgreSQL
# Si no existe, usamos SQLite en /tmp para Railway o ./database para local
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Detectar si estamos en Railway (tiene variable RAILWAY_ENVIRONMENT)
    if os.getenv("RAILWAY_ENVIRONMENT"):
        # Usar /tmp en Railway (persiste durante la ejecución)
        DATABASE_URL = "sqlite:////tmp/evaluai.db"
        print("🚂 Railway detectado - usando SQLite en /tmp")
    else:
        # Local - usar carpeta database
        DATABASE_URL = "sqlite:///./database/evaluai.db"
        print("💻 Local detectado - usando SQLite en ./database")

# Crear directorio para SQLite si no existe (solo para rutas relativas locales)
if DATABASE_URL.startswith("sqlite") and DATABASE_URL.startswith("sqlite:///./"):
    db_path = DATABASE_URL.replace("sqlite:///./", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Creado directorio: {db_dir}")

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

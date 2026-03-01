"""
EvaluAI Profesor - Backend API
FastAPI + AgentSquad + DeepSeek
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos y crear tablas
from models.database import init_db
from api.evaluation import router as evaluation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre"""
    # Startup
    print("🚀 Iniciando EvaluAI Profesor...")
    init_db()
    print("✅ Base de datos inicializada")
    yield
    # Shutdown
    print("👋 Cerrando aplicación...")


# Crear app FastAPI
app = FastAPI(
    title="EvaluAI Profesor API",
    description="API de evaluación académica inteligente para profesores",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Permitir frontend local y Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Endpoint de salud para Railway"""
    return {
        "status": "ok",
        "service": "evaluai-backend",
        "version": "1.0.0"
    }


# Incluir routers
app.include_router(evaluation_router)


# Endpoint raíz
@app.get("/")
async def root():
    return {
        "message": "EvaluAI Profesor API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )

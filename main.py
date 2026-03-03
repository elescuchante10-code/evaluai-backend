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
from api.auth import router as auth_router
from api.documents import router as documents_router
from api.agent_chat import router as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre"""
    # Startup
    print("🚀 Iniciando EvaluAI Profesor...")
    port = os.getenv("PORT", "8000")
    print(f"📡 Puerto configurado: {port}")
    
    try:
        init_db()
        print("✅ Base de datos inicializada")
    except Exception as e:
        # Loguear error exacto para ver en pestaña Logs
        print(f"❌ ERROR CRÍTICO DB: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
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

# Log de inicio para debug
print(f"🔧 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'No set')}")
print(f"🔧 PORT: {os.getenv('PORT', 'No set')}")

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


# Health check - CRÍTICO para Railway
@app.get("/health")
async def health_check():
    """Endpoint de salud para Railway"""
    return {
        "status": "ok",
        "service": "evaluai-backend",
        "version": "1.0.0"
    }


# Endpoint raíz - también útil para verificar que corre
@app.get("/")
async def root():
    return {
        "message": "EvaluAI Profesor API",
        "docs": "/docs",
        "health": "/health"
    }


# Incluir routers DESPUÉS de definir healthcheck
app.include_router(auth_router)
app.include_router(evaluation_router)
app.include_router(documents_router)
app.include_router(agent_router)

print("✅ Routers cargados correctamente")

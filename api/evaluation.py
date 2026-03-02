"""
API Endpoints para evaluación
"""
import uuid
import json
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from models.database import get_db
from models.user import User
from models.evaluation import Evaluation
from services.evaluation_service import EvaluationService
from api.auth import get_current_user

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


@router.post("/subir")
async def subir_documento(
    archivo: UploadFile = File(...),
    asignatura: str = Form(...),
    rubrica_json: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),  # Opcional, para compatibilidad
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Paso 1: Subir documento y obtener estimación
    Requiere autenticación (token JWT en header Authorization)
    """
    try:
        # Validar formato
        extension = archivo.filename.split('.')[-1].lower()
        if extension not in ['pdf', 'docx', 'txt', 'doc']:
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado. Use PDF, DOCX o TXT"
            )
        
        # Leer archivo
        contenido = await archivo.read()
        
        # Crear servicio y procesar
        service = EvaluationService(db)
        resultado = await service.subir_y_estimar(
            filename=archivo.filename,
            file_bytes=contenido,
            asignatura=asignatura,
            rubrica_json=rubrica_json,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "estimacion": resultado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluar")
async def evaluar_documento(
    estimacion_id: str = Form(...),
    confirmar: bool = Form(True),
    user_id: str = Form(...),  # En producción vendría del JWT
    db: Session = Depends(get_db)
):
    """
    Paso 2: Confirmar y ejecutar evaluación
    """
    try:
        # Verificar usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        service = EvaluationService(db)
        resultado = await service.ejecutar_evaluacion(
            estimacion_id=estimacion_id,
            user=user,
            confirmar=confirmar
        )
        
        return {
            "success": True,
            "evaluacion": resultado
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluacion_id}")
async def obtener_evaluacion(
    evaluacion_id: str,
    db: Session = Depends(get_db)
):
    """Obtiene una evaluación por ID"""
    evaluacion = db.query(Evaluation).filter(Evaluation.id == evaluacion_id).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    return {
        "success": True,
        "data": evaluacion.to_dict(),
        "detalle": evaluacion.resultados_json
    }


@router.get("/{evaluacion_id}/reporte")
async def descargar_reporte(
    evaluacion_id: str,
    formato: str = "json",  # "json", "word", "txt"
    db: Session = Depends(get_db)
):
    """Descarga el reporte de evaluación"""
    evaluacion = db.query(Evaluation).filter(Evaluation.id == evaluacion_id).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    if formato == "json":
        return evaluacion.resultados_json
    
    elif formato == "word":
        if not evaluacion.report_path or not os.path.exists(evaluacion.report_path):
            raise HTTPException(status_code=404, detail="Reporte Word no generado")
        
        return FileResponse(
            evaluacion.report_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"evaluacion_{evaluacion_id}.docx"
        )
    
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado")


@router.get("/asignaturas/lista")
async def listar_asignaturas():
    """Lista las asignaturas soportadas"""
    return {
        "asignaturas": [
            {"id": "matematicas", "nombre": "Matemáticas", "icono": "📐"},
            {"id": "lenguaje", "nombre": "Lengua Castellana", "icono": "📚"},
            {"id": "sociales", "nombre": "Ciencias Sociales", "icono": "🌍"},
            {"id": "ingles", "nombre": "Inglés", "icono": "🗣️"},
            {"id": "ciencias", "nombre": "Ciencias Naturales", "icono": "🔬"},
            {"id": "generico", "nombre": "Otra (segmentación básica)", "icono": "📝"}
        ]
    }


# Endpoint compatible con el formato del frontend
@router.post("/procesar")
async def procesar_evaluacion(
    documento_id: str = Form(...),
    asignatura: str = Form(...),
    rubrica: Optional[str] = Form(None),  # JSON string
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Procesa un documento con IA (formato compatible con frontend)
    
    Este endpoint es similar a /evaluar pero con el formato que espera el dashboard.
    """
    try:
        service = EvaluationService(db)
        
        # Ejecutar evaluación
        resultado = await service.ejecutar_evaluacion(
            estimacion_id=documento_id,
            user=current_user,
            confirmar=True
        )
        
        # Formatear respuesta según lo esperado por el frontend
        return {
            "success": True,
            "id": resultado.get("id"),
            "estado": "completado",
            "calificacion_global": resultado.get("calificacion_global"),
            "segmentos": resultado.get("segmentos", []),
            "retroalimentacion": resultado.get("retroalimentacion_general", ""),
            "evaluacion": resultado
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

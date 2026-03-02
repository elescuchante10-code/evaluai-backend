"""
API Endpoints para gestión de documentos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database import get_db
from models.evaluation import Evaluation
from api.auth import get_current_user, verify_token
from models.user import User

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.get("", response_model=dict)
async def listar_documentos(
    asignatura: Optional[str] = Query(None, description="Filtrar por asignatura"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista los documentos/evaluaciones del usuario actual
    """
    query = db.query(Evaluation).filter(Evaluation.user_id == current_user.id)
    
    # Filtrar por asignatura si se proporciona
    if asignatura:
        query = query.filter(Evaluation.asignatura == asignatura)
    
    # Ordenar por fecha de creación descendente
    query = query.order_by(desc(Evaluation.created_at))
    
    # Paginación
    total = query.count()
    evaluaciones = query.offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "documentos": [
            {
                "id": ev.id,
                "filename": ev.original_filename,
                "asignatura": ev.asignatura,
                "calificacion_global": ev.calificacion_global,
                "semaforo_global": ev.semaforo_global,
                "total_words": ev.total_words,
                "total_segments": ev.total_segments,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "cost_cop": ev.cost_cop
            }
            for ev in evaluaciones
        ]
    }


@router.get("/{documento_id}", response_model=dict)
async def obtener_documento(
    documento_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle completo de una evaluación/documento
    """
    evaluacion = db.query(Evaluation).filter(
        Evaluation.id == documento_id,
        Evaluation.user_id == current_user.id
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return {
        "success": True,
        "documento": {
            "id": evaluacion.id,
            "filename": evaluacion.original_filename,
            "asignatura": evaluacion.asignatura,
            "tipo_trabajo": evaluacion.tipo_trabajo,
            "calificacion_global": evaluacion.calificacion_global,
            "semaforo_global": evaluacion.semaforo_global,
            "total_words": evaluacion.total_words,
            "total_segments": evaluacion.total_segments,
            "cost_cop": evaluacion.cost_cop,
            "cost_usd": evaluacion.cost_usd,
            "tokens_input": evaluacion.tokens_input,
            "tokens_output": evaluacion.tokens_output,
            "created_at": evaluacion.created_at.isoformat() if evaluacion.created_at else None,
        },
        "resultados": evaluacion.resultados_json
    }


@router.delete("/{documento_id}", response_model=dict)
async def eliminar_documento(
    documento_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un documento y sus resultados
    """
    evaluacion = db.query(Evaluation).filter(
        Evaluation.id == documento_id,
        Evaluation.user_id == current_user.id
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Eliminar archivo de reporte si existe
    if evaluacion.report_path:
        import os
        try:
            if os.path.exists(evaluacion.report_path):
                os.remove(evaluacion.report_path)
        except Exception:
            pass  # Ignorar errores al eliminar archivo
    
    # Eliminar de la base de datos
    db.delete(evaluacion)
    db.commit()
    
    return {
        "success": True,
        "message": "Documento eliminado exitosamente",
        "documento_id": documento_id
    }


@router.get("/{documento_id}/resumen", response_model=dict)
async def obtener_resumen_documento(
    documento_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen rápido del documento (para el dashboard)
    """
    evaluacion = db.query(Evaluation).filter(
        Evaluation.id == documento_id,
        Evaluation.user_id == current_user.id
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Extraer resumen de resultados
    resultados = evaluacion.resultados_json or {}
    segmentos = resultados.get("segmentos", [])
    
    # Calcular distribución de semáforos
    semaforos = {"VERDE": 0, "AMARILLO": 0, "ROJO": 0}
    for seg in segmentos:
        sem = seg.get("semaforo", "GRIS")
        if sem in semaforos:
            semaforos[sem] += 1
    
    return {
        "success": True,
        "resumen": {
            "id": evaluacion.id,
            "filename": evaluacion.original_filename,
            "asignatura": evaluacion.asignatura,
            "calificacion_global": evaluacion.calificacion_global,
            "semaforo_global": evaluacion.semaforo_global,
            "total_segments": evaluacion.total_segments,
            "distribucion_semaforos": semaforos,
            "fortalezas": resultados.get("fortalezas", []),
            "areas_mejora": resultados.get("areas_mejora", [])
        }
    }

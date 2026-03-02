"""
API Endpoint para chat con el agente IA
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from api.auth import get_current_user
from models.user import User
from agents.kimi_agent import KimiAgent

router = APIRouter(prefix="/agente", tags=["Agente IA"])

# Instancia del agente
agent = KimiAgent()


class ChatMessage(BaseModel):
    mensaje: str
    contexto: Optional[Dict[str, Any]] = {}
    historial: Optional[List[Dict[str, str]]] = []  # Historial de conversación


class ChatResponse(BaseModel):
    respuesta: str
    accion: str  # "evaluar", "rubrica", "info", "general"
    data: Optional[Dict[str, Any]] = {}


@router.post("/chat", response_model=dict)
async def chat_con_agente(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje al agente IA y recibe una respuesta
    
    El agente puede:
    - Responder preguntas generales sobre la plataforma
    - Ayudar a configurar rúbricas
    - Interpretar resultados de evaluaciones
    - Sugerir mejoras a documentos
    """
    try:
        # Construir el prompt del sistema según el contexto
        system_prompt = _construir_system_prompt(message.contexto, current_user)
        
        # Procesar con el agente
        respuesta_agente = await agent.chat(
            mensaje=message.mensaje,
            system_prompt=system_prompt,
            historial=message.historial
        )
        
        # Detectar la acción/intención de la respuesta
        accion = _detectar_accion(message.mensaje, respuesta_agente)
        
        # Extraer datos estructurados si los hay
        data = _extraer_datos(respuesta_agente, accion)
        
        return {
            "success": True,
            "respuesta": respuesta_agente,
            "accion": accion,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")


def _construir_system_prompt(contexto: Dict, user: User) -> str:
    """Construye el prompt del sistema según el contexto"""
    
    base_prompt = f"""Eres EvaluAI Assistant, un agente especializado en ayudar a profesores con evaluación académica.

Información del usuario:
- Nombre: {user.full_name}
- Palabras disponibles: {user.words_available:,}
- Palabras usadas: {user.words_used:,}
- Plan: {user.plan_type}

Puedes ayudar con:
1. Configurar rúbricas de evaluación personalizadas
2. Interpretar resultados de evaluaciones
3. Sugerir mejoras a trabajos estudiantiles
4. Responder preguntas sobre el uso de la plataforma
5. Explicar conceptos pedagógicos y de evaluación

Responde de manera profesional, clara y útil para profesores."""

    # Agregar contexto adicional si existe
    if contexto.get("asignatura"):
        base_prompt += f"\n\nAsignatura actual: {contexto['asignatura']}"
    
    if contexto.get("documento_id"):
        base_prompt += f"\nDocumento en contexto: {contexto['documento_id']}"
    
    if contexto.get("evaluacion_id"):
        base_prompt += f"\nEvaluación en contexto: {contexto['evaluacion_id']}"
    
    return base_prompt


def _detectar_accion(mensaje: str, respuesta: str) -> str:
    """Detecta la intención/acción del mensaje"""
    
    mensaje_lower = mensaje.lower()
    respuesta_lower = respuesta.lower()
    
    # Detectar intención por palabras clave en el mensaje
    if any(word in mensaje_lower for word in ["rúbrica", "criterio", "peso", "calificar", "evaluar"]):
        return "rubrica"
    
    if any(word in mensaje_lower for word in ["evalúa", "revisar", "corregir", "califica este"]):
        return "evaluar"
    
    # Detectar por contenido de la respuesta
    if "rúbrica" in respuesta_lower and ("criterio" in respuesta_lower or "peso" in respuesta_lower):
        return "rubrica"
    
    if "evaluación" in respuesta_lower and any(word in respuesta_lower for word in ["calificación", "nota", "puntaje"]):
        return "evaluar"
    
    return "info"


def _extraer_datos(respuesta: str, accion: str) -> Dict:
    """Extrae datos estructurados de la respuesta si es posible"""
    
    import re
    
    data = {}
    
    if accion == "rubrica":
        # Intentar extraer criterios si están en formato lista
        criterios = []
        # Buscar patrones como "- Criterio (X%)" o "1. Criterio: X%"
        pattern = r'[-\d\.]+\s*[:\-]?\s*([^\(]+)\s*\(?(\d+)%\)?'
        matches = re.findall(pattern, respuesta)
        for match in matches:
            criterios.append({
                "nombre": match[0].strip(),
                "peso": int(match[1]) / 100
            })
        if criterios:
            data["criterios_sugeridos"] = criterios
    
    elif accion == "evaluar":
        # Intentar extraer calificación si está mencionada
        pattern = r'(\d+(?:\.\d+)?)\s*/?\s*10'
        match = re.search(pattern, respuesta)
        if match:
            data["calificacion_sugerida"] = float(match.group(1))
    
    return data


@router.post("/chat/stream")
async def chat_con_agente_stream(
    message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Chat con streaming de respuesta (para respuestas más largas)
    """
    # Por ahora, retornamos la misma respuesta
    # En el futuro, esto puede implementar Server-Sent Events
    return await chat_con_agente(message, current_user)


@router.post("/sugerir-rubrica", response_model=dict)
async def sugerir_rubrica(
    asignatura: str,
    tipo_trabajo: Optional[str] = None,
    descripcion: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Solicita al agente una sugerencia de rúbrica para una asignatura
    """
    try:
        prompt = f"""Sugiere una rúbrica de evaluación para:
- Asignatura: {asignatura}
- Tipo de trabajo: {tipo_trabajo or 'general'}
"""
        if descripcion:
            prompt += f"- Descripción: {descripcion}\n"
        
        prompt += """
Proporciona 4-6 criterios relevantes con sus pesos (que sumen 100%).
Responde en formato JSON con esta estructura:
{
  "criterios": [
    {"nombre": "...", "peso": 0.3, "descripcion": "..."}
  ],
  "explicacion": "..."
}"""

        respuesta = await agent.chat(
            mensaje=prompt,
            system_prompt="Eres un experto en diseño de rúbricas educativas."
        )
        
        # Intentar parsear JSON de la respuesta
        import json
        try:
            # Buscar JSON en la respuesta
            start = respuesta.find('{')
            end = respuesta.rfind('}') + 1
            if start >= 0 and end > start:
                rubrica_data = json.loads(respuesta[start:end])
            else:
                rubrica_data = {"raw_response": respuesta}
        except json.JSONDecodeError:
            rubrica_data = {"raw_response": respuesta}
        
        return {
            "success": True,
            "asignatura": asignatura,
            "tipo_trabajo": tipo_trabajo,
            "rubrica": rubrica_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando rúbrica: {str(e)}")

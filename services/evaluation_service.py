"""
Servicio de evaluación - Lógica de negocio
"""
import os
import json
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from agent_squad.orchestrator import AgentSquad
from agent_squad.storage import InMemoryChatStorage

from agents.kimi_agent import KimiAgent, KimiAgentOptions
from agents.parser_agent import DocumentParserAgent
from agents.segmenter_agent import SegmenterAgent

from models.user import User
from models.evaluation import Evaluation


class EvaluationService:
    """Orquesta todo el proceso de evaluación"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage_path = os.getenv("STORAGE_PATH", "./storage")
        
        # Inicializar orquestador AgentSquad (con storage en memoria)
        self.orchestrator = AgentSquad(storage=InMemoryChatStorage())
        
        # Agregar agentes
        self._setup_agents()
    
    def _setup_agents(self):
        """Configura los agentes del sistema"""
        
        # Parser
        parser = DocumentParserAgent(ParserOptions(
            name="DocumentParser",
            description="Extrae texto de archivos"
        ))
        self.orchestrator.add_agent(parser)
        
        # Segmenter
        segmenter = SegmenterAgent(SegmenterOptions(
            name="Segmenter",
            description="Divide documentos en segmentos"
        ))
        self.orchestrator.add_agent(segmenter)
        
        # Evaluador Kimi (matemáticas por defecto)
        math_evaluator = KimiAgent(KimiAgentOptions(
            name="MathEvaluator",
            description="Evalúa ejercicios de matemáticas",
            api_key=os.getenv("KIMI_API_KEY"),
            model=os.getenv("KIMI_MODEL", "kimi-k2-5"),
            temperature=0.1
        ))
        self.orchestrator.add_agent(math_evaluator)
    
    async def subir_y_estimar(self, filename: str, file_bytes: bytes, 
                             asignatura: str, rubrica_json: Optional[str] = None,
                             user_id: Optional[str] = None):
        """
        Paso 1: Procesa archivo y estima costo
        """
        # Guardar archivo temporal
        temp_id = str(uuid.uuid4())
        temp_path = os.path.join(self.storage_path, "documents", f"{temp_id}_{filename}")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        
        # Parsear documento
        parser = DocumentParserAgent(ParserOptions(name="Parser", description=""""""))
        parse_result = await parser.process_request(
            input_text="",
            user_id="temp",
            session_id=temp_id,
            chat_history=[],
            additional_params={
                "filename": filename,
                "file_bytes": file_bytes
            }
        )
        
        if parse_result.metadata.get("error"):
            raise ValueError(f"Error parseando: {parse_result.metadata.get('error_message')}")
        
        texto = parse_result.content[0]["text"]
        word_count = parse_result.metadata.get("word_count", 0)
        
        # Segmentar
        segmenter = SegmenterAgent(SegmenterOptions(name="Segmenter", description=""""""))
        segment_result = await segmenter.process_request(
            input_text=texto,
            user_id="temp",
            session_id=temp_id,
            chat_history=[],
            additional_params={"asignatura": asignatura}
        )
        
        segmentos_data = json.loads(segment_result.content[0]["text"])
        num_segmentos = len(segmentos_data)
        
        # Estimar costo DeepSeek
        # Input: texto + prompt (~500 tokens por segmento)
        tokens_input = int(word_count / 0.75) + (num_segmentos * 500)
        # Output: respuesta JSON (~300 tokens por segmento)
        tokens_output = num_segmentos * 300
        
        cost_input = (tokens_input / 1000) * float(os.getenv("COST_PER_1K_INPUT", 0.0005))
        cost_output = (tokens_output / 1000) * float(os.getenv("COST_PER_1K_OUTPUT", 0.002))
        costo_total_usd = cost_input + cost_output
        
        return {
            "temp_id": temp_id,
            "filename": filename,
            "word_count": word_count,
            "num_segmentos": num_segmentos,
            "asignatura": asignatura,
            "texto_preview": texto[:500] + "..." if len(texto) > 500 else texto,
            "segmentos_preview": segmentos_data[:3],  # Primeros 3 segmentos
            "estimacion_costo": {
                "usd": round(costo_total_usd, 6),
                "cop": round(costo_total_usd * 4100, 2),
                "tokens_input": tokens_input,
                "tokens_output": tokens_output
            },
            "rubrica": rubrica_json
        }
    
    async def ejecutar_evaluacion(self, estimacion_id: str, user: User, confirmar: bool = True):
        """
        Paso 2: Ejecuta la evaluación completa
        """
        if not confirmar:
            raise ValueError("Evaluación cancelada por el usuario")
        
        # TODO: Recuperar datos de la estimación (deberías guardarlos en Redis/DB temporal)
        # Por ahora, simulamos con datos de ejemplo
        
        # Verificar que tiene palabras disponibles
        # word_count = ... recuperar de la estimación
        # if not user.can_evaluate(word_count):
        #     raise ValueError("Límite de palabras excedido")
        
        # Ejecutar evaluación con los agentes
        # TODO: Implementar flujo completo
        
        # Crear evaluación en la base de datos
        evaluacion_id = str(uuid.uuid4())
        
        # Datos de ejemplo para el simulado (en producción vendrían de la evaluación real)
        evaluacion = Evaluation(
            id=evaluacion_id,
            user_id=user.id,
            filename=f"eval_{evaluacion_id}.json",
            original_filename=f"documento_{asignatura}.pdf",
            asignatura=asignatura,
            total_words=1500,
            total_segments=5,
            calificacion_global=8.5,
            semaforo_global="VERDE",
            resultados_json={
                "segmentos": [
                    {
                        "id": 1,
                        "tipo": "ejercicio",
                        "calificacion": 9.0,
                        "semaforo": "VERDE",
                        "retroalimentacion": "Excelente trabajo",
                        "criterios": [{"nombre": "Procedimiento", "puntuacion": 9}]
                    },
                    {
                        "id": 2,
                        "tipo": "problema",
                        "calificacion": 8.0,
                        "semaforo": "VERDE",
                        "retroalimentacion": "Buen razonamiento",
                        "criterios": [{"nombre": "Procedimiento", "puntuacion": 8}]
                    }
                ],
                "retroalimentacion_general": "El estudiante demuestra buen dominio del tema.",
                "fortalezas": ["Procedimiento claro", "Buena notación"],
                "areas_mejora": ["Revisar cálculos finales"]
            },
            cost_usd=0.05,
            cost_cop=205.0,
            tokens_input=2000,
            tokens_output=800
        )
        
        self.db.add(evaluacion)
        self.db.commit()
        
        return {
            "id": evaluacion_id,
            "message": "Evaluación completada",
            "user_words_remaining": user.words_available,
            "calificacion_global": evaluacion.calificacion_global,
            "semaforo_global": evaluacion.semaforo_global,
            "segmentos": evaluacion.resultados_json.get("segmentos", []),
            "retroalimentacion_general": evaluacion.resultados_json.get("retroalimentacion_general", "")
        }

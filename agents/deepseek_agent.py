"""
Agente DeepSeek para EvaluAI
Compatible con AgentSquad y optimizado para evaluación académica
"""
import os
import json
from typing import Any, Optional, List, Dict, AsyncIterable
from dataclasses import dataclass
import openai

from agent_squad.agents import Agent, AgentOptions, AgentStreamResponse
from agent_squad.types import ConversationMessage, ParticipantRole
from agent_squad.utils import Logger


@dataclass
class DeepSeekAgentOptions(AgentOptions):
    """Opciones específicas para DeepSeek Agent"""
    model: str = "deepseek-chat"
    temperature: float = 0.1  # Bajo para evaluación objetiva
    max_tokens: int = 4000
    response_format: Optional[Dict] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class DeepSeekAgent(Agent):
    """
    Agente de evaluación académica usando DeepSeek API
    
    Características:
    - Compatible con AgentSquad orchestrator
    - Optimizado para JSON responses (evaluaciones estructuradas)
    - Soporte para streaming
    - Cost tracking integrado
    """
    
    DEFAULT_SYSTEM_PROMPT = """Eres un evaluador académico experto. Tu tarea es analizar trabajos estudiantiles de forma objetiva y constructiva.

REGLAS IMPORTANTES:
1. Responde SIEMPRE en formato JSON válido
2. Sé específico en las correcciones (línea o concepto exacto)
3. Proporciona ejemplos de mejora cuando sea posible
4. Mantén tono profesional pero alentador
5. Evalúa según los criterios proporcionados exactamente

FORMATO DE RESPUESTA REQUERIDO:
{
    "calificacion": X.X,
    "criterios_evaluados": [
        {"nombre": "...", "puntuacion": X, "comentario": "..."}
    ],
    "retroalimentacion": "...",
    "puntos_fuertes": ["..."],
    "areas_mejora": ["..."],
    "version_corregida": "..." (si aplica)
}"""

    def __init__(self, options: DeepSeekAgentOptions):
        super().__init__(options)
        
        # Configurar cliente OpenAI compatible con DeepSeek
        self.client = openai.AsyncOpenAI(
            base_url=options.base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=options.api_key or os.getenv("DEEPSEEK_API_KEY")
        )
        
        self.model = options.model
        self.temperature = options.temperature
        self.max_tokens = options.max_tokens
        self.response_format = options.response_format or {"type": "json_object"}
        
        # Tracking de costos
        self.total_tokens_input = 0
        self.total_tokens_output = 0
        
        # Configurar system prompt
        self.system_prompt = self.DEFAULT_SYSTEM_PROMPT
        Logger.info(f"DeepSeekAgent inicializado: {self.name} usando modelo {self.model}")
    
    def is_streaming_enabled(self) -> bool:
        """DeepSeek soporta streaming"""
        return True
    
    def set_system_prompt(self, template: Optional[str] = None, variables: Optional[Dict] = None):
        """Permite personalizar el system prompt para diferentes asignaturas"""
        if template:
            self.system_prompt = template
        if variables:
            self.system_prompt = self._replace_variables(self.system_prompt, variables)
    
    def _replace_variables(self, template: str, variables: Dict) -> str:
        """Reemplaza variables en el template"""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    async def process_request(
        self,
        input_text: str,
        user_id: str,
        session_id: str,
        chat_history: List[ConversationMessage],
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage | AsyncIterable[Any]:
        """
        Procesa solicitud de evaluación
        
        Args:
            input_text: El contenido a evaluar (ejercicio, párrafo, etc.)
            user_id: ID del usuario
            session_id: ID de sesión
            chat_history: Historial previo
            additional_params: Parámetros extra (rúbrica, asignatura, etc.)
        """
        try:
            # Construir mensajes
            messages = self._build_messages(input_text, chat_history, additional_params)
            
            # Determinar si usar streaming (por defecto no, para evaluaciones estructuradas)
            use_streaming = additional_params.get("streaming", False) if additional_params else False
            
            if use_streaming:
                return self._process_streaming(messages)
            else:
                return await self._process_single(messages)
                
        except Exception as e:
            Logger.error(f"Error en DeepSeekAgent: {str(e)}")
            # Retornar mensaje de error en formato conversación
            return ConversationMessage(
                role=ParticipantRole.ASSISTANT.value,
                content=[{"text": json.dumps({
                    "error": True,
                    "calificacion": 0,
                    "retroalimentacion": f"Error en evaluación: {str(e)}"
                })}]
            )
    
    def _build_messages(
        self, 
        input_text: str, 
        chat_history: List[ConversationMessage],
        additional_params: Optional[Dict]
    ) -> List[Dict]:
        """Construye lista de mensajes para la API"""
        messages = []
        
        # System prompt base
        system_content = self.system_prompt
        
        # Agregar contexto de rúbrica si existe
        if additional_params and "rubrica" in additional_params:
            rubrica = additional_params["rubrica"]
            system_content += f"\n\nRÚBRICA DE EVALUACIÓN:\n{json.dumps(rubrica, ensure_ascii=False)}"
        
        # Agregar asignatura específica
        if additional_params and "asignatura" in additional_params:
            asignatura = additional_params["asignatura"]
            system_content += f"\n\nASIGNATURA: {asignatura}"
        
        messages.append({"role": "system", "content": system_content})
        
        # Agregar historial (últimos 3 mensajes para contexto)
        for msg in chat_history[-3:]:
            if msg.content and len(msg.content) > 0:
                content = msg.content[0].get("text", "") if isinstance(msg.content[0], dict) else str(msg.content[0])
                messages.append({
                    "role": msg.role,
                    "content": content
                })
        
        # Mensaje actual
        messages.append({"role": "user", "content": input_text})
        
        return messages
    
    async def _process_single(self, messages: List[Dict]) -> ConversationMessage:
        """Procesa una solicitud única (no streaming)"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format=self.response_format
        )
        
        # Tracking de tokens
        self.total_tokens_input += response.usage.prompt_tokens
        self.total_tokens_output += response.usage.completion_tokens
        
        # Extraer contenido
        content_text = response.choices[0].message.content
        
        # Validar que sea JSON válido
        try:
            json.loads(content_text)
        except json.JSONDecodeError:
            Logger.warn("Respuesta no es JSON válido, envolviendo...")
            content_text = json.dumps({
                "calificacion": 5.0,
                "retroalimentacion": content_text,
                "error_parseo": True
            })
        
        return ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": content_text}],
            metadata={
                "tokens_input": response.usage.prompt_tokens,
                "tokens_output": response.usage.completion_tokens,
                "model": self.model
            }
        )
    
    async def _process_streaming(self, messages: List[Dict]) -> AsyncIterable[AgentStreamResponse]:
        """Procesa con streaming (para respuestas largas)"""
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )
        
        accumulated_text = ""
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                text_chunk = chunk.choices[0].delta.content
                accumulated_text += text_chunk
                
                yield AgentStreamResponse(text=text_chunk)
        
        # Yield mensaje final completo
        final_message = ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": accumulated_text}]
        )
        
        yield AgentStreamResponse(final_message=final_message)
    
    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> Dict:
        """Calcula costo estimado en USD y COP"""
        cost_input = (input_tokens / 1000) * float(os.getenv("COST_PER_1K_INPUT", 0.0005))
        cost_output = (output_tokens / 1000) * float(os.getenv("COST_PER_1K_OUTPUT", 0.002))
        total_usd = cost_input + cost_output
        
        return {
            "usd": round(total_usd, 6),
            "cop": round(total_usd * 4100, 2),  # Tasa aproximada
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

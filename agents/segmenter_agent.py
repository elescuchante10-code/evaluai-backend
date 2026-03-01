"""
SegmenterAgent - Divide documentos por asignatura
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from agent_squad.agents import Agent, AgentOptions
from agent_squad.types import ConversationMessage, ParticipantRole
from agent_squad.utils import Logger


@dataclass
class Segmento:
    """Representa un segmento del documento"""
    numero: int
    tipo: str
    contenido: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SegmenterAgent(Agent):
    """
    Agente que divide documentos en segmentos evaluables
    según la asignatura (matemáticas, lenguaje, etc.)
    """
    
    # Patrones por asignatura
    PATRONES = {
        "matematicas": [
            (r'Ejercicio\s+(\d+)[\.:]?\s*(.+?)(?=Ejercicio\s+\d+|$)', 'ejercicio'),
            (r'Problema\s+(\d+)[\.:]?\s*(.+?)(?=Problema\s+\d+|$)', 'problema'),
            (r'Punto\s+(\d+)[\.:]?\s*(.+?)(?=Punto\s+\d+|$)', 'punto'),
            (r'(?:Solución|Desarrollo)[\.:]?\s*(.+?)(?=(?:Ejercicio|Problema)|$)', 'solucion'),
        ],
        "lenguaje": [
            (r'Introducción[\.:]?\s*(.+?)(?=Desarrollo|$)', 'introduccion'),
            (r'Desarrollo[\.:]?\s*(.+?)(?=Conclusión|$)', 'desarrollo'),
            (r'Conclusión[\.:]?\s*(.+?)(?=Refer|$|$)', 'conclusion'),
        ],
        "sociales": [
            (r'(?:Contexto|Antecedentes)[\.:]?\s*(.+?)(?=Causas|Desarrollo|$)', 'contexto'),
            (r'Causas[\.:]?\s*(.+?)(?=Consecuencias|Desarrollo|$)', 'causas'),
            (r'Desarrollo[\.:]?\s*(.+?)(?=Consecuencias|Conclusión|$)', 'desarrollo'),
            (r'Consecuencias[\.:]?\s*(.+?)(?=Conclusión|$)', 'consecuencias'),
            (r'Conclusión[\.:]?\s*(.+?)(?=$)', 'conclusion'),
        ],
        "generico": []  # Divide por párrafos
    }
    
    def __init__(self, options: AgentOptions):
        super().__init__(options)
        Logger.info("SegmenterAgent inicializado")
    
    async def process_request(
        self,
        input_text: str,
        user_id: str,
        session_id: str,
        chat_history: list,
        additional_params: Optional[dict] = None
    ) -> ConversationMessage:
        """
        Divide el texto en segmentos según la asignatura
        """
        try:
            asignatura = additional_params.get('asignatura', 'generico') if additional_params else 'generico'
            
            segmentos = self._segmentar(input_text, asignatura)
            
            # Convertir a formato JSON para la respuesta
            segmentos_data = [
                {
                    "numero": s.numero,
                    "tipo": s.tipo,
                    "contenido": s.contenido[:200] + "..." if len(s.contenido) > 200 else s.contenido,
                    "contenido_completo": s.contenido,
                    "longitud": len(s.contenido),
                    "palabras": len(s.contenido.split()),
                    "metadata": s.metadata
                }
                for s in segmentos
            ]
            
            import json
            return ConversationMessage(
                role=ParticipantRole.ASSISTANT.value,
                content=[{"text": json.dumps(segmentos_data, ensure_ascii=False)}],
                metadata={
                    "asignatura": asignatura,
                    "total_segmentos": len(segmentos),
                    "total_palabras": sum(s.metadata.get('palabras', 0) for s in segmentos),
                    "success": True
                }
            )
            
        except Exception as e:
            Logger.error(f"Error segmentando: {str(e)}")
            return ConversationMessage(
                role=ParticipantRole.ASSISTANT.value,
                content=[{"text": "[]"}],
                metadata={"error": True, "message": str(e)}
            )
    
    def _segmentar(self, texto: str, asignatura: str) -> List[Segmento]:
        """Lógica principal de segmentación"""
        
        patrones = self.PATRONES.get(asignatura, self.PATRONES["generico"])
        
        if not patrones:
            # Fallback: dividir por párrafos
            return self._segmentar_por_parrafos(texto)
        
        segmentos = []
        texto_restante = texto
        
        for patron, tipo in patrones:
            matches = list(re.finditer(patron, texto, re.DOTALL | re.IGNORECASE))
            
            for i, match in enumerate(matches, 1):
                # Extraer número si existe
                try:
                    numero = int(match.group(1)) if len(match.groups()) > 0 else len(segmentos) + 1
                    contenido = match.group(2) if len(match.groups()) > 1 else match.group(1)
                except:
                    numero = len(segmentos) + 1
                    contenido = match.group(0)
                
                segmentos.append(Segmento(
                    numero=numero,
                    tipo=tipo,
                    contenido=contenido.strip(),
                    metadata={
                        "palabras": len(contenido.split()),
                        "detectado_por": "patron"
                    }
                ))
        
        # Si no se detectaron patrones, fallback a párrafos
        if not segmentos:
            return self._segmentar_por_parrafos(texto)
        
        # Ordenar por número
        segmentos.sort(key=lambda x: x.numero)
        
        # Reenumerar si hay huecos
        for i, seg in enumerate(segmentos, 1):
            seg.numero = i
        
        return segmentos
    
    def _segmentar_por_parrafos(self, texto: str) -> List[Segmento]:
        """Divide por párrafos dobles"""
        parrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
        
        return [
            Segmento(
                numero=i,
                tipo="parrafo",
                contenido=p,
                metadata={"palabras": len(p.split())}
            )
            for i, p in enumerate(parrafos, 1)
        ]

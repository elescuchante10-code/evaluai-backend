"""
Modelo de Evaluación
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(String, index=True, nullable=False)
    
    # Información del documento
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    asignatura = Column(String, nullable=False)
    tipo_trabajo = Column(String, nullable=True)
    
    # Métricas
    total_words = Column(Integer, nullable=False)
    total_segments = Column(Integer, nullable=False)
    
    # Resultados
    calificacion_global = Column(Float, nullable=False)
    semaforo_global = Column(String, nullable=False)  # "VERDE", "AMARILLO", "ROJO"
    resultados_json = Column(JSON, nullable=False)  # Resultados detallados
    
    # Archivos generados
    report_path = Column(String, nullable=True)  # Path al archivo Word generado
    
    # Costo real
    cost_usd = Column(Float, nullable=True)
    cost_cop = Column(Float, nullable=True)
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convierte a diccionario para API"""
        return {
            "id": self.id,
            "filename": self.original_filename,
            "asignatura": self.asignatura,
            "calificacion_global": self.calificacion_global,
            "semaforo_global": self.semaforo_global,
            "total_segments": self.total_segments,
            "total_words": self.total_words,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "cost_cop": self.cost_cop
        }

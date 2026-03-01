"""
Modelo de Usuario (Profesor)
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    
    # Plan y límites
    plan_type = Column(String, default="profesor")  # "profesor" es el único
    word_limit = Column(Integer, default=120000)  # Límite mensual
    words_used = Column(Integer, default=0)  # Palabras usadas este mes
    extra_blocks = Column(Integer, default=0)  # Bloques extra comprados
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_paid = Column(Boolean, default=False)  # Suscripción al día
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def words_available(self):
        """Palabras disponibles este mes"""
        extra_words = self.extra_blocks * 50000
        return self.word_limit + extra_words - self.words_used
    
    @property
    def total_to_pay(self):
        """Total a pagar este mes"""
        return 30000 + (self.extra_blocks * 10000)
    
    def can_evaluate(self, word_count: int) -> bool:
        """Verifica si puede evaluar un documento"""
        return self.words_available >= word_count
    
    def consume_words(self, word_count: int):
        """Consume palabras del límite"""
        self.words_used += word_count

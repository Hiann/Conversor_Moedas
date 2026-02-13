"""Modelos ORM do banco de dados."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from .db import Base


class ConversaoDB(Base):
    """Modelo de conversão no banco de dados."""
    
    __tablename__ = "conversoes"
    
    id = Column(Integer, primary_key=True, index=True)
    valor_original = Column(Numeric(20, 8), nullable=False)
    valor_convertido = Column(Numeric(20, 8), nullable=False)
    moeda_origem = Column(String(3), nullable=False, index=True)
    moeda_destino = Column(String(3), nullable=False, index=True)
    taxa = Column(Numeric(20, 10), nullable=False)
    taxa_inversa = Column(Numeric(20, 10), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    notas = Column(Text, nullable=True)
    
    # Índices compostos para consultas comuns
    __table_args__ = (
        Index('idx_moedas', 'moeda_origem', 'moeda_destino'),
        Index('idx_timestamp', 'timestamp'),
    )
    
    def to_dict(self):
        """Converte para dicionário."""
        return {
            "id": self.id,
            "valor_original": float(self.valor_original),
            "valor_convertido": float(self.valor_convertido),
            "moeda_origem": self.moeda_origem,
            "moeda_destino": self.moeda_destino,
            "taxa": float(self.taxa),
            "taxa_inversa": float(self.taxa_inversa),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "notas": self.notas
        }


class ConversaoMultiplaDB(Base):
    """Modelo de conversão múltipla."""
    
    __tablename__ = "conversoes_multiplas"
    
    id = Column(Integer, primary_key=True, index=True)
    valor_original = Column(Numeric(20, 8), nullable=False)
    moeda_origem = Column(String(3), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    conversoes = relationship("ItemConversaoMultiplaDB", back_populates="conversao_multipla", cascade="all, delete-orphan")


class ItemConversaoMultiplaDB(Base):
    """Item de uma conversão múltipla."""
    
    __tablename__ = "itens_conversao_multipla"
    
    id = Column(Integer, primary_key=True)
    conversao_multipla_id = Column(Integer, ForeignKey("conversoes_multiplas.id"), nullable=False)
    moeda_destino = Column(String(3), nullable=False)
    valor_convertido = Column(Numeric(20, 8), nullable=False)
    taxa = Column(Numeric(20, 10), nullable=False)
    
    conversao_multipla = relationship("ConversaoMultiplaDB", back_populates="conversoes")


class ConfiguracaoDB(Base):
    """Configurações persistidas."""
    
    __tablename__ = "configuracoes"
    
    id = Column(Integer, primary_key=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=True)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)

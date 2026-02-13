"""Modelos de dados com Pydantic."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Moeda(BaseModel):
    """Representa uma moeda."""
    model_config = ConfigDict(frozen=True)
    
    codigo: str = Field(..., min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    nome: str
    simbolo: str = ""
    pais: Optional[str] = None
    
    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        return v.upper()


class TaxaCambio(BaseModel):
    """Representa uma taxa de câmbio."""
    model_config = ConfigDict(frozen=True)
    
    moeda_origem: str
    moeda_destino: str
    taxa: Decimal = Field(..., gt=0)
    taxa_inversa: Decimal = Field(..., gt=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    fonte: str = "unknown"


class Conversao(BaseModel):
    """Representa uma conversão realizada."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    valor_original: Decimal = Field(..., gt=0)
    valor_convertido: Decimal = Field(..., gt=0)
    moeda_origem: str
    moeda_destino: str
    taxa: Decimal
    taxa_inversa: Decimal
    timestamp: datetime = Field(default_factory=datetime.now)
    notas: Optional[str] = None
    
    def formatar(self, formato: str = "simples") -> str:
        """Formata a conversão para exibição."""
        if formato == "simples":
            return f"{self.valor_original} {self.moeda_origem} = {self.valor_convertido:.2f} {self.moeda_destino}"
        elif formato == "completo":
            data = self.timestamp.strftime("%d/%m/%Y %H:%M")
            return (
                f"💰 {self.valor_original} {self.moeda_origem} → "
                f"{self.valor_convertido:.2f} {self.moeda_destino}\n"
                f"   Taxa: 1 {self.moeda_origem} = {self.taxa} {self.moeda_destino}\n"
                f"   Data: {data}"
            )
        return str(self)


class ConversaoMultipla(BaseModel):
    """Representa uma conversão para múltiplas moedas."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    valor_original: Decimal
    moeda_origem: str
    conversoes: List[Conversao]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def total_moedas(self) -> int:
        return len(self.conversoes)


class Estatisticas(BaseModel):
    """Estatísticas de conversões."""
    model_config = ConfigDict(from_attributes=True)
    
    moeda_origem: str
    moeda_destino: str
    total_conversoes: int
    valor_total_origem: Decimal
    valor_total_destino: Decimal
    taxa_media: Decimal
    taxa_minima: Decimal
    taxa_maxima: Decimal
    primeira_conversao: Optional[datetime]
    ultima_conversao: Optional[datetime]
    variacao_percentual: Optional[Decimal] = None


class Configuracao(BaseModel):
    """Configurações do sistema."""
    model_config = ConfigDict(from_attributes=True)
    
    api_primary: str = "frankfurter"
    api_secondary: Optional[str] = "exchangerate"
    api_exchangerate_key: Optional[str] = None
    cache_enabled: bool = True
    cache_ttl: int = 3600  # segundos
    database_url: str = "sqlite:///data/conversor.db"
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    timeout: int = 10
    max_retries: int = 3


class HistoricoFiltro(BaseModel):
    """Filtro para consulta de histórico."""
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    moeda_origem: Optional[str] = None
    moeda_destino: Optional[str] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0


class ExportacaoConfig(BaseModel):
    """Configuração para exportação."""
    formato: str = Field(..., pattern=r'^(excel|pdf|csv|json)$')
    arquivo: str
    filtro: Optional[HistoricoFiltro] = None
    incluir_grafico: bool = False

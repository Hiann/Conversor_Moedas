"""Cliente para API ExchangeRate-API."""

import os
from decimal import Decimal
from typing import Dict, Optional

from .base import APIClient, APIError


class ExchangeRateClient(APIClient):
    """
    Cliente para ExchangeRate-API.
    
    Oferece plano gratuito com 1500 requisições/mês.
    Requer API key.
    
    Documentação: https://www.exchangerate-api.com/docs/overview
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("API_EXCHANGERATE_KEY", "demo")
    
    @property
    def nome(self) -> str:
        return "ExchangeRate-API"
    
    @property
    def url_base(self) -> str:
        return f"https://v6.exchangerate-api.com/v6/{self.api_key}"
    
    def _tratar_erro(self, data: dict) -> None:
        """Trata erros específicos da API."""
        if data.get("result") == "error":
            error_type = data.get("error-type", "unknown")
            
            mensagens = {
                "invalid-key": "API key inválida",
                "inactive-account": "Conta inativa",
                "quota-reached": "Limite de requisições atingido",
                "unsupported-code": "Moeda não suportada"
            }
            
            raise APIError(
                mensagens.get(error_type, f"Erro da API: {error_type}"),
                details={"error_type": error_type}
            )
    
    def obter_taxas(self, moeda_base: str = "USD") -> Dict[str, Decimal]:
        """Obtém todas as taxas para uma moeda base."""
        data = self._fazer_requisicao(f"/latest/{moeda_base}")
        self._tratar_erro(data)
        
        rates = data.get("conversion_rates", {})
        return {k: Decimal(str(v)) for k, v in rates.items()}
    
    def obter_taxa_par(self, de_moeda: str, para_moeda: str) -> Decimal:
        """Obtém taxa específica entre duas moedas."""
        data = self._fazer_requisicao(f"/pair/{de_moeda}/{para_moeda}")
        self._tratar_erro(data)
        
        taxa = data.get("conversion_rate")
        if taxa is None:
            raise APIError("Taxa não encontrada na resposta")
        
        return Decimal(str(taxa))
    
    def listar_moedas(self) -> Dict[str, str]:
        """Lista todas as moedas suportadas."""
        if self._moedas_cache is None:
            data = self._fazer_requisicao("/codes")
            self._tratar_erro(data)
            
            # Formato: [["USD", "United States Dollar"], ...]
            supported = data.get("supported_codes", [])
            self._moedas_cache = {code: name for code, name in supported}
        
        return self._moedas_cache
    
    def obter_quota(self) -> Dict:
        """Obtém informações de quota (apenas conta paga)."""
        data = self._fazer_requisicao("/quota")
        self._tratar_erro(data)
        
        return {
            "plan": data.get("plan_id"),
            "requests_remaining": data.get("requests_remaining"),
            "refresh_day": data.get("refresh_day_of_month")
        }

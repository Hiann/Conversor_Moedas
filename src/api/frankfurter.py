"""Cliente para API Frankfurter (gratuita, sem chave)."""

from decimal import Decimal
from typing import Dict

from .base import APIClient, APIError


class FrankfurterClient(APIClient):
    """
    Cliente para Frankfurter API.
    
    API gratuita e open-source mantida pelo Banco Central Europeu.
    Não requer API key.
    
    Documentação: https://www.frankfurter.app/docs/
    """
    
    @property
    def nome(self) -> str:
        return "Frankfurter"
    
    @property
    def url_base(self) -> str:
        return "https://api.frankfurter.app"
    
    def obter_taxas(self, moeda_base: str = "USD") -> Dict[str, Decimal]:
        """Obtém todas as taxas para uma moeda base."""
        data = self._fazer_requisicao(f"/latest?from={moeda_base}")
        
        rates = data.get("rates", {})
        return {k: Decimal(str(v)) for k, v in rates.items()}
    
    def obter_taxa_par(self, de_moeda: str, para_moeda: str) -> Decimal:
        """Obtém taxa específica entre duas moedas."""
        data = self._fazer_requisicao(
            f"/latest?from={de_moeda}&to={para_moeda}"
        )
        
        rates = data.get("rates", {})
        if para_moeda not in rates:
            raise APIError(f"Moeda {para_moeda} não encontrada")
        
        return Decimal(str(rates[para_moeda]))
    
    def listar_moedas(self) -> Dict[str, str]:
        """Lista todas as moedas suportadas."""
        if self._moedas_cache is None:
            data = self._fazer_requisicao("/currencies")
            self._moedas_cache = data
        return self._moedas_cache
    
    def obter_historico(
        self, 
        moeda_base: str, 
        moeda_destino: str,
        data_inicio: str,
        data_fim: str
    ) -> Dict[str, Decimal]:
        """
        Obtém histórico de taxas para um período.
        
        Args:
            moeda_base: Moeda de origem
            moeda_destino: Moeda de destino
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            
        Returns:
            Dicionário com data -> taxa
        """
        endpoint = f"/{data_inicio}..{data_fim}?from={moeda_base}&to={moeda_destino}"
        data = self._fazer_requisicao(endpoint)
        
        rates = data.get("rates", {})
        return {
            date: Decimal(str(values.get(moeda_destino, 0)))
            for date, values in rates.items()
        }

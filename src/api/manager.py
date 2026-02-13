"""Gerenciador de APIs com fallback automático."""

from typing import Dict, Optional, List, Type
from decimal import Decimal
import logging

from .base import APIClient, APIError
from .frankfurter import FrankfurterClient
from .exchangerate import ExchangeRateClient


class APIManager:
    """
    Gerenciador de APIs com fallback automático.
    
    Tenta APIs em ordem de prioridade até obter sucesso.
    """
    
    def __init__(
        self,
        primary: str = "frankfurter",
        secondary: Optional[str] = "exchangerate",
        api_key: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        self.logger = logging.getLogger("APIManager")
        self.clients: List[APIClient] = []
        self._moedas_cache: Optional[Dict[str, str]] = None
        
        # Configurações para cada cliente
        kwargs = {"timeout": timeout, "max_retries": max_retries}
        
        # Cria clientes na ordem de prioridade
        apis = [primary]
        if secondary:
            apis.append(secondary)
        
        for api_name in apis:
            try:
                if api_name == "frankfurter":
                    client = FrankfurterClient(**kwargs)
                elif api_name == "exchangerate":
                    client = ExchangeRateClient(api_key=api_key, **kwargs)
                else:
                    self.logger.warning(f"API desconhecida: {api_name}")
                    continue
                
                self.clients.append(client)
                self.logger.info(f"API configurada: {client.nome}")
                
            except Exception as e:
                self.logger.error(f"Erro ao configurar {api_name}: {e}")
    
    def _executar_com_fallback(self, method_name: str, *args, **kwargs):
        """Executa método com fallback entre APIs."""
        errors = []
        
        for client in self.clients:
            try:
                self.logger.debug(f"Tentando {client.nome}.{method_name}()")
                method = getattr(client, method_name)
                result = method(*args, **kwargs)
                self.logger.debug(f"Sucesso com {client.nome}")
                return result
                
            except APIError as e:
                self.logger.warning(f"Falha em {client.nome}: {e}")
                errors.append(f"{client.nome}: {e}")
                continue
        
        # Todas as APIs falharam
        raise APIError(
            f"Todas as APIs falharam: {'; '.join(errors)}",
            details={"errors": errors}
        )
    
    def obter_taxas(self, moeda_base: str = "USD") -> Dict[str, Decimal]:
        """Obtém taxas com fallback."""
        return self._executar_com_fallback("obter_taxas", moeda_base)
    
    def obter_taxa_par(self, de_moeda: str, para_moeda: str) -> Decimal:
        """Obtém taxa par com fallback."""
        return self._executar_com_fallback("obter_taxa_par", de_moeda, para_moeda)
    
    def listar_moedas(self) -> Dict[str, str]:
        """Lista moedas com fallback."""
        if self._moedas_cache is None:
            self._moedas_cache = self._executar_com_fallback("listar_moedas")
        return self._moedas_cache
    
    def verificar_moeda(self, moeda: str) -> bool:
        """Verifica se moeda é suportada."""
        try:
            moedas = self.listar_moedas()
            return moeda.upper() in moedas
        except APIError:
            return False
    
    def get_status(self) -> Dict[str, str]:
        """Retorna status de cada API."""
        status = {}
        
        for client in self.clients:
            try:
                # Tenta uma operação simples
                client.listar_moedas()
                status[client.nome] = "online"
            except APIError:
                status[client.nome] = "offline"
        
        return status
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for client in self.clients:
            client.__exit__(exc_type, exc_val, exc_tb)

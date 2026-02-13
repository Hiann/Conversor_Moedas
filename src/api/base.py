"""Classe base para clientes de API."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from decimal import Decimal
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.models import Moeda, TaxaCambio


class APIError(Exception):
    """Exceção para erros de API."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class APIClient(ABC):
    """Classe base abstrata para clientes de API."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session(max_retries)
        self._moedas_cache: Optional[Dict[str, str]] = None
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """Cria sessão HTTP com retry automático."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'ConversorMoedasPro/2.0',
            'Accept': 'application/json'
        })
        
        return session
    
    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome da API."""
        pass
    
    @property
    @abstractmethod
    def url_base(self) -> str:
        """URL base da API."""
        pass
    
    @abstractmethod
    def obter_taxas(self, moeda_base: str = "USD") -> Dict[str, Decimal]:
        """Obtém todas as taxas para uma moeda base."""
        pass
    
    @abstractmethod
    def obter_taxa_par(self, de_moeda: str, para_moeda: str) -> Decimal:
        """Obtém taxa específica entre duas moedas."""
        pass
    
    @abstractmethod
    def listar_moedas(self) -> Dict[str, str]:
        """Lista todas as moedas suportadas."""
        pass
    
    def verificar_moeda(self, moeda: str) -> bool:
        """Verifica se uma moeda é suportada."""
        try:
            moedas = self.listar_moedas()
            return moeda.upper() in moedas
        except APIError:
            return False
    
    def _fazer_requisicao(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Faz requisição HTTP com tratamento de erros."""
        url = f"{self.url_base}{endpoint}"
        
        try:
            self.logger.debug(f"Requisição: {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise APIError(f"Timeout na conexão com {self.nome}", details={"url": url})
        except requests.exceptions.ConnectionError:
            raise APIError(f"Erro de conexão com {self.nome}", details={"url": url})
        except requests.exceptions.HTTPError as e:
            raise APIError(
                f"Erro HTTP {e.response.status_code}",
                status_code=e.response.status_code,
                details={"url": url, "response": e.response.text}
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Erro na requisição: {str(e)}", details={"url": url})
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

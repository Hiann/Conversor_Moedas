"""Classe principal do conversor de moedas."""

import logging
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from src.core.models import (
    Conversao, ConversaoMultipla, Moeda, Estatisticas,
    HistoricoFiltro, Configuracao
)
from src.core.cache import CacheManager
from src.api.manager import APIManager, APIError
from src.database.db import get_db
from src.database.repository import ConversaoRepository


class ConversorMoedas:
    """
    Conversor de moedas principal.
    
    Orquestra APIs, cache, banco de dados e fornece
    interface unificada para conversões.
    """
    
    MOEDAS_POPULARES = {
        'USD': 'Dólar Americano',
        'EUR': 'Euro',
        'BRL': 'Real Brasileiro',
        'GBP': 'Libra Esterlina',
        'JPY': 'Iene Japonês',
        'CHF': 'Franco Suíço',
        'CAD': 'Dólar Canadense',
        'AUD': 'Dólar Australiano',
        'CNY': 'Yuan Chinês',
        'ARS': 'Peso Argentino'
    }
    
    def __init__(self, config: Optional[Configuracao] = None):
        """Inicializa o conversor."""
        self.config = config or Configuracao()
        
        # Logging
        self.logger = self._setup_logging()
        
        # Cache
        self.cache = CacheManager(
            ttl_seconds=self.config.cache_ttl,
            cache_dir="cache"
        )
        
        # API Manager com fallback
        self.api = APIManager(
            primary=self.config.api_primary,
            secondary=self.config.api_secondary,
            api_key=self.config.api_exchangerate_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        # Banco de dados
        self.db = get_db()
        self.db.criar_tabelas()
        
        # Moedas em cache
        self._moedas_disponiveis: Optional[Dict[str, str]] = None
        
        self.logger.info("Conversor inicializado com sucesso")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging."""
        Path("logs").mkdir(exist_ok=True)
        
        logger = logging.getLogger("ConversorMoedas")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if logger.handlers:
            return logger
        
        # Handler de arquivo
        file_handler = logging.FileHandler(
            self.config.log_file, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def converter(
        self, 
        valor: float, 
        de_moeda: str, 
        para_moeda: str,
        salvar: bool = True
    ) -> Conversao:
        """
        Converte valor entre duas moedas.
        
        Args:
            valor: Valor a converter (> 0)
            de_moeda: Moeda de origem (ex: USD)
            para_moeda: Moeda de destino (ex: BRL)
            salvar: Se deve salvar no histórico
            
        Returns:
            Objeto Conversao com resultado
        """
        # Validações
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        de_moeda = de_moeda.upper().strip()
        para_moeda = para_moeda.upper().strip()
        
        if de_moeda == para_moeda:
            raise ValueError("Moedas de origem e destino devem ser diferentes")
        
        self.logger.info(f"Convertendo {valor} {de_moeda} → {para_moeda}")
        
        try:
            # Tenta obter do cache primeiro
            cache_key = f"taxa:{de_moeda}:{para_moeda}"
            taxa = self.cache.get(cache_key)
            
            if taxa is None:
                taxa = self.api.obter_taxa_par(de_moeda, para_moeda)
                self.cache.set(cache_key, float(taxa))
            else:
                taxa = Decimal(str(taxa))
                self.logger.debug("Taxa obtida do cache")
            
            # Cálculo preciso
            valor_decimal = Decimal(str(valor))
            resultado = valor_decimal * taxa
            resultado = resultado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Cria objeto de conversão
            conversao = Conversao(
                valor_original=valor_decimal,
                valor_convertido=resultado,
                moeda_origem=de_moeda,
                moeda_destino=para_moeda,
                taxa=taxa,
                taxa_inversa=Decimal(str(1)) / taxa if taxa != 0 else Decimal('0')
            )
            
            # Salva no banco
            if salvar:
                with self.db.session_scope() as session:
                    repo = ConversaoRepository(session)
                    repo.salvar(conversao)
                self.logger.info(f"Conversão salva: {conversao.id}")
            
            return conversao
            
        except APIError as e:
            self.logger.error(f"Erro da API: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            raise
    
    def converter_multiplo(
        self, 
        valor: float, 
        de_moeda: str, 
        para_moedas: List[str]
    ) -> ConversaoMultipla:
        """
        Converte para múltiplas moedas.
        
        Args:
            valor: Valor a converter
            de_moeda: Moeda de origem
            para_moedas: Lista de moedas de destino
            
        Returns:
            Objeto ConversaoMultipla
        """
        de_moeda = de_moeda.upper().strip()
        para_moedas = [m.upper().strip() for m in para_moedas]
        
        self.logger.info(f"Conversão múltipla: {valor} {de_moeda} → {len(para_moedas)} moedas")
        
        conversoes = []
        for moeda in para_moedas:
            if moeda == de_moeda:
                continue
            try:
                conv = self.converter(valor, de_moeda, moeda, salvar=False)
                conversoes.append(conv)
            except Exception as e:
                self.logger.warning(f"Erro ao converter para {moeda}: {e}")
        
        multipla = ConversaoMultipla(
            valor_original=Decimal(str(valor)),
            moeda_origem=de_moeda,
            conversoes=conversoes
        )
        
        # Salva no banco
        with self.db.session_scope() as session:
            repo = ConversaoRepository(session)
            repo.salvar_multipla(multipla)
        
        return multipla
    
    def listar_moedas(self, apenas_populares: bool = False) -> Dict[str, str]:
        """Lista moedas disponíveis."""
        if apenas_populares:
            return self.MOEDAS_POPULARES
        
        if self._moedas_disponiveis is None:
            try:
                self._moedas_disponiveis = self.api.listar_moedas()
            except APIError as e:
                self.logger.warning(f"Erro ao listar moedas: {e}")
                return self.MOEDAS_POPULARES
        
        return self._moedas_disponiveis
    
    def buscar_moeda(self, termo: str) -> Dict[str, str]:
        """Busca moeda por termo."""
        termo = termo.upper()
        moedas = self.listar_moedas()
        
        return {
            codigo: nome 
            for codigo, nome in moedas.items()
            if termo in codigo or termo in nome.upper()
        }
    
    def obter_historico(
        self, 
        filtro: Optional[HistoricoFiltro] = None
    ) -> Tuple[List[Conversao], int]:
        """Obtém histórico de conversões."""
        filtro = filtro or HistoricoFiltro()
        
        with self.db.session_scope() as session:
            repo = ConversaoRepository(session)
            return repo.listar(filtro)
    
    def obter_estatisticas(
        self, 
        moeda_origem: str, 
        moeda_destino: str,
        dias: int = 30
    ) -> Optional[Estatisticas]:
        """Obtém estatísticas de conversões."""
        with self.db.session_scope() as session:
            repo = ConversaoRepository(session)
            return repo.obter_estatisticas(moeda_origem, moeda_destino, dias)
    
    def comparar_moedas(
        self, 
        moedas: List[str], 
        valor_base: float = 1,
        moeda_referencia: str = 'USD'
    ) -> Dict[str, Decimal]:
        """Compara múltiplas moedas."""
        resultado = {}
        
        for moeda in moedas:
            try:
                conv = self.converter(valor_base, moeda_referencia, moeda, salvar=False)
                resultado[moeda] = conv.valor_convertido
            except Exception as e:
                self.logger.warning(f"Erro na comparação de {moeda}: {e}")
                resultado[moeda] = None
        
        return resultado
    
    def obter_info_moeda(self, codigo: str) -> Optional[Dict]:
        """Obtém informações de uma moeda."""
        codigo = codigo.upper()
        moedas = self.listar_moedas()
        
        if codigo not in moedas:
            return None
        
        simbolos = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'BRL': 'R$', 'CAD': 'C$', 'AUD': 'A$', 'CHF': 'Fr',
            'CNY': '¥', 'INR': '₹', 'RUB': '₽', 'KRW': '₩'
        }
        
        return {
            'codigo': codigo,
            'nome': moedas[codigo],
            'simbolo': simbolos.get(codigo, codigo),
            'popular': codigo in self.MOEDAS_POPULARES
        }
    
    def limpar_historico(self, confirmar: bool = False) -> int:
        """Limpa histórico."""
        if not confirmar:
            return 0
        
        with self.db.session_scope() as session:
            repo = ConversaoRepository(session)
            count = repo.limpar_historico(confirmar=True)
        
        self.logger.info(f"Histórico limpo: {count} registros removidos")
        return count
    
    def get_status(self) -> Dict:
        """Retorna status do sistema."""
        return {
            "apis": self.api.get_status(),
            "cache": self.cache.get_stats(),
            "database": "connected" if self.db else "disconnected"
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.db.close()

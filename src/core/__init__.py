"""Módulo core - Lógica de negócio principal."""

from .conversor import ConversorMoedas
from .models import Conversao, Estatisticas, Moeda, Configuracao
from .cache import CacheManager

__all__ = ["ConversorMoedas", "Conversao", "Estatisticas", "Moeda", "Configuracao", "CacheManager"]

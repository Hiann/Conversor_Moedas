"""Sistema de cache para taxas de câmbio."""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from functools import wraps

from src.core.models import TaxaCambio


class CacheManager:
    """Gerenciador de cache em memória e disco."""
    
    def __init__(self, ttl_seconds: int = 3600, cache_dir: str = "cache"):
        self.ttl = ttl_seconds
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Gera chave única para o cache."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache."""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache."""
        # Tenta memória primeiro
        if key in self._memory_cache:
            if self._is_valid(key):
                return self._memory_cache[key]
            else:
                self.delete(key)
                return None
        
        # Tenta disco
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    self._memory_cache[key] = data['value']
                    self._timestamps[key] = timestamp
                    return data['value']
                else:
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Armazena valor no cache."""
        timestamp = datetime.now()
        
        # Memória
        self._memory_cache[key] = value
        self._timestamps[key] = timestamp
        
        # Disco
        cache_file = self._get_cache_file(key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp.isoformat(),
                'value': value
            }, f, default=str, ensure_ascii=False)
    
    def delete(self, key: str) -> None:
        """Remove item do cache."""
        self._memory_cache.pop(key, None)
        self._timestamps.pop(key, None)
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        self._memory_cache.clear()
        self._timestamps.clear()
        
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def _is_valid(self, key: str) -> bool:
        """Verifica se cache ainda é válido."""
        if key not in self._timestamps:
            return False
        return datetime.now() - self._timestamps[key] < timedelta(seconds=self.ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        disk_files = list(self.cache_dir.glob("*.json"))
        return {
            "memory_items": len(self._memory_cache),
            "disk_items": len(disk_files),
            "ttl_seconds": self.ttl
        }


def cached(ttl_seconds: int = 3600, cache_dir: str = "cache"):
    """Decorador para cache de funções."""
    cache = CacheManager(ttl_seconds, cache_dir)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave baseada nos argumentos
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Tenta obter do cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Executa função e armazena no cache
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        # Expõe métodos do cache
        wrapper.cache = cache
        wrapper.clear_cache = cache.clear
        
        return wrapper
    return decorator

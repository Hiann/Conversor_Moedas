"""Funções de validação."""

import re
from decimal import Decimal


def validar_codigo_moeda(codigo: str) -> str:
    """Valida código de moeda (3 letras maiúsculas)."""
    if not isinstance(codigo, str):
        raise ValueError('Código da moeda deve ser uma string')
    
    codigo = codigo.strip().upper()
    
    if not re.match(r'^[A-Z]{3}$', codigo):
        raise ValueError(f'Código de moeda inválido: {codigo}. Use 3 letras (ex: USD)')
    
    return codigo


def validar_valor(valor) -> Decimal:
    """Valida valor numérico positivo."""
    try:
        v = Decimal(str(valor))
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v
    except (ValueError, TypeError) as e:
        raise ValueError(f"Valor inválido: {e}")


def validar_email(email: str) -> bool:
    """Valida formato de email."""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))

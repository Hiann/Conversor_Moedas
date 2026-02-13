"""Funções de formatação."""

from decimal import Decimal


def formatar_moeda(valor: float, simbolo: str = '', decimal_places: int = 2) -> str:
    """Formata valor monetário."""
    try:
        valor_float = float(valor)
        formato = f'{{:,.{decimal_places}f}}'
        formatado = formato.format(valor_float)
        
        if simbolo:
            # Ajusta posição do símbolo baseado na moeda
            if simbolo in ['R$', '$']:
                return f"{simbolo}{formatado}"
            return f"{formatado} {simbolo}"
        
        return formatado
    except (ValueError, TypeError):
        return str(valor)


def formatar_taxa(taxa: float) -> str:
    """Formata taxa de câmbio."""
    if taxa >= 1:
        return f'{taxa:.4f}'
    elif taxa >= 0.01:
        return f'{taxa:.6f}'
    else:
        return f'{taxa:.8f}'


def formatar_data(data, formato: str = "%d/%m/%Y %H:%M") -> str:
    """Formata data."""
    if data is None:
        return ""
    return data.strftime(formato)


def truncar_texto(texto: str, maximo: int, sufixo: str = '...') -> str:
    """Trunca texto."""
    if len(texto) <= maximo:
        return texto
    return texto[:maximo - len(sufixo)] + sufixo

"""Testes para modelos."""

import unittest
from decimal import Decimal
from datetime import datetime

from src.core.models import Moeda, Conversao, Configuracao


class TestMoeda(unittest.TestCase):
    """Testes para modelo Moeda."""
    
    def test_criar_moeda_valida(self):
        """Testa criação de moeda válida."""
        moeda = Moeda(codigo="USD", nome="Dólar Americano", simbolo="$")
        self.assertEqual(moeda.codigo, "USD")
        self.assertEqual(moeda.nome, "Dólar Americano")
    
    def test_codigo_maiusculo(self):
        """Testa conversão automática para maiúsculas."""
        moeda = Moeda(codigo="brl", nome="Real")
        self.assertEqual(moeda.codigo, "BRL")
    
    def test_codigo_invalido(self):
        """Testa código inválido."""
        with self.assertRaises(ValueError):
            Moeda(codigo="US", nome="Inválido")
        
        with self.assertRaises(ValueError):
            Moeda(codigo="USDD", nome="Inválido")


class TestConversao(unittest.TestCase):
    """Testes para modelo Conversao."""
    
    def test_criar_conversao(self):
        """Testa criação de conversão."""
        conv = Conversao(
            valor_original=Decimal("100"),
            valor_convertido=Decimal("507.45"),
            moeda_origem="USD",
            moeda_destino="BRL",
            taxa=Decimal("5.0745"),
            taxa_inversa=Decimal("0.1971")
        )
        
        self.assertEqual(float(conv.valor_original), 100.0)
        self.assertEqual(conv.moeda_origem, "USD")
    
    def test_formatar_simples(self):
        """Testa formatação simples."""
        conv = Conversao(
            valor_original=Decimal("100"),
            valor_convertido=Decimal("507.45"),
            moeda_origem="USD",
            moeda_destino="BRL",
            taxa=Decimal("5.0745"),
            taxa_inversa=Decimal("0.1971")
        )
        
        formato = conv.formatar("simples")
        self.assertIn("USD", formato)
        self.assertIn("BRL", formato)


class TestConfiguracao(unittest.TestCase):
    """Testes para configurações."""
    
    def test_config_padrao(self):
        """Testa configurações padrão."""
        config = Configuracao()
        self.assertEqual(config.api_primary, "frankfurter")
        self.assertEqual(config.cache_ttl, 3600)
        self.assertTrue(config.cache_enabled)


if __name__ == '__main__':
    unittest.main()

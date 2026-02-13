"""Testes para o conversor principal."""

import unittest
from unittest.mock import Mock, patch
from decimal import Decimal

from src.core import ConversorMoedas
from src.core.models import Configuracao


class TestConversorMoedas(unittest.TestCase):
    """Testes para ConversorMoedas."""
    
    @patch('src.core.conversor.APIManager')
    @patch('src.core.conversor.get_db')
    def setUp(self, mock_db, mock_api):
        """Configuração dos testes."""
        mock_db.return_value = Mock()
        mock_db.return_value.session_scope = Mock()
        
        mock_api.return_value = Mock()
        mock_api.return_value.obter_taxa_par.return_value = Decimal("5.0745")
        mock_api.return_value.listar_moedas.return_value = {
            "USD": "Dólar", "BRL": "Real", "EUR": "Euro"
        }
        
        config = Configuracao(cache_enabled=False)
        self.conversor = ConversorMoedas(config)
    
    def test_converter(self):
        """Testa conversão básica."""
        resultado = self.conversor.converter(100, "USD", "BRL", salvar=False)
        
        self.assertEqual(float(resultado.valor_original), 100.0)
        self.assertEqual(resultado.moeda_origem, "USD")
        self.assertEqual(resultado.moeda_destino, "BRL")
    
    def test_converter_valor_invalido(self):
        """Testa conversão com valor inválido."""
        with self.assertRaises(ValueError):
            self.conversor.converter(-100, "USD", "BRL")
        
        with self.assertRaises(ValueError):
            self.conversor.converter(0, "USD", "BRL")
    
    def test_converter_mesma_moeda(self):
        """Testa conversão entre mesmas moedas."""
        with self.assertRaises(ValueError):
            self.conversor.converter(100, "USD", "USD")
    
    def test_buscar_moeda(self):
        """Testa busca de moeda."""
        resultados = self.conversor.buscar_moeda("US")
        self.assertIn("USD", resultados)


if __name__ == '__main__':
    unittest.main()

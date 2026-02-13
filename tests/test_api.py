"""Testes para APIs."""

import unittest
from unittest.mock import Mock, patch
from decimal import Decimal

from src.api.base import APIError
from src.api.frankfurter import FrankfurterClient
from src.api.manager import APIManager


class TestFrankfurterClient(unittest.TestCase):
    """Testes para cliente Frankfurter."""
    
    def setUp(self):
        self.client = FrankfurterClient()
    
    @patch('src.api.base.requests.Session.get')
    def test_obter_taxas(self, mock_get):
        """Testa obtenção de taxas."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "rates": {"BRL": 5.0745, "EUR": 0.9215}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        taxas = self.client.obter_taxas("USD")
        
        self.assertIn("BRL", taxas)
        self.assertAlmostEqual(float(taxas["BRL"]), 5.0745, places=4)
    
    @patch('src.api.base.requests.Session.get')
    def test_listar_moedas(self, mock_get):
        """Testa listagem de moedas."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "USD": "United States Dollar",
            "BRL": "Brazilian Real"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        moedas = self.client.listar_moedas()
        
        self.assertIn("USD", moedas)
        self.assertEqual(moedas["USD"], "United States Dollar")


class TestAPIManager(unittest.TestCase):
    """Testes para gerenciador de APIs."""
    
    def test_fallback(self):
        """Testa fallback entre APIs."""
        manager = APIManager(primary="frankfurter")
        self.assertEqual(len(manager.clients), 1)
        self.assertEqual(manager.clients[0].nome, "Frankfurter")


if __name__ == '__main__':
    unittest.main()

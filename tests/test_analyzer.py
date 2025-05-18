"""
Test pro analyzer.py, zejména pro synchronní wrapper analyze_query_sync.
"""

import unittest
import os
from memory_agent.analyzer import analyze_query_sync
from memory_agent.tools import MockMCPConnector

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        """Nastavení před každým testem"""
        # Vytvoření instance MockMCPConnector pro testy
        self.mock_connector = MockMCPConnector(data_path="./mock_data")

    def test_analyze_query_sync_company(self):
        """Test pro analyze_query_sync s dotazem na společnost."""
        # Dotaz jednoznačně identifikující společnost
        query = "Co je to MB TOOL?"
        result = analyze_query_sync(query, None, None, self.mock_connector)
        
        # Ověření, že výsledek je očekávaný typ
        self.assertEqual(result, "company")
        print(f"Test pro dotaz společnosti: '{query}' → '{result}'")

    def test_analyze_query_sync_person(self):
        """Test pro analyze_query_sync s dotazem na osobu."""
        # Dotaz jednoznačně identifikující osobu
        query = "Kdo je Jan Novák?"
        result = analyze_query_sync(query, None, None, self.mock_connector)
        
        # Ověření, že výsledek je očekávaný typ
        self.assertEqual(result, "person")
        print(f"Test pro dotaz osoby: '{query}' → '{result}'")

    def test_analyze_query_sync_relationship(self):
        """Test pro analyze_query_sync s dotazem na vztah."""
        # Dotaz jednoznačně identifikující vztah
        query = "Jaké jsou vztahy mezi MB TOOL a jeho dodavateli?"
        result = analyze_query_sync(query, None, None, self.mock_connector)
        
        # Ověření, že výsledek je očekávaný typ
        self.assertEqual(result, "relationship")
        print(f"Test pro dotaz vztahů: '{query}' → '{result}'")

    def test_analyze_query_sync_custom(self):
        """Test pro analyze_query_sync s obecným dotazem."""
        # Obecný dotaz
        query = "Jak se daří českému průmyslu?"
        result = analyze_query_sync(query, None, None, self.mock_connector)
        
        # Ověření, že výsledek je očekávaný typ
        self.assertEqual(result, "custom")
        print(f"Test pro obecný dotaz: '{query}' → '{result}'")


if __name__ == "__main__":
    unittest.main()

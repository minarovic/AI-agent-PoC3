"""
Oficiální jednotkové testy pro analyzer.py s podporou LLM-based analýzy dotazů.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from memory_agent.analyzer import (
    analyze_company_query, 
    analyze_query_sync, 
    get_anthropic_llm,
    extract_company_fallback
)

class TestAnalyzerWithLLM(unittest.TestCase):
    """Testy pro analyzátor s LLM podporou."""
    
    def setUp(self):
        """Nastavení před každým testem."""
        # Ujistíme se, že testy budou fungovat i bez API klíče
        self.original_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
    
    def tearDown(self):
        """Úklid po každém testu."""
        # Obnovíme původní API klíč, pokud existoval
        if self.original_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.original_api_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
    
    def test_get_anthropic_llm_no_api_key(self):
        """Test get_anthropic_llm bez API klíče."""
        self.assertIsNone(get_anthropic_llm())
    
    @unittest.skipIf(not os.environ.get("ANTHROPIC_API_KEY"), "Vyžaduje Anthropic API klíč")
    def test_get_anthropic_llm_with_api_key(self):
        """Test get_anthropic_llm s API klíčem."""
        llm = get_anthropic_llm()
        self.assertIsNotNone(llm)
    
    def test_extract_company_fallback(self):
        """Test fallback funkce pro extrakci společnosti."""
        # Test běžných společností
        self.assertEqual(extract_company_fallback("Co je to MB TOOL?"), "MB TOOL")
        self.assertEqual(extract_company_fallback("Analýza firmy ŠKODA AUTO"), "ŠKODA AUTO")
        
        # Test různých variant zápisu
        self.assertEqual(extract_company_fallback("Informace o bos automotive"), "BOS")
        self.assertEqual(extract_company_fallback("Něco o Flídr plast"), "Flídr plast")
    
    @patch('memory_agent.analyzer.get_anthropic_llm')
    def test_analyze_company_query_fallback(self, mock_get_llm):
        """Test analyze_company_query s fallbackem na regex."""
        # Simulujeme, že LLM není k dispozici
        mock_get_llm.return_value = None
        
        # Test různých dotazů
        company, analysis_type = analyze_company_query("Co je to MB TOOL?")
        self.assertEqual(company, "MB TOOL")
        self.assertEqual(analysis_type, "general")
        
        company, analysis_type = analyze_company_query("Porovnej rizika spojená s firmou BOS AUTOMOTIVE")
        self.assertEqual(company, "BOS")
        self.assertEqual(analysis_type, "risk_comparison")
        
        company, analysis_type = analyze_company_query("Udělej analýzu dodavatelů společnosti ADIS TACHOV")
        self.assertEqual(company, "ADIS TACHOV")
        self.assertEqual(analysis_type, "supplier_analysis")
    
    @patch('memory_agent.analyzer.get_anthropic_llm')
    def test_analyze_company_query_with_llm(self, mock_get_llm):
        """Test analyze_company_query s LLM."""
        # Vytvoříme mock pro LLM
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Nastavíme očekávaný výstup z LLM
        mock_response = MagicMock()
        mock_response.content = """
        {
            "company": "MB TOOL",
            "analysis_type": "general"
        }
        """
        mock_llm.invoke.return_value = mock_response
        
        # Test analýzy s LLM
        company, analysis_type = analyze_company_query("Co je to MB TOOL?")
        
        # Ověříme výsledek
        self.assertEqual(company, "MB TOOL")
        self.assertEqual(analysis_type, "general")
        
        # Ověříme, že LLM byl volán
        self.assertTrue(mock_llm.invoke.called)
    
    @patch('memory_agent.analyzer.analyze_company_query')
    def test_analyze_query_sync(self, mock_analyze):
        """Test synchronní wrapperu analyze_query_sync."""
        # Nastavíme očekávaný výsledek
        mock_analyze.return_value = ("MB TOOL", "general")
        
        # Zavoláme funkci
        result = analyze_query_sync("Co je to MB TOOL?")
        
        # Ověříme, že funkce vrátila očekávaný výsledek
        self.assertEqual(result, {"company": "MB TOOL", "analysis_type": "general"})
        
        # Ověříme, že byla volána správná funkce
        mock_analyze.assert_called_once_with("Co je to MB TOOL?")

if __name__ == "__main__":
    unittest.main()

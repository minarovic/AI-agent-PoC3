#!/usr/bin/env python3
"""
Test pro ověření funkčnosti zjednodušeného analyzeru.py
"""
import sys
import os
import logging

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Přidání cesty k src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import funkcí z analyzeru
try:
    from src.memory_agent.analyzer import (
        detect_analysis_type,
        analyze_company_query,
        analyze_query_sync,
        extract_company_name
    )
    
    # Testovací dotazy
    test_queries = [
        # Dotazy pro risk_comparison
        "Jaká jsou rizika pro MB TOOL?",
        "Compliance status for ADIS TACHOV",
        "Má BOS AUTOMOTIVE nějaké sankce?",
        
        # Dotazy pro supplier_analysis
        "Kdo jsou dodavatelé pro Flídr plast?",
        "Supply chain for BOS",
        "Ukaž mi tier 2 dodavatele pro ŠKODA AUTO",
        
        # Dotazy pro general
        "Co je to MB TOOL?",
        "Informace o společnosti ADIS TACHOV",
        "Tell me about BOS AUTOMOTIVE"
    ]
    
    def test_analyzer():
        """Test funkcí zjednodušeného analyzeru"""
        print("\n=== TEST ZJEDNODUŠENÉHO ANALYZERU.PY ===\n")
        
        for query in test_queries:
            print(f"\nDotaz: '{query}'")
            
            # Test funkce detect_analysis_type
            analysis_type = detect_analysis_type(query)
            print(f"  > Detekovaný typ analýzy: {analysis_type}")
            
            # Test funkce analyze_company_query
            company, analysis_type = analyze_company_query(query)
            print(f"  > Extrahovaná společnost: {company}")
            print(f"  > Typ analýzy: {analysis_type}")
            
            # Test funkce analyze_query_sync
            query_type = analyze_query_sync(query)
            print(f"  > Typ dotazu: {query_type}")
            
            # Test funkce extract_company_name
            if 'extract_company_name' in globals():
                company_name = extract_company_name(query)
                print(f"  > Extrahované jméno společnosti: {company_name}")
            
            print("-" * 50)
    
    if __name__ == "__main__":
        test_analyzer()
        print("\nVše OK!")

except ImportError as e:
    print(f"Chyba při importu: {e}")
    print("Ujistěte se, že složka 'src' obsahuje správně strukturovaný modul memory_agent s analyzer.py")
except Exception as e:
    print(f"Obecná chyba: {e}")

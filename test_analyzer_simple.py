#!/usr/bin/env python3
"""
Jednoduchý test pro zjednodušenou verzi analyzéru.
Tento skript testuje, zda analyzér správně funguje s N8N-inspirovaným promptem.

DŮLEŽITÉ: Tento skript volá skutečný LLM API.
"""

import os
import sys
import logging
import os
import sys
import logging

# Přidáme nadřazený adresář do sys.path, aby bylo možné importovat memory_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Nastavení loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Načtení proměnných prostředí z .env souboru
from dotenv import load_dotenv
load_dotenv()  # API klíče jsou nyní načteny z .env souboru

# Kontrola, zda jsou nastaveny potřebné API klíče
if not os.environ.get("ANTHROPIC_API_KEY"):
    logger.warning("ANTHROPIC_API_KEY není nastaven! Test pravděpodobně selže.")
if not os.environ.get("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY není nastaven! Test pravděpodobně selže.")

def test_analyzer_with_real_llm():
    """Test analýzy dotazů pomocí skutečného LLM."""
    from memory_agent.analyzer import analyze_company_query, analyze_query_sync
    
    test_queries = [
        "Co je to MB TOOL?",
        "Má MB TOOL nějaké sankce?",
        "Co jsou rizika pro ADIS TACHOV?",
        "Jaké jsou vztahy mezi ŠKODA AUTO a jejími dodavateli?",
        "Kdo dodává komponenty pro Flídr plast?"
    ]
    
    # Testování analyze_company_query
    logger.info("\nTestování analyze_company_query:")
    for query in test_queries:
        try:
            company, analysis_type = analyze_company_query(query)
            logger.info(f"Dotaz: '{query}' -> Společnost: '{company}', Typ: '{analysis_type}'")
        except Exception as e:
            logger.error(f"Chyba při zpracování dotazu '{query}': {str(e)}")
    
    # Testování analyze_query_sync
    logger.info("\nTestování analyze_query_sync:")
    for query in test_queries:
        try:
            query_type = analyze_query_sync(query)
            logger.info(f"Dotaz: '{query}' -> Typ dotazu: '{query_type}'")
        except Exception as e:
            logger.error(f"Chyba při zpracování dotazu '{query}': {str(e)}")
    
    logger.info("Test dokončen.")

if __name__ == "__main__":
    test_analyzer_with_real_llm()

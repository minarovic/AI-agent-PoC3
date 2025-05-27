#!/usr/bin/env python3
"""
Jednoduchý test pro N8N-inspired analyzér.
"""

import os
import sys
import logging

# Nastavení loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Načtení proměnných prostředí z .env souboru
from dotenv import load_dotenv
load_dotenv()  # API klíče jsou nyní načteny z .env souboru

# Kontrola, zda jsou nastaveny potřebné API klíče
if not os.environ.get("ANTHROPIC_API_KEY"):
    logger.warning("ANTHROPIC_API_KEY není nastaven! Test pravděpodobně selže.")
    logger.warning("Ujistěte se, že v souboru .env máte nastavení:")
    logger.warning("ANTHROPIC_API_KEY=váš_API_klíč_zde")

# Importy LangChain
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    logger.error("Chybí LangChain balíčky. Nainstalujte je pomocí: pip install langchain_core langchain_anthropic")
    sys.exit(1)

# N8N-inspired prompt
PROMPT = """Analyze the user's input to extract company name and analysis type.

The format should follow the pattern: "Company Name; analysis_type"
Where analysis_type can be:
- risk_comparison (for risk analysis, compliance, sanctions, etc.)
- common_suppliers (for supplier relationships, supply chain, etc.)
- general (for general information about the company)

Examples:
- Input: "Find risks for Apple Inc"
  Output: "Apple Inc; risk_comparison"
  
- Input: "Show me suppliers for Samsung Electronics"
  Output: "Samsung Electronics; common_suppliers"
  
- Input: "I need information about Microsoft"
  Output: "Microsoft; general"

- Input: "Má MB TOOL nějaké sankce?"
  Output: "MB TOOL; risk_comparison"

- Input: "Jaké jsou vztahy mezi ŠKODA AUTO a jejími dodavateli?"
  Output: "ŠKODA AUTO; common_suppliers"

- Input: "Co je to Flídr plast?"
  Output: "Flídr plast; general"

Input: {query}

Only respond with the structured output in the format "Company Name; analysis_type" - no other text.
"""

def analyze_with_n8n_prompt(query):
    """
    Analyzuj dotaz pomocí N8N-inspired promptu.
    
    Args:
        query: Dotaz k analýze
        
    Returns:
        tuple: (název_společnosti, typ_analýzy)
    """
    try:
        # Inicializace LLM
        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.1)
        
        # Vytvoření zpráv pro LLM
        messages = [
            SystemMessage(content="You are an expert at extracting company names and analysis intents from queries."),
            HumanMessage(content=PROMPT.format(query=query))
        ]
        
        # Získání odpovědi z LLM
        response = llm.invoke(messages)
        result = response.content.strip()
        logger.info(f"LLM analýza dotazu: '{query}' → '{result}'")
        
        # Parsování výsledku
        if ";" in result:
            company_name, analysis_type = result.split(";", 1)
            return company_name.strip(), analysis_type.strip()
        else:
            # Pokud není formát správný, použij celou odpověď jako název společnosti
            return result, "general"
    except Exception as e:
        logger.error(f"Chyba při analýze dotazu: {str(e)}")
        return "Unknown Company", "general"

def main():
    """
    Hlavní funkce pro testování N8N-inspired analyzéru.
    """
    test_queries = [
        "Co je to MB TOOL?",
        "Má MB TOOL nějaké sankce?",
        "Co jsou rizika pro ADIS TACHOV?",
        "Jaké jsou vztahy mezi ŠKODA AUTO a jejími dodavateli?",
        "Kdo dodává komponenty pro Flídr plast?"
    ]
    
    logger.info("Testování N8N-inspired analyzéru:")
    for query in test_queries:
        company, analysis_type = analyze_with_n8n_prompt(query)
        logger.info(f"Dotaz: '{query}' → Společnost: '{company}', Typ analýzy: '{analysis_type}'")
    
    logger.info("Test dokončen.")

if __name__ == "__main__":
    main()

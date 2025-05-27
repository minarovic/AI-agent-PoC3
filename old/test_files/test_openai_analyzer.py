#!/usr/bin/env python3
"""
Jednoduchý test pro N8N-inspired analyzér s přímým použitím OpenAI API.
"""

import os
import sys
import logging
import json
import requests

# Nastavení loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Načtení proměnných prostředí z .env souboru
from dotenv import load_dotenv
load_dotenv()  # API klíče jsou nyní načteny z .env souboru

# Kontrola, zda jsou nastaveny potřebné API klíče
if not os.environ.get("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY není nastaven! Test pravděpodobně selže.")
    logger.warning("Ujistěte se, že v souboru .env máte nastavení:")
    logger.warning("OPENAI_API_KEY=váš_API_klíč_zde")

# Použití API klíče z proměnné prostředí
API_KEY = os.environ.get("OPENAI_API_KEY")

# Přímé použití OpenAI API bez závislostí
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

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

def analyze_with_openai(query):
    """
    Analyzuj dotaz s využitím OpenAI API přímo.
    
    Args:
        query: Dotaz k analýze
        
    Returns:
        tuple: (název_společnosti, typ_analýzy)
    """
    try:
        # Vytvoření požadavku na OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are an expert at extracting company names and analysis intents from queries."},
                {"role": "user", "content": PROMPT.format(query=query)}
            ],
            "temperature": 0.1
        }
        
        # Odeslání požadavku
        response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Kontrola chyb
        
        # Zpracování odpovědi
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        logger.info(f"OpenAI analýza dotazu: '{query}' → '{content}'")
        
        # Parsování výsledku
        if ";" in content:
            company_name, analysis_type = content.split(";", 1)
            return company_name.strip(), analysis_type.strip()
        else:
            # Pokud není formát správný, použij celou odpověď jako název společnosti
            return content, "general"
    
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
    
    logger.info("Testování N8N-inspired analyzéru s OpenAI:")
    for query in test_queries:
        company, analysis_type = analyze_with_openai(query)
        logger.info(f"Dotaz: '{query}' → Společnost: '{company}', Typ analýzy: '{analysis_type}'")
    
    logger.info("Test dokončen.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Přímý test pro zjednodušenou verzi analyzéru bez závislosti na memory_agent.
"""

import os
import sys
import logging
from typing import Dict, List, Literal, Optional, Any, Tuple
from pydantic import BaseModel, Field

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

# API klíče by nikdy neměly být přímo v kódu, vždy používejte .env soubor nebo proměnné prostředí

# Potrebné importy pro LangChain
try:
    from langchain.chat_models import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    logger.error("Chybí LangChain balíčky. Zkuste nainstalovat: pip install langchain langchain_anthropic")
    sys.exit(1)

# Definice typů analýzy
AnalysisType = Literal["risk_comparison", "common_suppliers", "general"]

# Platné typy analýzy
VALID_ANALYSIS_TYPES = ["risk_comparison", "common_suppliers", "general"]

# Define the simplified prompt inspired by N8N
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

class AnalysisResult(BaseModel):
    """Result of user input analysis."""
    companies: List[str] = Field(description="List of identified companies")
    company: str = Field(description="Primary company (first in the list)")
    analysis_type: AnalysisType = Field(description="Type of analysis to perform")
    query: str = Field(description="Original user query")
    is_company_analysis: bool = Field(description="Indicates whether the query is about company analysis")
    confidence: float = Field(ge=0.0, le=1.0, description="Analysis confidence level (0.0 - 1.0)")

def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Analyze a user query to extract company name and analysis type.
    Uses only LLM with a prompt-based approach, no regex fallbacks.
    
    Args:
        query: User query to analyze
        
    Returns:
        Tuple of (company_name, analysis_type)
    """
    try:
        # Initialize LLM model
        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.1)
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content="You are an expert at extracting company names and analysis intents from queries."),
            HumanMessage(content=PROMPT.format(query=query))
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        result = response.content.strip()
        logger.info(f"LLM analyzed query: '{query}' → '{result}'")
        
        # Parse the result
        if ";" in result:
            company_name, analysis_type = result.split(";", 1)
            company_name = company_name.strip()
            analysis_type = analysis_type.strip()
            
            # Validate analysis type
            if analysis_type not in VALID_ANALYSIS_TYPES:
                # Default to general if not valid
                analysis_type = "general"
                
            return company_name, analysis_type
        else:
            # If format is incorrect, try using the whole response as company name
            company_name = result
            # Default to general analysis
            return company_name, "general"
    
    except Exception as e:
        logger.error(f"Error analyzing query: {str(e)}")
        # Return default values in case of error
        return "Unknown Company", "general"

def test_analyzer_direct():
    """Test analýzy dotazů přímo bez závislosti na memory_agent."""
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
    
    logger.info("Test dokončen.")

if __name__ == "__main__":
    test_analyzer_direct()

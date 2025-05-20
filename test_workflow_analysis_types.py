#!/usr/bin/env python
"""
Test skript pro ověření celého workflow s podporou typů analýz.

Tento skript testuje celý workflow od zpracování dotazu přes určení typu
analýzy až po načtení dat a provedení analýzy pro různé typy dotazů.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional

# Nastavení logování
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_workflow")

# Přidání src do PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import potřebných modulů
from memory_agent.state import State
from memory_agent.graph_nodes import (
    determine_analysis_type,
    plan_company_analysis,
    retrieve_additional_company_data,
    analyze_company_data
)
from memory_agent.analyzer import detect_analysis_type
from memory_agent.tools import MockMCPConnector

# Testovací dotazy pro různé typy analýz
TEST_QUERIES = [
    {
        "query": "Jaké jsou základní informace o společnosti Adis?",
        "expected_type": "general",
        "company_name": "Adis"
    },
    {
        "query": "Řekni mi o rizicích spojených se společností BOS Automotive CZ.",
        "expected_type": "risk_comparison",
        "company_name": "BOS Automotive CZ"
    },
    {
        "query": "Kteří jsou hlavní dodavatelé společnosti Flidr?",
        "expected_type": "supplier_analysis",
        "company_name": "Flidr"
    }
]

def simulate_company_extraction(query: str, expected_company: str) -> Dict[str, Any]:
    """Simuluje extrakci společnosti z dotazu."""
    company_data = {
        "Adis": {"id": "adis12345", "name": "Adis"},
        "BOS Automotive CZ": {"id": "bos_cze12345", "name": "BOS Automotive CZ"},
        "BOS Automotive DE": {"id": "bos_deu12345", "name": "BOS Automotive DE"},
        "Flidr": {"id": "flidr12345", "name": "Flidr"},
        "MB Tool": {"id": "mb_tool12345", "name": "MB Tool"}
    }
    
    if expected_company in company_data:
        return {"basic_info": company_data[expected_company]}
    else:
        return {"basic_info": {"id": "unknown", "name": expected_company}}

def test_workflow(query_data: Dict[str, str]) -> None:
    """Testuje workflow pro jeden dotaz."""
    query = query_data["query"]
    expected_type = query_data["expected_type"]
    company_name = query_data["company_name"]
    
    logger.info(f"\n=== Test workflow pro dotaz: {query} ===")
    logger.info(f"Očekávaný typ analýzy: {expected_type}")
    logger.info(f"Očekávaná společnost: {company_name}")
    
    # Inicializace stavu
    state = State(messages=[])
    state.current_query = query
    
    # Krok 1: Detekce typu analýzy
    try:
        logger.info("Krok 1: Detekce typu analýzy")
        analysis_type_result = detect_analysis_type(query)
        logger.info(f"Detekovaný typ analýzy: {analysis_type_result}")
        
        state_update = determine_analysis_type(state)
        state.analysis_type = state_update.get("analysis_type", "general")
        
        if state.analysis_type == expected_type:
            logger.info("✅ Typ analýzy odpovídá očekávání")
        else:
            logger.warning(f"⚠️ Typ analýzy se liší od očekávání: {state.analysis_type} vs {expected_type}")
    except Exception as e:
        logger.error(f"❌ Chyba při detekci typu analýzy: {str(e)}")
        return
    
    # Krok 2: Simulace extrakce společnosti
    try:
        logger.info("\nKrok 2: Simulace extrakce společnosti")
        company_data = simulate_company_extraction(query, company_name)
        state.company_data = company_data
        logger.info(f"Extrahovaná společnost: {company_data['basic_info']['name']} (ID: {company_data['basic_info']['id']})")
    except Exception as e:
        logger.error(f"❌ Chyba při simulaci extrakce společnosti: {str(e)}")
        return
    
    # Krok 3: Načtení dodatečných dat podle typu analýzy
    try:
        logger.info("\nKrok 3: Načtení dodatečných dat podle typu analýzy")
        data_result = retrieve_additional_company_data(state)
        
        # Aktualizace stavu
        for key, value in data_result.items():
            if key != "error_state":
                setattr(state, key, value)
        
        logger.info(f"Data načtena pro typ analýzy: {state.analysis_type}")
        
        # Kontrola načtených dat podle typu analýzy
        if state.analysis_type == "general":
            has_expected_data = "search_info" in state.company_data
            data_type = "search_info a financial_data"
        elif state.analysis_type == "risk_comparison":
            has_expected_data = hasattr(state, "risk_factors_data")
            data_type = "risk_factors_data"
        elif state.analysis_type == "supplier_analysis":
            has_expected_data = hasattr(state, "relationships_data") and hasattr(state, "supply_chain_data")
            data_type = "relationships_data a supply_chain_data"
        
        if has_expected_data:
            logger.info(f"✅ Správně načtena očekávaná data: {data_type}")
        else:
            logger.warning(f"⚠️ Chybí očekávaná data: {data_type}")
    except Exception as e:
        logger.error(f"❌ Chyba při načítání dat: {str(e)}")
        return
    
    # Krok 4: Analýza dat
    try:
        logger.info("\nKrok 4: Analýza dat")
        analysis_result = analyze_company_data(state)
        
        # Aktualizace stavu
        if "analysis_result" in analysis_result:
            state.analysis_result = analysis_result["analysis_result"]
            
            logger.info(f"Analýza dokončena, výsledek obsahuje:")
            logger.info(f"- Typ analýzy: {state.analysis_result.get('analysis_type')}")
            logger.info(f"- Souhrn: {state.analysis_result.get('summary')}")
            
            # Kontrola typu analýzy ve výsledku
            if state.analysis_result.get("analysis_type") == expected_type:
                logger.info("✅ Typ analýzy ve výsledku odpovídá očekávání")
            else:
                logger.warning(f"⚠️ Typ analýzy ve výsledku se liší od očekávání: {state.analysis_result.get('analysis_type')} vs {expected_type}")
            
            # Kontrola klíčových sekcí podle typu analýzy
            if expected_type == "general" and "basic_info" in state.analysis_result:
                logger.info("✅ Výsledek obsahuje očekávané sekce pro general analýzu")
            elif expected_type == "risk_comparison" and "risk_factors" in state.analysis_result:
                logger.info("✅ Výsledek obsahuje očekávané sekce pro risk_comparison analýzu")
            elif expected_type == "supplier_analysis" and "suppliers" in state.analysis_result:
                logger.info("✅ Výsledek obsahuje očekávané sekce pro supplier_analysis analýzu")
        else:
            logger.warning("⚠️ Analýza dat nevrátila očekávaný výsledek")
    except Exception as e:
        logger.error(f"❌ Chyba při analýze dat: {str(e)}")

def main():
    """Hlavní funkce pro spuštění testů."""
    logger.info("=== Test workflow s podporou typů analýz ===")
    
    for query_data in TEST_QUERIES:
        test_workflow(query_data)
        print("\n" + "-" * 80)

if __name__ == "__main__":
    main()

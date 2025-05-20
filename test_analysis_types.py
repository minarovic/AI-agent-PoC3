#!/usr/bin/env python
"""
Test skript pro ověření podpory typů analýz v Memory Agent.

Tento skript testuje funkčnost tří typů analýz:
- general: Obecná analýza společnosti
- risk_comparison: Analýza rizik a compliance
- supplier_analysis: Analýza dodavatelských vztahů
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional

# Pokus o instalaci chybějících závislostí
try:
    import importlib.util
    missing_modules = []
    
    for module in ["pydantic", "typing_extensions", "langchain_core", "unidecode", "langgraph"]:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Chybějící moduly: {', '.join(missing_modules)}")
        print("Instaluji chybějící moduly...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules)
        print("Moduly nainstalovány.")
except Exception as e:
    print(f"Varování při kontrole závislostí: {str(e)}")

# Nastavení logování
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_analysis_types")

# Přidání src do PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import funkcí pro testování
from memory_agent.analyzer import detect_analysis_type
from memory_agent.tools import MockMCPConnector
from memory_agent.graph_nodes import determine_analysis_type, retrieve_additional_company_data, analyze_company_data
from memory_agent.state import State

# Test případy pro různé typy analýz
TEST_CASES = [
    {
        "name": "General Analysis",
        "query": "Jaké jsou základní informace o společnosti Adis?",
        "expected_type": "general",
        "company_id": "adis12345",
    },
    {
        "name": "Risk Comparison",
        "query": "Jaká jsou rizika spojená se společností BOS Automotive?",
        "expected_type": "risk_comparison",
        "company_id": "bos_cze12345",
    },
    {
        "name": "Supplier Analysis",
        "query": "Kteří jsou dodavatelé pro Flídr?",
        "expected_type": "supplier_analysis",
        "company_id": "flidr12345",
    }
]

def create_test_state(query: str, company_id: str, analysis_type: str) -> State:
    """Vytvoří testovací stav pro workflow."""
    # Vytvoření základního stavu
    state = State(messages=[])
    
    # Nastavení dotazu a typu analýzy
    state.current_query = query
    state.analysis_type = analysis_type
    
    # Nastavení základních dat o společnosti
    state.company_data = {
        "basic_info": {
            "id": company_id,
            "name": company_id.split("12345")[0].capitalize()
        }
    }
    
    return state

def test_determine_analysis_type():
    """Test funkce determine_analysis_type."""
    logger.info("Spouštím test determine_analysis_type")
    
    for test_case in TEST_CASES:
        # Vytvoření testovacího stavu
        state = create_test_state(test_case["query"], test_case["company_id"], "")
        
        # Volání testované funkce
        result = determine_analysis_type(state)
        
        # Kontrola výsledku
        if "analysis_type" in result and result["analysis_type"] == test_case["expected_type"]:
            logger.info(f"✅ Test determine_analysis_type pro '{test_case['name']}' prošel")
        else:
            logger.error(f"❌ Test determine_analysis_type pro '{test_case['name']}' selhal. "
                       f"Očekáván typ: {test_case['expected_type']}, "
                       f"Obdržen typ: {result.get('analysis_type', 'není nastaveno')}")

def test_retrieve_additional_company_data():
    """Test funkce retrieve_additional_company_data."""
    logger.info("Spouštím test retrieve_additional_company_data")
    
    for test_case in TEST_CASES:
        # Vytvoření testovacího stavu
        state = create_test_state(test_case["query"], test_case["company_id"], test_case["expected_type"])
        
        # Volání testované funkce
        try:
            result = retrieve_additional_company_data(state)
            logger.info(f"✅ Test retrieve_additional_company_data pro '{test_case['name']}' prošel")
            
            # Další kontroly podle typu analýzy
            if test_case["expected_type"] == "general":
                if "search_info" in result.get("company_data", {}):
                    logger.info("  ✅ Data pro general analýzu obsahují search_info")
                else:
                    logger.warning("  ⚠️ Data pro general analýzu neobsahují search_info")
            
            elif test_case["expected_type"] == "risk_comparison":
                if "risk_factors_data" in result:
                    logger.info("  ✅ Data pro risk_comparison analýzu obsahují risk_factors_data")
                else:
                    logger.warning("  ⚠️ Data pro risk_comparison analýzu neobsahují risk_factors_data")
            
            elif test_case["expected_type"] == "supplier_analysis":
                if "relationships_data" in result and "supply_chain_data" in result:
                    logger.info("  ✅ Data pro supplier_analysis analýzu obsahují relationships_data a supply_chain_data")
                else:
                    logger.warning("  ⚠️ Data pro supplier_analysis analýzu neobsahují relationships_data nebo supply_chain_data")
        
        except Exception as e:
            logger.error(f"❌ Test retrieve_additional_company_data pro '{test_case['name']}' selhal: {str(e)}")

def test_analyze_company_data():
    """Test funkce analyze_company_data."""
    logger.info("Spouštím test analyze_company_data")
    
    for test_case in TEST_CASES:
        # Vytvoření testovacího stavu
        state = create_test_state(test_case["query"], test_case["company_id"], test_case["expected_type"])
        
        # Nastavení dodatečných dat podle typu analýzy
        if test_case["expected_type"] == "general":
            state.company_data["search_info"] = {"countries": ["CZ"], "addresses": []}
            state.company_data["financials"] = {"supplier_since": "2020"}
        
        elif test_case["expected_type"] == "risk_comparison":
            state.risk_factors_data = {
                "risk_score": 65,
                "all_risk_factors": [
                    {"factor": "sanctions", "category": "compliance", "level": "high"}
                ]
            }
        
        elif test_case["expected_type"] == "supplier_analysis":
            state.relationships_data = {
                test_case["company_id"]: [
                    {
                        "type": "has_supplier",
                        "source": {"id": test_case["company_id"]},
                        "target": {"id": "supplier1", "label": "Supplier 1"},
                        "metadata": {"tier": "1"}
                    }
                ]
            }
            state.supply_chain_data = {
                test_case["company_id"]: [
                    {
                        "source": {"id": test_case["company_id"]},
                        "target": {"id": "supplier1", "label": "Supplier 1"},
                        "tier": "1"
                    }
                ]
            }
        
        # Volání testované funkce
        try:
            result = analyze_company_data(state)
            logger.info(f"✅ Test analyze_company_data pro '{test_case['name']}' prošel")
            
            # Kontrola, zda výsledek obsahuje správný typ analýzy
            if "analysis_result" in result and result["analysis_result"].get("analysis_type") == test_case["expected_type"]:
                logger.info(f"  ✅ Výsledek analýzy obsahuje správný typ: {test_case['expected_type']}")
            else:
                logger.warning(f"  ⚠️ Výsledek analýzy obsahuje nesprávný typ: {result.get('analysis_result', {}).get('analysis_type', 'není nastaveno')}")
                
            # Další kontroly podle typu analýzy
            if test_case["expected_type"] == "general":
                if "basic_info" in result.get("analysis_result", {}) and "financial_overview" in result.get("analysis_result", {}):
                    logger.info("  ✅ Výsledek general analýzy obsahuje očekávané sekce")
                else:
                    logger.warning("  ⚠️ Výsledku general analýzy chybí očekávané sekce")
            
            elif test_case["expected_type"] == "risk_comparison":
                if "risk_score" in result.get("analysis_result", {}) and "risk_factors" in result.get("analysis_result", {}):
                    logger.info("  ✅ Výsledek risk_comparison analýzy obsahuje očekávané sekce")
                else:
                    logger.warning("  ⚠️ Výsledku risk_comparison analýzy chybí očekávané sekce")
            
            elif test_case["expected_type"] == "supplier_analysis":
                if "suppliers" in result.get("analysis_result", {}) and "supply_chain" in result.get("analysis_result", {}):
                    logger.info("  ✅ Výsledek supplier_analysis analýzy obsahuje očekávané sekce")
                else:
                    logger.warning("  ⚠️ Výsledku supplier_analysis analýzy chybí očekávané sekce")
        
        except Exception as e:
            logger.error(f"❌ Test analyze_company_data pro '{test_case['name']}' selhal: {str(e)}")

def main():
    """Hlavní funkce pro spuštění testů."""
    logger.info("=== Test podpory typů analýz ===")
    
    # Test zjištění typu analýzy
    test_determine_analysis_type()
    print()
    
    # Test načítání dat podle typu analýzy
    test_retrieve_additional_company_data()
    print()
    
    # Test analýzy dat podle typu analýzy
    test_analyze_company_data()

if __name__ == "__main__":
    main()

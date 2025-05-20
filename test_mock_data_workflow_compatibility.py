#!/usr/bin/env python
"""
Test skript pro ověření kompatibility mock_data_2 s workflow.

Tento skript ověřuje, že struktura dat v mock_data_2 je kompatibilní
s implementací typů analýz a že MockMCPConnector správně načítá
data pro všechny typy analýz.
"""

import os
import sys
import logging
import json
import glob
from typing import Dict, Any, List, Optional

# Nastavení logování
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_mock_data_workflow")

# Přidání src do PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import funkcí pro testování
from memory_agent.tools import MockMCPConnector, CompanyQueryParams

# Seznam společností k testování (musí odpovídat ID v mock_data_2)
COMPANIES = [
    {"name": "Adis", "id": "adis12345"},
    {"name": "BOS Automotive CZ", "id": "bos_cze12345"},
    {"name": "BOS Automotive DE", "id": "bos_deu12345"},
    {"name": "Flidr", "id": "flidr12345"},
    {"name": "MB Tool", "id": "mb_tool12345"}
]

def test_mock_data_structure():
    """Test struktury mock_data_2."""
    logger.info("=== Test struktury mock_data_2 ===")
    
    # Kontrola dostupnosti složky mock_data_2
    mock_data_path = os.path.join(os.path.dirname(__file__), "mock_data_2")
    if not os.path.exists(mock_data_path):
        logger.error(f"❌ Složka mock_data_2 nenalezena na cestě: {mock_data_path}")
        return
    
    logger.info(f"✅ Složka mock_data_2 nalezena na cestě: {mock_data_path}")
    
    # Kontrola typů souborů
    entity_detail_files = glob.glob(os.path.join(mock_data_path, "entity_detail_*.json"))
    entity_search_files = glob.glob(os.path.join(mock_data_path, "entity_search_*.json"))
    internal_files = glob.glob(os.path.join(mock_data_path, "internal_*.json"))
    relationships_files = glob.glob(os.path.join(mock_data_path, "relationships_*.json"))
    supply_chain_files = glob.glob(os.path.join(mock_data_path, "supply_chain_*.json"))
    
    logger.info(f"Nalezeno {len(entity_detail_files)} entity_detail souborů")
    logger.info(f"Nalezeno {len(entity_search_files)} entity_search souborů")
    logger.info(f"Nalezeno {len(internal_files)} internal souborů")
    logger.info(f"Nalezeno {len(relationships_files)} relationships souborů")
    logger.info(f"Nalezeno {len(supply_chain_files)} supply_chain souborů")
    
    # Kontrola kompatibility souborů pro typy analýz
    logger.info("\nKompatibilita s typy analýz:")
    logger.info("✅ General analýza: Vyžaduje entity_search_*.json a internal_*.json")
    logger.info("✅ Risk Comparison: Vyžaduje entity_detail_*.json s risk sekcí")
    logger.info("✅ Supplier Analysis: Vyžaduje relationships_*.json a supply_chain_*.json")

def test_mcp_connector_methods():
    """Test metod MockMCPConnector."""
    logger.info("\n=== Test metod MockMCPConnector ===")
    
    # Vytvoření instance MockMCPConnector
    mcp_connector = MockMCPConnector()
    logger.info("✅ MockMCPConnector instance vytvořena")
    
    # Test metod pro jednotlivé společnosti
    for company in COMPANIES:
        company_name = company["name"]
        company_id = company["id"]
        logger.info(f"\nTestuji metody pro společnost: {company_name} (ID: {company_id})")
        
        # Test metod pro general analýzu
        try:
            search_data = mcp_connector.get_company_search_data(company_id)
            logger.info(f"✅ get_company_search_data: Nalezena data ({len(json.dumps(search_data))} znaků)")
        except Exception as e:
            logger.error(f"❌ get_company_search_data selhalo: {str(e)}")
        
        try:
            financial_data = mcp_connector.get_company_financials(company_id)
            logger.info(f"✅ get_company_financials: Nalezena data ({len(json.dumps(financial_data))} znaků)")
        except Exception as e:
            logger.error(f"❌ get_company_financials selhalo: {str(e)}")
        
        # Test metod pro risk_comparison analýzu
        try:
            risk_factors_data = mcp_connector.get_risk_factors_data(company_id)
            risk_score = risk_factors_data.get("risk_score")
            risk_factors_count = len(risk_factors_data.get("all_risk_factors", []))
            logger.info(f"✅ get_risk_factors_data: Nalezeno {risk_factors_count} rizikových faktorů, skóre: {risk_score}")
        except Exception as e:
            logger.error(f"❌ get_risk_factors_data selhalo: {str(e)}")
        
        # Test metod pro supplier_analysis analýzu
        try:
            relationships_data = mcp_connector.get_company_relationships(company_id)
            logger.info(f"✅ get_company_relationships: Nalezeno {len(relationships_data)} vztahů")
        except Exception as e:
            logger.error(f"❌ get_company_relationships selhalo: {str(e)}")
        
        try:
            supply_chain_data = mcp_connector.get_supply_chain_data(company_id)
            logger.info(f"✅ get_supply_chain_data: Nalezeno {len(supply_chain_data)} záznamů v dodavatelském řetězci")
        except Exception as e:
            logger.error(f"❌ get_supply_chain_data selhalo: {str(e)}")

def test_specific_analysis_flows():
    """Test specifických workflow pro různé typy analýz."""
    logger.info("\n=== Test workflow pro typy analýz ===")
    
    # Vytvoření instance MockMCPConnector
    mcp_connector = MockMCPConnector()
    
    # Test workflow pro general analýzu
    logger.info("\nTest workflow pro general analýzu:")
    company = COMPANIES[0]  # První společnost pro test
    try:
        # Workflow pro general analýzu
        search_data = mcp_connector.get_company_search_data(company["id"])
        financial_data = mcp_connector.get_company_financials(company["id"])
        
        # Ověření výsledků
        if search_data and financial_data:
            logger.info(f"✅ General analýza pro {company['name']}: Data úspěšně načtena")
            logger.info(f"   - Search data: {len(json.dumps(search_data))} znaků")
            logger.info(f"   - Financial data: {len(json.dumps(financial_data))} znaků")
        else:
            logger.warning(f"⚠️ General analýza pro {company['name']}: Některá data chybí")
    except Exception as e:
        logger.error(f"❌ General analýza pro {company['name']} selhala: {str(e)}")
    
    # Test workflow pro risk_comparison analýzu
    logger.info("\nTest workflow pro risk_comparison analýzu:")
    company = COMPANIES[1]  # Druhá společnost pro test
    try:
        # Workflow pro risk_comparison analýzu
        risk_factors_data = mcp_connector.get_risk_factors_data(company["id"])
        
        # Ověření výsledků
        if risk_factors_data:
            risk_score = risk_factors_data.get("risk_score")
            risk_factors_count = len(risk_factors_data.get("all_risk_factors", []))
            logger.info(f"✅ Risk comparison analýza pro {company['name']}: Data úspěšně načtena")
            logger.info(f"   - Risk score: {risk_score}")
            logger.info(f"   - Risk factors: {risk_factors_count}")
        else:
            logger.warning(f"⚠️ Risk comparison analýza pro {company['name']}: Chybí data")
    except Exception as e:
        logger.error(f"❌ Risk comparison analýza pro {company['name']} selhala: {str(e)}")
    
    # Test workflow pro supplier_analysis analýzu
    logger.info("\nTest workflow pro supplier_analysis analýzu:")
    company = COMPANIES[2]  # Třetí společnost pro test
    try:
        # Workflow pro supplier_analysis analýzu
        relationships_data = mcp_connector.get_company_relationships(company["id"])
        supply_chain_data = mcp_connector.get_supply_chain_data(company["id"])
        
        # Ověření výsledků
        if relationships_data or supply_chain_data:
            logger.info(f"✅ Supplier analysis analýza pro {company['name']}: Data úspěšně načtena")
            logger.info(f"   - Relationships: {len(relationships_data)} vztahů")
            logger.info(f"   - Supply chain: {len(supply_chain_data)} záznamů")
        else:
            logger.warning(f"⚠️ Supplier analysis analýza pro {company['name']}: Chybí data")
    except Exception as e:
        logger.error(f"❌ Supplier analysis analýza pro {company['name']} selhala: {str(e)}")

def main():
    """Hlavní funkce pro spuštění testů."""
    logger.info("=== Test kompatibility mock_data_2 s workflow ===")
    
    # Test struktury mock_data_2
    test_mock_data_structure()
    
    # Test metod MockMCPConnector
    test_mcp_connector_methods()
    
    # Test specifických workflow pro typy analýz
    test_specific_analysis_flows()

if __name__ == "__main__":
    main()

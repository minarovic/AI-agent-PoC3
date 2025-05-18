#!/usr/bin/env python3
"""
Test script pro ověření funkčnosti MockMCPConnector s novými mock_data_2.
"""

import os
import sys
import json
import logging

# Přidání kořenového adresáře projektu do sys.path pro správné importy
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.memory_agent.tools import MockMCPConnector, CompanyQueryParams

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_connector():
    """Otestuje základní funkčnost MockMCPConnector s novými daty."""
    connector = MockMCPConnector()
    logger.info(f"Inicializován connector s cestou: {connector.data_path}")
    
    # Test 1: Vyhledání společnosti podle názvu
    logger.info("TEST 1: Vyhledání společnosti podle názvu")
    try:
        mb_tool = connector.get_company_by_name("MB TOOL")
        logger.info(f"Nalezena společnost MB TOOL s ID: {mb_tool.get('id')}")
        logger.info(f"Label: {mb_tool.get('label')}")
        logger.info(f"Země: {mb_tool.get('countries')}")
        assert mb_tool.get('id') == "entity_1001", "Nesprávné ID pro MB TOOL"
    except Exception as e:
        logger.error(f"Test 1 selhal: {e}")
    
    # Test 2: Vyhledání společnosti podle ID
    logger.info("\nTEST 2: Vyhledání společnosti podle ID")
    try:
        adis = connector.get_company_by_id("entity_1004")
        logger.info(f"Nalezena společnost s ID entity_1004: {adis.get('label')}")
        assert adis.get('label') == "ADIS TACHOV, zp", "Nesprávný název pro ADIS TACHOV"
    except Exception as e:
        logger.error(f"Test 2 selhal: {e}")
    
    # Test 3: Vyhledání společností podle parametrů
    logger.info("\nTEST 3: Vyhledání společností podle parametrů")
    try:
        params = CompanyQueryParams(country="CZE")
        czech_companies = connector.search_companies(params)
        logger.info(f"Nalezeno {len(czech_companies)} českých společností")
        for company in czech_companies:
            logger.info(f"- {company.get('label')} (ID: {company.get('id')})")
    except Exception as e:
        logger.error(f"Test 3 selhal: {e}")
    
    # Test 4: Získání vztahů společnosti
    logger.info("\nTEST 4: Získání vztahů společnosti")
    try:
        relationships = connector.get_company_relationships("entity_1001")  # MB TOOL
        logger.info(f"Nalezeno {len(relationships)} vztahů pro MB TOOL")
        
        # Vypsání několika vztahů
        for i, rel in enumerate(relationships[:3]):  # Jen prvních 3 vztahy
            source = rel.get('source', {}).get('label', 'Unknown')
            target = rel.get('target', {}).get('label', 'Unknown')
            rel_type = rel.get('type', 'Unknown')
            logger.info(f"- Vztah {i+1}: {source} {rel_type} {target}")
    except Exception as e:
        logger.error(f"Test 4 selhal: {e}")
    
    # Test 5: Získání finančních dat společnosti
    logger.info("\nTEST 5: Získání finančních dat společnosti")
    try:
        financials = connector.get_company_financials("entity_1001")  # MB TOOL
        logger.info(f"Získána finanční data pro MB TOOL:")
        if isinstance(financials, dict):
            # Vypsat klíče nebo některé hodnoty
            logger.info(f"Dostupná finanční data: {list(financials.keys())}")
        else:
            logger.info(f"Finanční data: {financials}")
    except Exception as e:
        logger.error(f"Test 5 selhal: {e}")

if __name__ == "__main__":
    logger.info("Spouštím test MockMCPConnector s novými mock_data_2")
    test_connector()
    logger.info("Testy dokončeny")

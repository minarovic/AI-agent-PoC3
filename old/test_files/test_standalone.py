#!/usr/bin/env python3
"""
Standalone testovací skript pro ověření přístupu k mock_data_2.
"""

import os
import json
import glob
import logging
from pathlib import Path

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_mock_data():
    """Testuje přístup k novým mock_data_2 souborům."""
    # Cesta k mock datům
    mock_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_data_2")
    logger.info(f"Testuji data v: {mock_data_path}")
    
    if not os.path.exists(mock_data_path):
        logger.error(f"Adresář {mock_data_path} neexistuje!")
        return
    
    # 1. Test: Výpis všech souborů
    logger.info("==== VÝPIS DOSTUPNÝCH SOUBORŮ ====")
    files = glob.glob(os.path.join(mock_data_path, "*.json"))
    logger.info(f"Nalezeno {len(files)} JSON souborů")
    for file in files:
        logger.info(f"- {os.path.basename(file)}")
    
    # 2. Test: Načtení entity_detail souborů pro Tier 1 společnosti
    logger.info("\n==== TIER 1 SPOLEČNOSTI ====")
    tier1_companies = {}
    
    for file_path in glob.glob(os.path.join(mock_data_path, "entity_detail_*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("id", "").startswith("entity_100"):  # Tier 1 IDčka podle README
                    company_id = data.get("id")
                    company_name = data.get("label", "Unknown")
                    tier1_companies[company_id] = company_name
                    logger.info(f"Nalezena Tier 1 společnost: {company_name} (ID: {company_id})")
        except Exception as e:
            logger.error(f"Chyba při zpracování souboru {file_path}: {e}")
    
    # 3. Test: Kontrola vztahů pro MB TOOL
    logger.info("\n==== VZTAHY PRO MB TOOL ====")
    if "entity_1001" in tier1_companies:
        mb_tool_relationships = []
        for file_path in glob.glob(os.path.join(mock_data_path, "relationships_*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "data" in data and isinstance(data["data"], list):
                        for rel in data["data"]:
                            source = rel.get("source", {})
                            target = rel.get("target", {})
                            
                            if source.get("id") == "entity_1001" or target.get("id") == "entity_1001":
                                mb_tool_relationships.append(rel)
            except Exception as e:
                logger.error(f"Chyba při zpracování souboru {file_path}: {e}")
        
        logger.info(f"Nalezeno {len(mb_tool_relationships)} vztahů pro MB TOOL")
        
        # Výpis prvních 3 dodavatelů
        suppliers = []
        for rel in mb_tool_relationships:
            if rel.get("type") == "has_supplier" and rel.get("source", {}).get("id") == "entity_1001":
                suppliers.append(rel.get("target", {}).get("label", "Unknown"))
        
        logger.info(f"MB TOOL má {len(suppliers)} dodavatelů, například:")
        for i, supplier in enumerate(suppliers[:3]):
            logger.info(f"- {supplier}")
    
    # 4. Test: Kontrola interních dat
    logger.info("\n==== INTERNÍ DATA ====")
    for file_path in glob.glob(os.path.join(mock_data_path, "internal_*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                company_name = data.get("supplier_name", "Unknown")
                duns = data.get("duns_number", "Unknown")
                tier = data.get("primary_tier", "Unknown")
                logger.info(f"Interní data pro: {company_name} (DUNS: {duns}, Tier: {tier})")
        except Exception as e:
            logger.error(f"Chyba při zpracování souboru {file_path}: {e}")

if __name__ == "__main__":
    logger.info("Spouštím test přístupu k mock_data_2")
    test_mock_data()
    logger.info("Testy dokončeny")

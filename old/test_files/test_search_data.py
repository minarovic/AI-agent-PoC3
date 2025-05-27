#!/usr/bin/env python3
"""
Test pro ověření funkčnosti get_company_search_data metody v MockMCPConnector.
"""

import os
import sys
import json
import logging
import glob
import re
from typing import Dict, Any, Optional, List, ClassVar
from pathlib import Path

# Pro unidecode je potřeba instalace: pip install unidecode
try:
    from unidecode import unidecode
except ImportError:
    # Jednoduchá náhrada, pokud unidecode není k dispozici
    def unidecode(text):
        return text

# Nastavení cesty k mock datům
MOCK_DATA_PATH = "./mock_data_2"

# Třídy výjimek - kopie z memory_agent.tools pro standalone test
class MockMCPConnectorError(Exception):
    """Základní výjimka pro chyby MCP Connectoru."""
    pass

class ConnectionError(MockMCPConnectorError):
    """Výjimka vyvolaná při chybě připojení k MCP."""
    pass

class DataFormatError(MockMCPConnectorError):
    """Výjimka vyvolaná při chybě formátu dat z MCP."""
    pass

class EntityNotFoundError(MockMCPConnectorError):
    """Výjimka vyvolaná, když entita není nalezena v MCP."""
    pass

class MockMCPConnector:
    """
    Zjednodušená verze MockMCPConnector pro účely testování get_company_search_data.
    """
    MOCK_DATA_PATH = MOCK_DATA_PATH
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or self.MOCK_DATA_PATH
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            raise DataFormatError(f"Soubor {file_path} není validní JSON")
        except FileNotFoundError:
            raise ConnectionError(f"Soubor {file_path} nebyl nalezen")
        except Exception as e:
            raise ConnectionError(f"Nelze načíst soubor {file_path}: {str(e)}")

    def _normalize_name(self, name: str) -> str:
        normalized = unidecode(name).lower()
        normalized = re.sub(r'[^a-z0-9]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _fuzzy_name_match(self, name1: str, name2: str) -> bool:
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        return (norm1 in norm2) or (norm2 in norm1)

    def get_company_by_name(self, name: str) -> Dict[str, Any]:
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
            try:
                company_data = self._load_json_file(file_path)
                company_name = company_data.get("label", "")
                
                if self._fuzzy_name_match(name, company_name):
                    return company_data
            except Exception as e:
                continue
        
        raise EntityNotFoundError(f"Společnost s názvem '{name}' nebyla nalezena")
        
    def get_company_search_data(self, company_id: str) -> Dict[str, Any]:
        """
        Získá základní data společnosti z entity_search JSON souborů.
        
        Args:
            company_id: ID společnosti
            
        Returns:
            Dict[str, Any]: Základní data společnosti
            
        Raises:
            EntityNotFoundError: Pokud společnost nebyla nalezena
        """
        # Nejprve se pokusíme získat název společnosti z ID pro lepší vyhledávání
        company_name = None
        company_detail = None
        
        try:
            # Zkusíme najít detail společnosti podle ID
            for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
                try:
                    detail_data = self._load_json_file(file_path)
                    if detail_data.get("id") == company_id:
                        company_detail = detail_data
                        company_name = detail_data.get("label", "").split(" ")[0].lower()  # První část názvu pro hledání souboru
                        break
                except Exception as e:
                    continue
        except Exception as e:
            pass
        
        # Hledání specifického souboru entity_search pro společnost
        search_files = []
        
        if company_name:
            # Hledáme specifické soubory podle názvu společnosti
            for file_path in glob.glob(os.path.join(self.data_path, f"entity_search_{company_name}*.json")):
                search_files.append(file_path)
        
        # Pokud nemáme specifické soubory, použijeme všechny soubory entity_search
        if not search_files:
            for file_path in glob.glob(os.path.join(self.data_path, "entity_search_*.json")):
                search_files.append(file_path)
        
        # Procházíme nalezené soubory
        for file_path in search_files:
            try:
                search_data = self._load_json_file(file_path)
                
                # V entity_search_*.json jsou data v poli "results"
                if "results" in search_data and isinstance(search_data["results"], list):
                    for entity in search_data["results"]:
                        if entity.get("id") == company_id:
                            return entity
            except Exception as e:
                continue
        
        # Pokud jsme nenašli specifický záznam, zkusíme ještě obecný soubor
        general_path = os.path.join(self.data_path, "entity_search.json")
        if os.path.exists(general_path):
            try:
                general_data = self._load_json_file(general_path)
                if "results" in general_data and isinstance(general_data["results"], list):
                    for entity in general_data["results"]:
                        if entity.get("id") == company_id:
                            return entity
            except Exception as e:
                pass
        
        # Pokud jsme nenašli search data, ale máme detail, vraťme ten jako záložní řešení
        if company_detail:
            return company_detail
            
        raise EntityNotFoundError(f"Základní data pro společnost s ID '{company_id}' nebyla nalezena")

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_search_data():
    """Otestuje funkčnost get_company_search_data v MockMCPConnector."""
    connector = MockMCPConnector(data_path="./mock_data_2")
    logger.info(f"Inicializován connector s cestou: {connector.data_path}")
    
    # Test 1: Získání search dat pro MB TOOL
    logger.info("\nTEST 1: Získání search dat pro MB TOOL")
    try:
        # Nejprve získáme ID společnosti
        mb_tool = connector.get_company_by_name("MB TOOL")
        mb_tool_id = mb_tool.get('id')
        logger.info(f"MB TOOL ID: {mb_tool_id}")
        
        # Nyní získáme search data pomocí ID
        search_data = connector.get_company_search_data(mb_tool_id)
        logger.info(f"Získána search data pro MB TOOL:")
        logger.info(f"Label: {search_data.get('label')}")
        if "identifiers" in search_data:
            logger.info(f"Identifikátory: {[i.get('type') + ': ' + i.get('value') for i in search_data.get('identifiers', [])]}")
        if "countries" in search_data:
            logger.info(f"Země: {search_data.get('countries')}")
    except Exception as e:
        logger.error(f"Test 1 selhal: {e}")
    
    # Test 2: Získání search dat pro ADIS TACHOV
    logger.info("\nTEST 2: Získání search dat pro ADIS TACHOV")
    try:
        # Nejprve získáme ID společnosti
        adis = connector.get_company_by_name("ADIS TACHOV")
        adis_id = adis.get('id')
        logger.info(f"ADIS TACHOV ID: {adis_id}")
        
        # Nyní získáme search data pomocí ID
        search_data = connector.get_company_search_data(adis_id)
        logger.info(f"Získána search data pro ADIS TACHOV:")
        logger.info(f"Label: {search_data.get('label')}")
        if "identifiers" in search_data:
            logger.info(f"Identifikátory: {[i.get('type') + ': ' + i.get('value') for i in search_data.get('identifiers', [])]}")
        if "countries" in search_data:
            logger.info(f"Země: {search_data.get('countries')}")
    except Exception as e:
        logger.error(f"Test 2 selhal: {e}")
    
    # Test 3: Zkouška neexistující společnosti
    logger.info("\nTEST 3: Zkouška neexistující společnosti")
    try:
        # Zkusíme získat search data pro neexistující ID
        search_data = connector.get_company_search_data("nonexistent_id")
        logger.info(f"Neočekávaně získána data pro neexistující společnost: {search_data}")
    except Exception as e:
        logger.info(f"Očekávaná chyba pro neexistující společnost: {e}")

if __name__ == "__main__":
    logger.info("Spouštím test get_company_search_data")
    test_search_data()
    logger.info("Testy dokončeny")

"""Define the agent's tools."""

import logging
import traceback
import uuid
import json
import os
import glob
import asyncio
import warnings
from functools import wraps
from pathlib import Path
from typing import Annotated, Dict, Any, Optional, List, ClassVar, Callable, TypeVar, cast
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, ToolException, BaseTool
from langgraph.store.base import BaseStore

from unidecode import unidecode
import re
import time

logger = logging.getLogger(__name__)

# Vytvoření generického typu pro funkce
F = TypeVar('F', bound=Callable[..., Any])

def deprecated(message: str) -> Callable[[F], F]:
    """
    Označuje funkce nebo třídy jako zastaralé s varováním.
    
    Args:
        message: Zpráva popisující důvod pro zastarání a doporučenou alternativu
    
    Returns:
        Dekorovaná funkce, která při volání vydá varování
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{func.__name__} je zastaralá a bude v budoucnu odstraněna. {message}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator


# Výjimky pro práci s MCP connector
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


# Parametry dotazu pro vyhledávání firem
class CompanyQueryParams(BaseModel):
    """Parametry pro dotazy na firmy."""
    name: Optional[str] = None
    id: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[List[str]] = None


# Třída pro přístup k mock datům
class MockMCPConnector:
    """
    Connector pro přístup k mock datům pro Memory Agent.
    
    Tato třída poskytuje jednotné rozhraní pro přístup k různým typům dat
    (firmy, osoby, vztahy) v simulovaném prostředí Model Context Protocol (MCP).
    """
    
    # Třídní proměnné pro konfiguraci
    MOCK_DATA_PATH: ClassVar[str] = os.environ.get(
        "MOCK_DATA_PATH", 
        str(Path(__file__).parent.parent.parent / "mock_data")
    )
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializuje MockMCPConnector.
        
        Args:
            data_path: Volitelná cesta k mock datům.
                       Pokud není poskytnuta, použije se výchozí cesta.
        """
        self.data_path = data_path or self.MOCK_DATA_PATH
        logger.info(f"Inicializace MockMCPConnector s cestou k datům: {self.data_path}")
        
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Načte a parsuje JSON soubor.
        
        Args:
            file_path: Cesta k JSON souboru
            
        Returns:
            Dict[str, Any]: Parsovaný obsah JSON souboru
            
        Raises:
            DataFormatError: Pokud soubor není validní JSON
            ConnectionError: Pokud soubor nelze načíst
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            logger.error(f"Chyba při parsování JSON souboru: {file_path}")
            raise DataFormatError(f"Soubor {file_path} není validní JSON")
        except FileNotFoundError:
            logger.error(f"Soubor nenalezen: {file_path}")
            raise ConnectionError(f"Soubor {file_path} nebyl nalezen")
        except Exception as e:
            logger.error(f"Chyba při čtení souboru {file_path}: {str(e)}")
            raise ConnectionError(f"Nelze načíst soubor {file_path}: {str(e)}")
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalizuje název pro porovnávání (odstraní diakritiku, převede na malá písmena).
        
        Args:
            name: Název k normalizaci
            
        Returns:
            str: Normalizovaný název
        """
        # Odstranit diakritiku a převést na malá písmena
        normalized = unidecode(name).lower()
        # Odstranit nadbytečné mezery a speciální znaky
        normalized = re.sub(r'[^a-z0-9]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _fuzzy_name_match(self, name1: str, name2: str, threshold: float = 0.8) -> bool:
        """
        Porovná dva názvy s tolerancí (fuzzy matching).
        
        Args:
            name1: První název
            name2: Druhý název
            threshold: Práh podobnosti pro shodu (0-1)
            
        Returns:
            bool: True pokud jsou názvy dostatečně podobné
        """
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Jednoduchá implementace - pokud jeden je podřetězcem druhého
        # V reálném systému by zde byla sofistikovanější metrika
        return (norm1 in norm2) or (norm2 in norm1)
    
    def get_company_by_name(self, name: str) -> Dict[str, Any]:
        """
        Najde společnost podle názvu v mock datech.
        
        Args:
            name: Název společnosti
            
        Returns:
            Dict[str, Any]: Data společnosti
            
        Raises:
            EntityNotFoundError: Pokud společnost nebyla nalezena
        """
        companies_path = os.path.join(self.data_path, "companies")
        if not os.path.isdir(companies_path):
            logger.error(f"Adresář společností neexistuje: {companies_path}")
            raise ConnectionError(f"Adresář společností neexistuje: {companies_path}")
        
        for file_path in glob.glob(os.path.join(companies_path, "*.json")):
            try:
                company_data = self._load_json_file(file_path)
                company_name = company_data.get("name", "")
                
                if self._fuzzy_name_match(name, company_name):
                    logger.info(f"Nalezena společnost: {company_name} (hledáno: {name})")
                    return company_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.error(f"Společnost s názvem '{name}' nebyla nalezena")
        raise EntityNotFoundError(f"Společnost s názvem '{name}' nebyla nalezena")
    
    def get_company_by_id(self, company_id: str) -> Dict[str, Any]:
        """
        Najde společnost podle ID v mock datech.
        
        Args:
            company_id: ID společnosti
            
        Returns:
            Dict[str, Any]: Data společnosti
            
        Raises:
            EntityNotFoundError: Pokud společnost nebyla nalezena
        """
        companies_path = os.path.join(self.data_path, "companies")
        if not os.path.isdir(companies_path):
            logger.error(f"Adresář společností neexistuje: {companies_path}")
            raise ConnectionError(f"Adresář společností neexistuje: {companies_path}")
        
        for file_path in glob.glob(os.path.join(companies_path, "*.json")):
            try:
                company_data = self._load_json_file(file_path)
                if company_data.get("id") == company_id:
                    logger.info(f"Nalezena společnost s ID: {company_id}")
                    return company_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.error(f"Společnost s ID '{company_id}' nebyla nalezena")
        raise EntityNotFoundError(f"Společnost s ID '{company_id}' nebyla nalezena")
    
    def search_companies(self, params: CompanyQueryParams) -> List[Dict[str, Any]]:
        """
        Vyhledá společnosti podle zadaných parametrů.
        
        Args:
            params: Parametry vyhledávání
            
        Returns:
            List[Dict[str, Any]]: Seznam nalezených společností
        """
        companies_path = os.path.join(self.data_path, "companies")
        if not os.path.isdir(companies_path):
            logger.error(f"Adresář společností neexistuje: {companies_path}")
            raise ConnectionError(f"Adresář společností neexistuje: {companies_path}")
        
        results = []
        
        for file_path in glob.glob(os.path.join(companies_path, "*.json")):
            try:
                company_data = self._load_json_file(file_path)
                
                # Kontrola parametrů vyhledávání
                matches = True
                
                if params.id and company_data.get("id") != params.id:
                    matches = False
                
                if params.name and not self._fuzzy_name_match(params.name, company_data.get("name", "")):
                    matches = False
                
                if params.country and company_data.get("country") != params.country:
                    matches = False
                
                if params.industry and company_data.get("industry") not in params.industry:
                    matches = False
                
                if matches:
                    results.append(company_data)
            
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.info(f"Nalezeno {len(results)} společností podle parametrů: {params}")
        return results
    
    def get_company_financials(self, company_id: str) -> Dict[str, Any]:
        """
        Získá finanční data společnosti.
        
        Args:
            company_id: ID společnosti
            
        Returns:
            Dict[str, Any]: Finanční data společnosti
            
        Raises:
            EntityNotFoundError: Pokud finanční data nebyla nalezena
        """
        internal_path = os.path.join(self.data_path, "internal_data", "financials")
        if not os.path.isdir(internal_path):
            logger.error(f"Adresář finančních dat neexistuje: {internal_path}")
            raise ConnectionError(f"Adresář finančních dat neexistuje: {internal_path}")
        
        file_path = os.path.join(internal_path, f"{company_id}.json")
        if os.path.isfile(file_path):
            try:
                return self._load_json_file(file_path)
            except Exception as e:
                logger.error(f"Chyba při načítání finančních dat pro společnost {company_id}: {str(e)}")
                raise DataFormatError(f"Chyba při načítání finančních dat: {str(e)}")
        
        # Fallback na generický soubor, pokud neexistuje specifický
        generic_path = os.path.join(internal_path, "generic_financial_data.json")
        if os.path.isfile(generic_path):
            try:
                data = self._load_json_file(generic_path)
                # Přidáme ID společnosti pro konzistenci
                data["company_id"] = company_id
                return data
            except Exception as e:
                logger.error(f"Chyba při načítání generických finančních dat: {str(e)}")
                raise DataFormatError(f"Chyba při načítání finančních dat: {str(e)}")
        
        logger.error(f"Finanční data pro společnost s ID '{company_id}' nebyla nalezena")
        raise EntityNotFoundError(f"Finanční data pro společnost s ID '{company_id}' nebyla nalezena")
    
    def get_company_relationships(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Získá vztahy společnosti k jiným entitám.
        
        Args:
            company_id: ID společnosti
            
        Returns:
            List[Dict[str, Any]]: Seznam vztahů společnosti
        """
        relationships_path = os.path.join(self.data_path, "relationships")
        if not os.path.isdir(relationships_path):
            logger.error(f"Adresář vztahů neexistuje: {relationships_path}")
            raise ConnectionError(f"Adresář vztahů neexistuje: {relationships_path}")
        
        # Nejprve zkusíme najít specifický soubor pro společnost
        specific_path = os.path.join(relationships_path, f"{company_id}.json")
        if os.path.isfile(specific_path):
            try:
                return self._load_json_file(specific_path)
            except Exception as e:
                logger.error(f"Chyba při načítání vztahů pro společnost {company_id}: {str(e)}")
                raise DataFormatError(f"Chyba při načítání vztahů: {str(e)}")
        
        # Pokud neexistuje specifický soubor, projdeme všechny soubory vztahů
        results = []
        
        for file_path in glob.glob(os.path.join(relationships_path, "*.json")):
            try:
                relationships_data = self._load_json_file(file_path)
                
                if isinstance(relationships_data, list):
                    # Filtrujeme vztahy týkající se dané společnosti
                    for relationship in relationships_data:
                        if (relationship.get("source_id") == company_id or 
                            relationship.get("target_id") == company_id):
                            results.append(relationship)
                elif isinstance(relationships_data, dict):
                    # Pokud je to slovník s klíčem odpovídajícím ID společnosti
                    if company_id in relationships_data:
                        results.extend(relationships_data[company_id])
            
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.info(f"Nalezeno {len(results)} vztahů pro společnost {company_id}")
        return results
    
    def get_person_by_name(self, name: str) -> Dict[str, Any]:
        """
        Najde osobu podle jména v mock datech.
        
        Args:
            name: Jméno osoby
            
        Returns:
            Dict[str, Any]: Data osoby
            
        Raises:
            EntityNotFoundError: Pokud osoba nebyla nalezena
        """
        people_path = os.path.join(self.data_path, "people")
        if not os.path.isdir(people_path):
            logger.error(f"Adresář osob neexistuje: {people_path}")
            raise ConnectionError(f"Adresář osob neexistuje: {people_path}")
        
        for file_path in glob.glob(os.path.join(people_path, "*.json")):
            try:
                person_data = self._load_json_file(file_path)
                person_name = person_data.get("name", "")
                
                if self._fuzzy_name_match(name, person_name):
                    logger.info(f"Nalezena osoba: {person_name} (hledáno: {name})")
                    return person_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.error(f"Osoba s jménem '{name}' nebyla nalezena")
        raise EntityNotFoundError(f"Osoba s jménem '{name}' nebyla nalezena")
    
    def get_person_by_id(self, person_id: str) -> Dict[str, Any]:
        """
        Najde osobu podle ID v mock datech.
        
        Args:
            person_id: ID osoby
            
        Returns:
            Dict[str, Any]: Data osoby
            
        Raises:
            EntityNotFoundError: Pokud osoba nebyla nalezena
        """
        people_path = os.path.join(self.data_path, "people")
        if not os.path.isdir(people_path):
            logger.error(f"Adresář osob neexistuje: {people_path}")
            raise ConnectionError(f"Adresář osob neexistuje: {people_path}")
        
        for file_path in glob.glob(os.path.join(people_path, "*.json")):
            try:
                person_data = self._load_json_file(file_path)
                if person_data.get("id") == person_id:
                    logger.info(f"Nalezena osoba s ID: {person_id}")
                    return person_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.error(f"Osoba s ID '{person_id}' nebyla nalezena")
        raise EntityNotFoundError(f"Osoba s ID '{person_id}' nebyla nalezena")
    
    def get_person_relationships(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Získá vztahy osoby k jiným entitám.
        
        Args:
            person_id: ID osoby
            
        Returns:
            List[Dict[str, Any]]: Seznam vztahů osoby
        """
        # Podobná implementace jako get_company_relationships
        relationships_path = os.path.join(self.data_path, "relationships")
        results = []
        
        if not os.path.isdir(relationships_path):
            logger.error(f"Adresář vztahů neexistuje: {relationships_path}")
            raise ConnectionError(f"Adresář vztahů neexistuje: {relationships_path}")
        
        # Nejprve zkusíme najít specifický soubor pro osobu
        specific_path = os.path.join(relationships_path, f"person_{person_id}.json")
        if os.path.isfile(specific_path):
            try:
                return self._load_json_file(specific_path)
            except Exception as e:
                logger.error(f"Chyba při načítání vztahů pro osobu {person_id}: {str(e)}")
                raise DataFormatError(f"Chyba při načítání vztahů: {str(e)}")
        
        # Pokud neexistuje specifický soubor, projdeme všechny soubory vztahů
        for file_path in glob.glob(os.path.join(relationships_path, "*.json")):
            try:
                relationships_data = self._load_json_file(file_path)
                
                if isinstance(relationships_data, list):
                    # Filtrujeme vztahy týkající se dané osoby
                    for relationship in relationships_data:
                        if (relationship.get("source_id") == person_id or 
                            relationship.get("target_id") == person_id):
                            results.append(relationship)
                elif isinstance(relationships_data, dict):
                    # Pokud je to slovník s klíčem odpovídajícím ID osoby
                    if person_id in relationships_data:
                        results.extend(relationships_data[person_id])
            
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        logger.info(f"Nalezeno {len(results)} vztahů pro osobu {person_id}")
        return results

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
        str(Path(__file__).parent.parent.parent / "mock_data_2")
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
        # Hledáme v souborech entity_detail_*.json
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
            try:
                company_data = self._load_json_file(file_path)
                # V nových datech se používá "label" místo "name"
                company_name = company_data.get("label", "")
                
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
        # Hledáme v souborech entity_detail_*.json
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
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
        results = []
        
        # Nejprve zkontrolujeme soubor entity_search.json, pokud existuje
        entity_search_path = os.path.join(self.data_path, "entity_search.json")
        if os.path.exists(entity_search_path):
            try:
                search_results = self._load_json_file(entity_search_path)
                if "results" in search_results:
                    for company in search_results["results"]:
                        # Kontrola parametrů vyhledávání
                        matches = True
                        
                        if params.id and company.get("id") != params.id:
                            matches = False
                        
                        if params.name and not self._fuzzy_name_match(params.name, company.get("label", "")):
                            matches = False
                        
                        # V nových datech jsou země uloženy v seznamu
                        if params.country:
                            country_match = False
                            if "countries" in company:
                                for country in company["countries"]:
                                    if country.lower() == params.country.lower():
                                        country_match = True
                                        break
                            if not country_match:
                                matches = False
                        
                        # Kontrola průmyslu z detailů společnosti
                        if params.industry and params.industry:
                            # Pro kontrolu průmyslu musíme načíst detailní data
                            try:
                                detail_path = os.path.join(self.data_path, f"entity_detail_{company.get('id')}.json")
                                if os.path.exists(detail_path):
                                    detail_data = self._load_json_file(detail_path)
                                    industry_match = False
                                    if "industry" in detail_data:
                                        for ind in params.industry:
                                            if ind.lower() in detail_data["industry"].lower():
                                                industry_match = True
                                                break
                                    if not industry_match:
                                        matches = False
                            except:
                                # Pokud nelze načíst detaily, předpokládáme neshodu
                                matches = False
                        
                        if matches:
                            results.append(company)
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {entity_search_path}: {str(e)}")
        
        # Pokud není entity_search.json nebo neobsahuje výsledky, procházíme jednotlivé entity_detail_*.json soubory
        if not results:
            for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
                try:
                    company_data = self._load_json_file(file_path)
                    
                    # Kontrola parametrů vyhledávání
                    matches = True
                    
                    if params.id and company_data.get("id") != params.id:
                        matches = False
                    
                    if params.name and not self._fuzzy_name_match(params.name, company_data.get("label", "")):
                        matches = False
                    
                    if params.country and params.country:
                        country_match = False
                        if "countries" in company_data:
                            for country in company_data["countries"]:
                                if country.lower() == params.country.lower():
                                    country_match = True
                                    break
                        if not country_match:
                            matches = False
                    
                    if params.industry and params.industry:
                        industry_match = False
                        if "industry" in company_data:
                            for ind in params.industry:
                                if ind.lower() in company_data["industry"].lower():
                                    industry_match = True
                                    break
                        if not industry_match:
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
        # Nejprve získáme detail společnosti pro získání názvu/labelu
        company_detail = None
        company_name = None
        
        try:
            # Zkusíme najít detail společnosti podle ID
            for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
                detail_data = self._load_json_file(file_path)
                if detail_data.get("id") == company_id:
                    company_detail = detail_data
                    company_name = detail_data.get("label", "").split(" ")[0].lower()  # První část názvu pro hledání souboru
                    break
        except Exception as e:
            logger.warning(f"Nepodařilo se načíst detail společnosti: {str(e)}")
        
        # Pokusíme se najít internal_*.json soubor
        internal_files = []
        
        # Pokud známe název společnosti, zkusíme najít podle něj
        if company_name:
            # Hledáme soubory internal_*.json podle názvu společnosti
            for file_path in glob.glob(os.path.join(self.data_path, f"internal_{company_name}*.json")):
                internal_files.append(file_path)
        
        # Pokud ne, projdeme všechny internal_*.json soubory
        if not internal_files:
            for file_path in glob.glob(os.path.join(self.data_path, "internal_*.json")):
                internal_files.append(file_path)
        
        # Procházíme nalezené soubory a hledáme finanční data
        for file_path in internal_files:
            try:
                internal_data = self._load_json_file(file_path)
                
                # Pokud máme ID společnosti, kontrolujeme shodu
                if "duns_number" in internal_data and company_detail and "identifiers" in company_detail:
                    for identifier in company_detail["identifiers"]:
                        if identifier.get("type") == "duns_number" and identifier.get("value") == internal_data.get("duns_number"):
                            # Našli jsme shodu - vrátíme celá interní data nebo jen finanční část
                            if "financial_data" in internal_data:
                                financial_data = internal_data["financial_data"]
                                financial_data["company_id"] = company_id  # Přidáme ID pro konzistenci
                                return financial_data
                            else:
                                # Pokud neexistuje specifická sekce financial_data, vrátíme celá interní data
                                return internal_data
                
                # Pokud soubor obsahuje financial_data pro dané ID
                if "company_id" in internal_data and internal_data["company_id"] == company_id:
                    if "financial_data" in internal_data:
                        return internal_data["financial_data"]
                    else:
                        return internal_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
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
        results = []
        company_detail = None
        company_name = None
        
        # Nejprve zkusíme získat detail společnosti, abychom měli její název
        try:
            for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
                detail_data = self._load_json_file(file_path)
                if detail_data.get("id") == company_id:
                    company_detail = detail_data
                    company_name = detail_data.get("label", "").split(" ")[0].lower()  # První část názvu pro hledání souboru
                    break
        except Exception as e:
            logger.warning(f"Nepodařilo se načíst detail společnosti: {str(e)}")
        
        # Pokud známe název společnosti, zkusíme najít specifický soubor pro tuto společnost
        relationship_files = []
        
        if company_name:
            # Hledáme specifické soubory vztahů pro společnost
            for file_path in glob.glob(os.path.join(self.data_path, f"relationships_{company_name}*.json")):
                relationship_files.append(file_path)
        
        # Pokud nemáme specifické soubory, použijeme všechny soubory vztahů
        if not relationship_files:
            for file_path in glob.glob(os.path.join(self.data_path, "relationships_*.json")):
                relationship_files.append(file_path)
        
        # Procházíme nalezené soubory vztahů
        for file_path in relationship_files:
            try:
                relationships_data = self._load_json_file(file_path)
                
                # Nová struktura obsahuje "data" pole s jednotlivými vztahy
                if "data" in relationships_data and isinstance(relationships_data["data"], list):
                    for relationship in relationships_data["data"]:
                        # Kontrola, zda tento vztah zahrnuje hledanou společnost
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == company_id or target.get("id") == company_id):
                            results.append(relationship)
                
                # Pro případ, že by struktura byla jiná, zkontrolujeme i "relationships" pole
                elif "relationships" in relationships_data and isinstance(relationships_data["relationships"], list):
                    for relationship in relationships_data["relationships"]:
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == company_id or target.get("id") == company_id):
                            results.append(relationship)
                
                # Starší formát bez vnořené struktury
                elif isinstance(relationships_data, list):
                    for relationship in relationships_data:
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == company_id or target.get("id") == company_id):
                            results.append(relationship)
            
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        # Pokud jsme nenašli žádné vztahy, zkusíme ještě obecný soubor relationships.json
        if not results:
            general_path = os.path.join(self.data_path, "relationships.json")
            if os.path.exists(general_path):
                try:
                    general_data = self._load_json_file(general_path)
                    
                    if "data" in general_data and isinstance(general_data["data"], list):
                        for relationship in general_data["data"]:
                            source = relationship.get("source", {})
                            target = relationship.get("target", {})
                            
                            if (source.get("id") == company_id or target.get("id") == company_id):
                                results.append(relationship)
                except Exception as e:
                    logger.warning(f"Chyba při zpracování obecného souboru vztahů: {str(e)}")
        
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
        # V nové struktuře dat mohou být osoby v souborech entity_detail_person_*.json nebo přímo v entity_detail_*.json
        # s typem "person"
        
        # Nejprve zkusíme najít specifické soubory pro osoby
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_person_*.json")):
            try:
                person_data = self._load_json_file(file_path)
                person_name = person_data.get("label", "")
                
                if self._fuzzy_name_match(name, person_name):
                    logger.info(f"Nalezena osoba: {person_name} (hledáno: {name})")
                    return person_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
                
        # Pokud nenajdeme specifické soubory, projdeme všechny entity_detail soubory
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
            try:
                entity_data = self._load_json_file(file_path)
                # Kontrola, zda jde o osobu
                if entity_data.get("type") == "person":
                    person_name = entity_data.get("label", "")
                    
                    if self._fuzzy_name_match(name, person_name):
                        logger.info(f"Nalezena osoba: {person_name} (hledáno: {name})")
                        return entity_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        # Pro zpětnou kompatibilitu zkontrolujeme i původní adresář people, pokud existuje
        people_path = os.path.join(self.data_path, "people")
        if os.path.isdir(people_path):
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
        # V nové struktuře dat mohou být osoby v souborech entity_detail_person_*.json nebo přímo v entity_detail_*.json
        # s typem "person"
        
        # Nejprve zkusíme najít specifické soubory pro osoby
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_person_*.json")):
            try:
                person_data = self._load_json_file(file_path)
                if person_data.get("id") == person_id:
                    logger.info(f"Nalezena osoba s ID: {person_id}")
                    return person_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
                
        # Pokud nenajdeme specifické soubory, projdeme všechny entity_detail soubory
        for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
            try:
                entity_data = self._load_json_file(file_path)
                # Kontrola, zda jde o osobu a ID se shoduje
                if entity_data.get("type") == "person" and entity_data.get("id") == person_id:
                    logger.info(f"Nalezena osoba s ID: {person_id}")
                    return entity_data
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        # Pro zpětnou kompatibilitu zkontrolujeme i původní adresář people, pokud existuje
        people_path = os.path.join(self.data_path, "people")
        if os.path.isdir(people_path):
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
        # Implementace podobná metodě get_company_relationships s úpravou pro osoby
        results = []
        person_detail = None
        person_name = None
        
        # Nejprve zkusíme získat detail osoby, abychom měli její jméno
        try:
            # Hledat v entity_detail souborech
            for file_path in glob.glob(os.path.join(self.data_path, "entity_detail_*.json")):
                detail_data = self._load_json_file(file_path)
                if detail_data.get("id") == person_id:
                    person_detail = detail_data
                    person_name = detail_data.get("label", "").split(" ")[0].lower()  # První část jména pro hledání souborů
                    break
        except Exception as e:
            logger.warning(f"Nepodařilo se načíst detail osoby: {str(e)}")
        
        # Procházíme soubory relationships_*.json a hledáme vztahy zahrnující osobu
        for file_path in glob.glob(os.path.join(self.data_path, "relationships_*.json")):
            try:
                relationships_data = self._load_json_file(file_path)
                
                # Kontrola různých formátů dat vztahů
                
                # Formát s polem "data"
                if "data" in relationships_data and isinstance(relationships_data["data"], list):
                    for relationship in relationships_data["data"]:
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == person_id or target.get("id") == person_id):
                            results.append(relationship)
                
                # Formát s polem "relationships"
                elif "relationships" in relationships_data and isinstance(relationships_data["relationships"], list):
                    for relationship in relationships_data["relationships"]:
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == person_id or target.get("id") == person_id):
                            results.append(relationship)
                
                # Starší formát - přímo seznam vztahů
                elif isinstance(relationships_data, list):
                    for relationship in relationships_data:
                        source = relationship.get("source", {})
                        target = relationship.get("target", {})
                        
                        if (source.get("id") == person_id or target.get("id") == person_id):
                            results.append(relationship)
            
            except Exception as e:
                logger.warning(f"Chyba při zpracování souboru {file_path}: {str(e)}")
                continue
        
        # Pokud jsme nenašli žádné vztahy, zkusíme ještě obecný soubor relationships.json
        if not results:
            general_path = os.path.join(self.data_path, "relationships.json")
            if os.path.exists(general_path):
                try:
                    general_data = self._load_json_file(general_path)
                    
                    if "data" in general_data and isinstance(general_data["data"], list):
                        for relationship in general_data["data"]:
                            source = relationship.get("source", {})
                            target = relationship.get("target", {})
                            
                            if (source.get("id") == person_id or target.get("id") == person_id):
                                results.append(relationship)
                except Exception as e:
                    logger.warning(f"Chyba při zpracování obecného souboru vztahů: {str(e)}")
        
        # Pro zpětnou kompatibilitu zkontrolujeme i původní adresář relationships, pokud existuje
        relationships_path = os.path.join(self.data_path, "relationships")
        if os.path.isdir(relationships_path):
            # Nejprve zkusíme najít specifický soubor pro osobu
            specific_path = os.path.join(relationships_path, f"person_{person_id}.json")
            if os.path.isfile(specific_path):
                try:
                    relationships_data = self._load_json_file(specific_path)
                    
                    # Podle formátu dat je přidáme do výsledků
                    if isinstance(relationships_data, list):
                        results.extend(relationships_data)
                    elif isinstance(relationships_data, dict) and "relationships" in relationships_data:
                        results.extend(relationships_data["relationships"])
                except Exception as e:
                    logger.warning(f"Chyba při zpracování specifického souboru vztahů: {str(e)}")
        
        logger.info(f"Nalezeno {len(results)} vztahů pro osobu {person_id}")
        return results

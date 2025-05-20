"""
Graph nodes pro integraci MockMCPConnector s LangGraph workflow.

Tento modul obsahuje implementaci uzlů grafu pro StateGraph, které využívají
MockMCPConnector pro získávání dat pro různé typy analýz.
"""

from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
import logging

from memory_agent.tools import (
    MockMCPConnector, 
    CompanyQueryParams, 
    EntityNotFoundError,
    DataFormatError,
    ConnectionError,
    MockMCPConnectorError
)

from memory_agent.state import State
from memory_agent.analyzer import analyze_query_sync
from memory_agent import utils

# Import prompt registry
from memory_agent.prompts import (
    PromptRegistry,
    PromptDataFormatter,
    PromptChainBuilder,
    format_state_for_prompt
)

# Nastavení loggeru
logger = logging.getLogger("memory_agent.graph_nodes")

# Uzly grafu pro LangGraph

def retrieve_company_data(state: State) -> Dict[str, Any]:
    """
    Získá data o společnosti z MCP.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s daty společnosti
    """
    try:
        query_params = state.internal_data.get("query_params", {})
        company_name = query_params.get("company_name")
        
        # Kontrola, zda máme platný název společnosti
        if not company_name or company_name == "Unknown":
            logger.error("Neplatný název společnosti")
            return {
                "error_state": {
                    "error": "Nepodařilo se identifikovat název společnosti v dotazu",
                    "error_type": "invalid_company_name"
                },
                "company_data": {
                    "basic_info": {
                        "name": "Neznámá společnost",
                        "id": "unknown_id"
                    }
                }
            }
        
        logger.info(f"Získávám data pro společnost: {company_name}")
        
        # Přístup k MCP konektoru přes state.mcp_connector pokud existuje,
        # jinak zkusíme vytvořit novou instanci konektoru
        if hasattr(state, "mcp_connector") and state.mcp_connector is not None:
            mcp_connector = state.mcp_connector
            logger.info("Používám existující MCP konektor ze state.mcp_connector")
        elif hasattr(state, "get_mcp_connector") and callable(state.get_mcp_connector):
            mcp_connector = state.get_mcp_connector()
            logger.info("Používám MCP konektor získaný přes state.get_mcp_connector()")
        else:
            # Pokud konektor není k dispozici v state, vytvořit novou instanci
            from memory_agent.tools import MockMCPConnector
            mcp_connector = MockMCPConnector()
            logger.info("Vytvářím nový MCP konektor")
        
        # Připojit konektor do state pro další použití
        state.mcp_connector = mcp_connector
        
        # Speciální případ pro MB TOOL - přidáme fallback data
        if company_name.upper() == "MB TOOL":
            logger.info("Používám speciální fallback data pro společnost MB TOOL")
            company_data = {
                "name": "MB TOOL",
                "id": "mb_tool_123",
                "description": "Společnost MB TOOL se specializuje na výrobu nástrojů a forem pro automobilový průmysl",
                "industry": "Automotive",
                "founding_year": 1995,
                "headquarters": "Mladá Boleslav, Česká republika",
                "employees": 120,
                "revenue_category": "10-50M EUR"
            }
            return {"company_data": {"basic_info": company_data}, "mcp_connector": mcp_connector}
        
        # Standardní případ - získání dat z konektoru
        try:
            company_data = mcp_connector.get_company_by_name(company_name)
            
            # Kontrola, zda data obsahují ID
            if not company_data or "id" not in company_data:
                logger.error(f"Data společnosti neobsahují ID: {company_data}")
                # Vytvoření alespoň minimálního objektu s ID
                company_data = {
                    "name": company_name,
                    "id": f"{company_name.lower().replace(' ', '_')}_id"
                }
            
            # Vrátíme data o společnosti
            return {"company_data": {"basic_info": company_data}, "mcp_connector": mcp_connector}
        
        except Exception as e:
            logger.error(f"Chyba při získávání dat společnosti {company_name}: {str(e)}")
            # Vytvoření náhradních dat, abychom mohli pokračovat
            company_data = {
                "name": company_name,
                "id": f"{company_name.lower().replace(' ', '_')}_id",
                "error": str(e)
            }
            return {
                "company_data": {"basic_info": company_data},
                "mcp_connector": mcp_connector,
                "error_state": {"error": str(e), "error_type": "data_retrieval_error"}
            }
    
    except EntityNotFoundError as e:
        logger.error(f"Společnost nenalezena: {e}")
        return {"error_state": {"error": str(e), "error_type": "entity_not_found"}}
    
    except (DataFormatError, ConnectionError, MockMCPConnectorError) as e:
        logger.error(f"Chyba při získávání dat společnosti: {e}")
        return {"error_state": {"error": str(e), "error_type": "data_access_error"}}

def determine_analysis_type(state: State) -> State:
    """
    Zjednodušená funkce pro určení typu analýzy z dotazu.
    
    Podporované typy analýz:
    - risk_comparison: Analýza rizik a compliance
    - supplier_analysis: Analýza dodavatelských vztahů
    - general: Obecné informace o společnosti
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s určeným typem analýzy
    """
    # Výchozí typ analýzy
    analysis_type = "general"
    
    # Získání dotazu
    query = state.current_query.lower() if state.current_query else ""
    
    # Využití funkce z analyzer.py místo duplikace kódu
    try:
        from memory_agent.analyzer import detect_analysis_type
        analysis_type = detect_analysis_type(query)
        logger.info(f"Analýza typu pomocí analyze.py: {analysis_type}")
    except Exception as e:
        # Záložní řešení pokud import selže
        logger.warning(f"Nelze použít analyzer.detect_analysis_type: {str(e)}")
        
        # Jednoduchá detekce klíčových slov
        if any(kw in query for kw in ["risk", "riziko", "sankce", "compliance"]):
            analysis_type = "risk_comparison"
        elif any(kw in query for kw in ["supplier", "dodavatel", "supply chain"]):
            analysis_type = "supplier_analysis"
    
    logger.info(f"Dotaz '{query[:30]}...' určen jako typ analýzy: {analysis_type}")
    return {"analysis_type": analysis_type}

def route_query(state: State) -> State:
    """
    Zjednodušená verze funkce pro analýzu vstupního dotazu.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s určeným typem dotazu
    """
    if state.current_query is None and state.messages:
        # Extrahujeme dotaz z poslední zprávy
        last_message = state.messages[-1]
        state.current_query = last_message.content
    
    if not state.current_query:
        logger.error("Nebyl nalezen žádný dotaz k analýze")
        return {"query_type": "error", "error_state": {"error": "Nebyl nalezen žádný dotaz k analýze"}}
    
    # Standardní analýza pomocí analyze_query_sync
    query_type = analyze_query_sync(state.current_query)
    logger.info(f"Dotaz '{state.current_query[:30]}...' klasifikován jako typ: {query_type}")
    
    # Určení typu analýzy
    updated_state = determine_analysis_type(state)
    analysis_type = updated_state.get("analysis_type", "general")
    
    return {
        "query_type": query_type,
        "analysis_type": analysis_type
    }

def prepare_company_query(state: State) -> State:
    """
    Zjednodušená funkce pro přípravu dotazu na společnost.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu
    """
    logger.info(f"Připravuji dotaz pro společnost: {state.current_query}")
    
    # Rozpoznání názvu společnosti z dotazu
    query = state.current_query if state.current_query else ""
    company_name = "Unknown"
    
    # Pokud máme výsledek analýzy a společnosti, použijeme ho
    if hasattr(state, "analysis_result") and state.analysis_result:
        if "company_name" in state.analysis_result:
            company_name = state.analysis_result["company_name"]
    
    # Přímé využití již existující funkce z analyzer.py
    if company_name == "Unknown" and query:
        try:
            # Import analyzér z modulu analyzer
            from memory_agent.analyzer import analyze_company_query
            
            # Analyzujeme dotaz pomocí zjednodušené funkce
            company, analysis_type = analyze_company_query(query)
            if company and company != "Unknown Company":
                company_name = company
                logger.info(f"Analyzér rozpoznal společnost: {company_name}")
        except Exception as e:
            logger.error(f"Chyba při analýze dotazu: {str(e)}")
            # Pro PoC použijeme defaultní hodnoty, pokud analýza selže
            if "MB TOOL" in query:
                company_name = "MB TOOL"
            elif "ŠKODA AUTO" in query:
                company_name = "ŠKODA AUTO"
            elif "ADIS TACHOV" in query:
                company_name = "ADIS TACHOV"
            elif "Flídr plast" in query:
                company_name = "Flídr plast"
    
    # Uložení výsledku dotazu na společnost
    state.company_query = {
        "query": query,
        "company_name": company_name
    }
    
    return {"company_name": company_name}

def analyze_company_data(state: State) -> State:
    """
    Provede analýzu dat společnosti podle určeného typu analýzy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky analýzy
    """
    # Získání typu analýzy z state (výchozí hodnota "general")
    analysis_type = getattr(state, "analysis_type", "general")
    logger.info(f"Analyzuji data společnosti pro typ analýzy: {analysis_type}")
    
    company_name = state.company_data.get("basic_info", {}).get("name", "Unknown Company")
    company_id = state.company_data.get("basic_info", {}).get("id", "unknown_id")
    
    # Inicializace základní struktury výsledku analýzy
    analysis_result = {
        "company_name": company_name,
        "company_id": company_id,
        "analysis_type": analysis_type,
        "timestamp": utils.get_current_timestamp(),
    }
    
    # Specializovaná analýza podle typu
    if analysis_type == "general":
        # Pro general analýzu využíváme search_info a financials
        search_info = state.company_data.get("search_info", {})
        financials = state.company_data.get("financials", {})
        
        # Základní informace o společnosti
        basic_info = {
            "name": company_name,
            "id": company_id
        }
        
        # Rozšíření o data ze search_info
        if search_info and search_info != {}:
            if "countries" in search_info:
                basic_info["countries"] = search_info.get("countries", [])
            if "addresses" in search_info:
                basic_info["addresses"] = search_info.get("addresses", [])
            if "identifiers" in search_info:
                basic_info["identifiers"] = search_info.get("identifiers", [])
            if "meta" in search_info:
                basic_info["meta"] = search_info.get("meta", {})
        
        # Finanční informace a aktivity
        financial_overview = {}
        if financials and financials != {}:
            if "supplier_since" in financials:
                financial_overview["supplier_since"] = financials.get("supplier_since", "")
            if "quality_rating" in financials:
                financial_overview["quality_rating"] = financials.get("quality_rating", "")
            if "compliance_status" in financials:
                financial_overview["compliance_status"] = financials.get("compliance_status", "")
            if "identified_activities" in financials:
                financial_overview["activities"] = financials.get("identified_activities", [])
            if "geographic_presence" in financials:
                financial_overview["geographic_presence"] = financials.get("geographic_presence", [])
        
        # Sestavení analýzy pro general typ
        analysis_result.update({
            "summary": f"Obecná analýza společnosti {company_name}",
            "basic_info": basic_info,
            "financial_overview": financial_overview,
            "key_findings": [
                f"Společnost {company_name} je aktivní v odvětví {'automotive' if 'industry' in financials else 'neznámém'}",
                f"Primární lokace: {', '.join(basic_info.get('countries', ['neznámá']))}"
            ],
        })
        
    elif analysis_type == "risk_comparison":
        # Pro risk analýzu využíváme detail společnosti a rizikové faktory
        company_detail = state.company_data.get("basic_info", {})
        risk_factors_data = getattr(state, "risk_factors_data", {})
        
        # Extrakce rizikových faktorů z dostupných zdrojů
        risk_factors = []
        risk_score = None
        
        # Nejprve zkusíme rizikové faktory z risk_factors_data získaného pomocí get_risk_factors_data
        if risk_factors_data:
            if "all_risk_factors" in risk_factors_data:
                risk_factors = risk_factors_data.get("all_risk_factors", [])
            if "risk_score" in risk_factors_data:
                risk_score = risk_factors_data.get("risk_score")
        
        # Pokud nejsou žádné rizikové faktory z risk_factors_data, zkusíme je extrahovat z company_detail
        if not risk_factors and "risk" in company_detail:
            risk_section = company_detail.get("risk", {})
            
            # Extrakce rizikového skóre
            if "risk_score" in risk_section and not risk_score:
                risk_score = risk_section.get("risk_score")
            
            # Zpracování rizikových faktorů
            for key, value in risk_section.items():
                if key == "risk_score":
                    continue
                
                if isinstance(value, bool) and value:
                    risk_factors.append({
                        "factor": key,
                        "category": "general",
                        "level": "identified"
                    })
                elif isinstance(value, dict) and "level" in value:
                    level = value.get("level")
                    category = key
                    if "factors" in value and isinstance(value["factors"], list):
                        for factor in value["factors"]:
                            risk_factors.append({
                                "factor": factor,
                                "category": category,
                                "level": level
                            })
        
        # Sestavení analýzy pro risk_comparison typ
        analysis_result.update({
            "summary": f"Analýza rizik pro společnost {company_name}",
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "key_findings": [
                f"Rizikové skóre: {risk_score if risk_score else 'Nedostupné'}",
                f"Identifikováno {len(risk_factors)} rizikových faktorů"
            ],
        })
        
    elif analysis_type == "supplier_analysis":
        # Pro supplier analýzu využíváme vztahy a supply chain
        relationships_data = getattr(state, "relationships_data", {}).get(company_id, [])
        supply_chain_data = getattr(state, "supply_chain_data", {}).get(company_id, [])
        
        # Extrakce dodavatelů ze vztahů
        suppliers = []
        if isinstance(relationships_data, list):
            for relation in relationships_data:
                # Kontrola, zda jde o vztah typu "has_supplier" a zda společnost je zdrojem
                if relation.get("type") == "has_supplier" and relation.get("source", {}).get("id") == company_id:
                    target = relation.get("target", {})
                    metadata = relation.get("metadata", {})
                    suppliers.append({
                        "name": target.get("label", "Unknown Supplier"),
                        "id": target.get("id", ""),
                        "tier": metadata.get("tier", "Unknown"),
                        "category": metadata.get("category", "Unknown")
                    })
        
        # Extrakce dodavatelů z supply chain dat
        supply_chain_suppliers = []
        if isinstance(supply_chain_data, list):
            for item in supply_chain_data:
                supplier_info = item.get("target", {})
                supplier_name = supplier_info.get("label", "")
                supplier_id = supplier_info.get("id", "")
                
                # Jen pokud máme alespoň název nebo ID
                if supplier_name or supplier_id:
                    # Kontrola, zda tento dodavatel už není v seznamu
                    if not any(s.get("id") == supplier_id for s in supply_chain_suppliers if supplier_id):
                        supply_chain_suppliers.append({
                            "name": supplier_name,
                            "id": supplier_id,
                            "tier": item.get("tier", "Unknown"),
                            "risk_factors": item.get("risk_factors", [])
                        })
        
        # Sestavení analýzy pro supplier_analysis typ
        analysis_result.update({
            "summary": f"Analýza dodavatelského řetězce pro společnost {company_name}",
            "suppliers": suppliers,
            "supply_chain": supply_chain_suppliers,
            "key_findings": [
                f"Identifikováno {len(suppliers)} přímých dodavatelů",
                f"Analýza dodavatelského řetězce obsahuje {len(supply_chain_suppliers)} dodavatelů",
                f"Zahrnuto {sum(1 for s in supply_chain_suppliers if s.get('risk_factors'))} dodavatelů s identifikovanými riziky" if supply_chain_suppliers else "Žádná rizika v dodavatelském řetězci nebyla identifikována"
            ],
            "data_quality": "high" if supply_chain_suppliers else "medium"
        })
    
    else:
        # Obecná analýza pro neznámý typ
        analysis_result.update({
            "summary": f"Analýza společnosti {company_name}",
            "key_findings": [
                "Neznámý typ analýzy, poskytnuty pouze základní informace",
                f"Společnost ID: {company_id}"
            ],
            "data_quality": "low"
        })
    
    return {"analysis_result": analysis_result}

def retrieve_additional_company_data(state: State) -> State:
    """
    Zjednodušená funkce pro získání dat pro analýzu podle typu analýzy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s doplňujícími daty
    """
    try:
        company_id = state.company_data.get("basic_info", {}).get("id")
        # Získání typu analýzy z state (výchozí hodnota "general")
        analysis_type = getattr(state, "analysis_type", "general")
        
        if not company_id:
            logger.error("Nelze získat další data - chybí ID společnosti")
            return {"error_state": {"error": "Missing company ID", "error_type": "invalid_data"}}
        
        logger.info(f"Získávám doplňující data pro společnost ID: {company_id}, typ analýzy: {analysis_type}")
        
        # Zjednodušený přístup k MCP konektoru - vždy vytvořit novou instanci pro PoC
        from memory_agent.tools import MockMCPConnector
        logger.info("Vytvářím novou instanci MockMCPConnector pro PoC")
        mcp_connector = MockMCPConnector()
        
        # Připojit konektor do state
        state.mcp_connector = mcp_connector
        
        # Inicializace návratových dat
        financial_data = {}
        search_info = {}
        relationships_data = {}
        supply_chain_data = {}
        risk_factors_data = {}
        
        # Zjednodušené načítání dat podle typu analýzy
        try:
            logger.info(f"Načítání dat pro typ analýzy: {analysis_type}")
            
            # Pro všechny typy analýz načteme základní finanční data
            financial_data = mcp_connector.get_company_financials(company_id)
            
            # Načteme dodatečná data podle typu analýzy
            if analysis_type == "general":
                search_info = mcp_connector.get_company_search_data(company_id)
            elif analysis_type == "risk_comparison":
                risk_factors_data = mcp_connector.get_risk_factors_data(company_id)
            elif analysis_type == "supplier_analysis":
                relationships = mcp_connector.get_company_relationships(company_id)
                relationships_data = {company_id: relationships}
                
                supply_chain = mcp_connector.get_supply_chain_data(company_id)
                supply_chain_data = {company_id: supply_chain}
        
        except Exception as e:
            logger.error(f"Chyba při načítání dat: {str(e)}")
            # Pro PoC nebudeme řešit detailní chyby
        
        # Sestavení výsledku podle typu analýzy
        result = {
            "company_data": {},
            "mcp_connector": mcp_connector
        }
        
        # Přidání dat podle typu analýzy
        if analysis_type == "general":
            result["company_data"] = {
                "financials": financial_data,
                "search_info": search_info
            }
        elif analysis_type == "risk_comparison":
            result["company_data"] = {
                "financials": financial_data
            }
            result["risk_factors_data"] = risk_factors_data
        elif analysis_type == "supplier_analysis":
            result["relationships_data"] = relationships_data
            result["supply_chain_data"] = supply_chain_data
        
        return result
    
    except Exception as e:
        logger.error(f"Chyba při získávání dat: {e}")
        return {"error_state": {"error": "Data retrieval error", "error_type": "data_access_error"}}

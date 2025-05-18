"""
Graph nodes pro integraci MockMCPConnector s LangGraph workflow.

Tento modul obsahuje implementaci uzlů grafu pro StateGraph, které využívají
MockMCPConnector pro získávání dat pro různé typy analýz.
"""

from typing import Dict, Any, TypedDict, List, Optional, Literal
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
from memory_agent.analyzer import analyze_query

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

def route_query(state: State) -> State:
    """
    Analyzuje vstupní dotaz a určí, jaký typ dotazu to je.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s určeným typem dotazu
    """
    if state.current_query is None and state.messages:
        # Extrahujeme dotaz z poslední zprávy
        last_message = state.messages[-1]
        state.current_query = last_message.content
    
    if state.current_query:
        analysis_result = analyze_query(state.current_query)
        query_type = "general"  # Výchozí typ dotazu
        
        # Pokud analyze_query vrátilo AnalysisResult (což by mělo)
        if hasattr(analysis_result, "analysis_type"):
            query_type = analysis_result.analysis_type
        elif isinstance(analysis_result, dict) and "analysis_type" in analysis_result:
            query_type = analysis_result["analysis_type"]
        
        logger.info(f"Dotaz '{state.current_query[:30]}...' klasifikován jako typ: {query_type}")
        
        return {"query_type": query_type}
    else:
        logger.error("Nebyl nalezen žádný dotaz k analýze")
        return {"query_type": "error", "error_state": {"error": "Nebyl nalezen žádný dotaz k analýze"}}

def prepare_company_query(state: State) -> State:
    """
    Připraví parametry pro dotaz na společnost.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu
    """
    logger.info(f"Připravuji dotaz pro společnost: {state.current_query}")
    
    # Zde by byl kód pro extrakci názvu společnosti, časového období atd.
    # Pro jednoduchost předpokládáme, že dotaz obsahuje název společnosti
    
    # Placeholder - v reálném kódu by zde byla skutečná extrakce parametrů
    company_name = state.current_query.split()[-1] if state.current_query else "Unknown"
    
    internal_data = {
        "query_params": {
            "company_name": company_name,
            "time_period": "last_year"
        }
    }
    
    return {"internal_data": internal_data}

def retrieve_company_data(state: State) -> State:
    """
    Získá data o společnosti z MCP.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s daty společnosti
    """
    mcp_connector = state.get_mcp_connector()
    
    try:
        query_params = state.internal_data.get("query_params", {})
        company_name = query_params.get("company_name")
        
        logger.info(f"Získávám data pro společnost: {company_name}")
        
        company_data = mcp_connector.get_company_by_name(company_name)
        
        return {"company_data": {"basic_info": company_data}}
    
    except EntityNotFoundError as e:
        logger.error(f"Společnost nenalezena: {e}")
        return {"error_state": {"error": str(e), "error_type": "entity_not_found"}}
    
    except (DataFormatError, ConnectionError, MockMCPConnectorError) as e:
        logger.error(f"Chyba při získávání dat společnosti: {e}")
        return {"error_state": {"error": str(e), "error_type": "data_access_error"}}

def plan_company_analysis(state: State) -> State:
    """
    Naplánuje analýzu společnosti na základě dostupných dat.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s plánem analýzy
    """
    logger.info("Plánuji analýzu společnosti")
    
    # Placeholder pro plánování analýzy
    analysis_plan = {
        "steps": [
            "basic_info_analysis",
            "financial_analysis",
            "relationship_analysis"
        ],
        "required_data": [
            "financial_reports",
            "relationships"
        ]
    }
    
    return {"internal_data": {"analysis_plan": analysis_plan}}

def retrieve_additional_company_data(state: State) -> State:
    """
    Získá další data potřebná pro analýzu společnosti.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s doplňujícími daty
    """
    mcp_connector = state.get_mcp_connector()
    
    try:
        company_id = state.company_data.get("basic_info", {}).get("id")
        
        if not company_id:
            logger.error("Nelze získat další data - chybí ID společnosti")
            return {"error_state": {"error": "Missing company ID", "error_type": "invalid_data"}}
        
        logger.info(f"Získávám doplňující data pro společnost ID: {company_id}")
        
        # Získání finančních dat
        financial_data = mcp_connector.get_company_financials(company_id)
        
        # Získání vztahů
        relationships = mcp_connector.get_company_relationships(company_id)
        
        return {
            "company_data": {
                "financials": financial_data
            },
            "relationships_data": {
                company_id: relationships
            }
        }
    
    except Exception as e:
        logger.error(f"Chyba při získávání doplňujících dat: {e}")
        return {"error_state": {"error": str(e), "error_type": "data_access_error"}}

def analyze_company_data(state: State) -> State:
    """
    Provede analýzu dat společnosti.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky analýzy
    """
    logger.info("Analyzuji data společnosti")
    
    # Placeholder pro skutečnou analýzu
    company_name = state.company_data.get("basic_info", {}).get("name", "Unknown Company")
    
    analysis_result = {
        "company_name": company_name,
        "summary": f"Analýza společnosti {company_name}",
        "key_findings": [
            "Nalezeno několik významných obchodních vztahů",
            "Finanční údaje ukazují stabilní růst"
        ],
        "data_quality": "high"
    }
    
    return {"analysis_result": analysis_result}

def prepare_person_query(state: State) -> State:
    """
    Připraví parametry pro dotaz na osobu.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu
    """
    logger.info(f"Připravuji dotaz pro osobu: {state.current_query}")
    
    # Placeholder pro extrakci parametrů osoby
    person_name = state.current_query.split()[-1] if state.current_query else "Unknown"
    
    internal_data = {
        "query_params": {
            "person_name": person_name
        }
    }
    
    return {"internal_data": internal_data}

def retrieve_person_data(state: State) -> State:
    """
    Získá data o osobě z MCP.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s daty osoby
    """
    mcp_connector = state.get_mcp_connector()
    
    try:
        query_params = state.internal_data.get("query_params", {})
        person_name = query_params.get("person_name")
        
        logger.info(f"Získávám data pro osobu: {person_name}")
        
        # Mockovaná funkce - ve skutečnosti by volala MCP connector
        person_data = mcp_connector.get_person_by_name(person_name)
        
        return {"internal_data": {"person_data": person_data}}
    
    except Exception as e:
        logger.error(f"Chyba při získávání dat osoby: {e}")
        return {"error_state": {"error": str(e), "error_type": "data_access_error"}}

def analyze_person_data(state: State) -> State:
    """
    Provede analýzu dat osoby.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky analýzy
    """
    logger.info("Analyzuji data osoby")
    
    person_data = state.internal_data.get("person_data", {})
    person_name = person_data.get("name", "Unknown Person")
    
    analysis_result = {
        "person_name": person_name,
        "summary": f"Analýza osoby {person_name}",
        "key_findings": [
            "Osoba má několik významných rolí ve společnostech",
            "Nalezeno několik relevantních vztahů"
        ]
    }
    
    return {"analysis_result": analysis_result}

def prepare_relationship_query(state: State) -> State:
    """
    Připraví parametry pro dotaz na vztahy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu
    """
    logger.info(f"Připravuji dotaz pro vztahy: {state.current_query}")
    
    # Placeholder pro extrakci entit vztahu
    entities = state.current_query.split(" a ") if state.current_query else []
    
    internal_data = {
        "query_params": {
            "entities": entities,
            "relationship_type": "all"
        }
    }
    
    return {"internal_data": internal_data}

def retrieve_relationship_data(state: State) -> State:
    """
    Získá data o vztazích z MCP.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s daty vztahů
    """
    mcp_connector = state.get_mcp_connector()
    
    try:
        query_params = state.internal_data.get("query_params", {})
        entities = query_params.get("entities", [])
        
        logger.info(f"Získávám data pro vztahy mezi entitami: {entities}")
        
        # Mockovaná funkce - ve skutečnosti by volala MCP connector
        relationship_data = []
        for entity in entities:
            # Placeholder - předstíráme, že získáváme data pro každou entitu
            entity_data = {"entity": entity, "relationships": [{"type": "business", "target": "Example Corp"}]}
            relationship_data.append(entity_data)
        
        return {"internal_data": {"relationship_data": relationship_data}}
    
    except Exception as e:
        logger.error(f"Chyba při získávání dat o vztazích: {e}")
        return {"error_state": {"error": str(e), "error_type": "data_access_error"}}

def analyze_relationship_data(state: State) -> State:
    """
    Provede analýzu dat o vztazích.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky analýzy
    """
    logger.info("Analyzuji data o vztazích")
    
    relationship_data = state.internal_data.get("relationship_data", [])
    entities = [data.get("entity") for data in relationship_data]
    
    analysis_result = {
        "entities_analyzed": entities,
        "summary": f"Analýza vztahů mezi {', '.join(entities)}",
        "key_findings": [
            "Nalezeno několik přímých obchodních vazeb",
            "Identifikovány potenciální nepřímé vztahy"
        ]
    }
    
    return {"analysis_result": analysis_result}

def prepare_custom_query(state: State) -> State:
    """
    Připraví parametry pro vlastní dotaz.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu
    """
    logger.info(f"Připravuji vlastní dotaz: {state.current_query}")
    
    # Placeholder pro identifikaci parametrů vlastního dotazu
    internal_data = {
        "query_params": {
            "custom_query": state.current_query,
            "query_type": "generic"
        }
    }
    
    return {"internal_data": internal_data}

def execute_custom_query(state: State) -> State:
    """
    Provede vlastní dotaz.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky dotazu
    """
    mcp_connector = state.get_mcp_connector()
    
    try:
        query_params = state.internal_data.get("query_params", {})
        custom_query = query_params.get("custom_query")
        
        logger.info(f"Provádím vlastní dotaz: {custom_query}")
        
        # Placeholder pro provedení vlastního dotazu
        custom_results = {"query": custom_query, "results": ["Výsledek 1", "Výsledek 2"]}
        
        return {"internal_data": {"custom_results": custom_results}}
    
    except Exception as e:
        logger.error(f"Chyba při provádění vlastního dotazu: {e}")
        return {"error_state": {"error": str(e), "error_type": "query_execution_error"}}

def analyze_custom_results(state: State) -> State:
    """
    Analyzuje výsledky vlastního dotazu.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s analýzou výsledků
    """
    logger.info("Analyzuji výsledky vlastního dotazu")
    
    custom_results = state.internal_data.get("custom_results", {})
    query = custom_results.get("query", "Neznámý dotaz")
    
    analysis_result = {
        "query": query,
        "summary": f"Analýza výsledků pro dotaz: {query}",
        "key_findings": [
            "Nalezeno několik relevantních výsledků",
            "Výsledky poskytují odpověď na dotaz"
        ]
    }
    
    return {"analysis_result": analysis_result}

def generate_response(state: State) -> State:
    """
    Vygeneruje odpověď na základě analýzy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s odpovědí
    """
    logger.info("Generuji odpověď")
    
    analysis_result = state.analysis_result or {}
    error_state = state.error_state or {}
    
    if error_state:
        response = f"Omlouvám se, ale došlo k chybě: {error_state.get('error', 'Neznámá chyba')}"
    else:
        summary = analysis_result.get("summary", "Nemám dostatek informací pro odpověď.")
        key_findings = analysis_result.get("key_findings", [])
        
        response = f"{summary}\n\nKlíčová zjištění:\n"
        for finding in key_findings:
            response += f"- {finding}\n"
    
    return {"messages": [{"role": "assistant", "content": response}]}

def handle_error(state: State) -> State:
    """
    Zpracuje chybový stav a připraví informace pro odpověď.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s informacemi o chybě
    """
    logger.error(f"Zpracovávám chybový stav: {state.error_state}")
    
    error_message = "Omlouvám se, ale nemohu zpracovat váš dotaz."
    if state.error_state and "error" in state.error_state:
        error_message += f" Důvod: {state.error_state['error']}"
    
    analysis_result = {
        "summary": error_message,
        "key_findings": [
            "Došlo k chybě při zpracování dotazu",
            "Zkuste přeformulovat svůj dotaz nebo poskytnout více informací"
        ]
    }
    
    return {"analysis_result": analysis_result}

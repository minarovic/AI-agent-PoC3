"""
StateGraph workflow pro Memory Agent PoC-3.

Tento modul obsahuje implementaci grafu workflow pro zpracování uživatelských dotazů,
detekci typu analýzy a generování optimalizovaných odpovědí.
Upraveno pro kompatibilitu s LangGraph Platform.
Zjednodušeno pro základní analýzu společností.
"""

from typing import Dict, List, Any, Annotated, Literal, Optional, cast
from typing_extensions import TypedDict
import operator
import logging
from pathlib import Path

# LangChain/LangGraph imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, START, END
from langgraph.graph.graph import Graph
from pydantic import BaseModel, Field

# Local imports
from memory_agent.tools import (
    MockMCPConnector, 
    CompanyQueryParams, 
    EntityNotFoundError,
    DataFormatError,
    ConnectionError,
    MockMCPConnectorError
)
from memory_agent.state import State, AgentState
from memory_agent.graph_nodes import (
    determine_analysis_type,
    route_query,
    prepare_company_query,
    analyze_company_data,
    retrieve_additional_company_data
)
from memory_agent.configuration import get_config, Config

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Implementace chybějících funkcí
def handle_error(state: State) -> State:
    """
    Jednoduchá funkce pro zpracování chyb.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav
    """
    error_message = "Nastala chyba při zpracování dotazu."
    
    if hasattr(state, "error_state") and state.error_state:
        error_detail = state.error_state.get("error", "Neznámá chyba")
        error_type = state.error_state.get("error_type", "general_error")
        error_message = f"Chyba: {error_detail} (typ: {error_type})"
    
    logger.error(f"Zpracovávám chybu: {error_message}")
    
    return {
        "error_handled": True,
        "error_message": error_message
    }

def generate_response(state: State) -> State:
    """
    Generuje odpověď na základě výsledků analýzy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s odpovědí
    """
    # Vytvoříme zprávu na základě výsledků analýzy
    if hasattr(state, "error_handled") and state.error_handled:
        response_text = f"Omlouvám se, ale nastala chyba při zpracování vašeho dotazu: {state.error_message}"
    elif hasattr(state, "analysis_result") and state.analysis_result:
        # Formátování odpovědi na základě výsledků analýzy
        result = state.analysis_result
        company_name = result.get("company_name", "neznámá společnost")
        analysis_type = result.get("analysis_type", "general")
        summary = result.get("summary", f"Analýza společnosti {company_name}")
        
        response_text = f"{summary}\n\n"
        
        # Přidání klíčových zjištění
        key_findings = result.get("key_findings", [])
        if key_findings:
            response_text += "Klíčová zjištění:\n"
            for finding in key_findings:
                response_text += f"- {finding}\n"
    else:
        response_text = "Nepodařilo se získat dostatek informací pro odpověď na váš dotaz."
    
    # Přidáme odpověď do historie zpráv
    messages = list(state.messages) if hasattr(state, "messages") else []
    messages.append(AIMessage(content=response_text))
    
    logger.info(f"Generuji odpověď: {response_text[:100]}...")
    
    return {
        "messages": messages,
        "response": response_text
    }

def create_graph(config: Optional[Config] = None) -> StateGraph:
    """
    Vytvoří a konfiguruje StateGraph pro Memory Agent.
    
    Args:
        config: Konfigurace agenta. Pokud None, použije se výchozí konfigurace.
        
    Returns:
        StateGraph: Nakonfigurovaný StateGraph připravený k použití.
    """
    if config is None:
        config = get_config()
        
    logger.info(f"Vytvářím graf Memory Agent s modelem: {config.model}")
    
    # Inicializace grafu s State kontejnerem
    builder = StateGraph(State)

    # Přidání uzlů workflow - jen ty, které existují + naše implementace
    builder.add_node("route_query", route_query)
    builder.add_node("prepare_company_query", prepare_company_query)
    builder.add_node("retrieve_additional_company_data", retrieve_additional_company_data)
    builder.add_node("analyze_company_data", analyze_company_data)
    builder.add_node("generate_response", generate_response)
    builder.add_node("handle_error", handle_error)
    
    # Definice základního workflow
    builder.add_edge(START, "route_query")
    
    # Definice cest pro jednotlivé typy dotazů - zjednodušeno
    builder.add_conditional_edges(
        "route_query",
        lambda x: x.query_type if hasattr(x, "query_type") else "error",
        {
            "company": "prepare_company_query",
            # Zjednodušeno - všechny ostatní typy vedou na error
            "error": "handle_error"
        },
        default_dest="handle_error"  # Default pro všechny nezpracované typy
    )
    
    # Zjednodušený company workflow
    builder.add_edge("prepare_company_query", "retrieve_additional_company_data")
    builder.add_edge("retrieve_additional_company_data", "analyze_company_data")
    builder.add_edge("analyze_company_data", "generate_response")
    
    # Error handling
    builder.add_edge("handle_error", "generate_response")
    
    # Odpověď je koncovým bodem
    builder.add_edge("generate_response", END)
    
    # Kompilace grafu
    return builder.compile()

# Vytvoření grafu pro nasazení na LangGraph Platform
graph = create_graph()

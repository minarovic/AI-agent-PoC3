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
# Přidání importu pro checkpointing
from langgraph.checkpoint.memory import MemorySaver

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
    Zajišťuje, že uživatel vždy dostane užitečnou informaci.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s odpovědí
    """
    # Získáme základní informace o dotazu
    company_name = getattr(state, "company_name", "neznámá společnost")
    query = getattr(state, "current_query", "")
    analysis_type = getattr(state, "analysis_type", "general")
    
    # Vytvoříme zprávu podle výsledku workflow
    if hasattr(state, "error_handled") and state.error_handled:
        # Chybová odpověď s pokusem o řešení
        error_msg = getattr(state, "error_message", "Neznámá chyba")
        
        response_text = f"Omlouvám se, ale nastala chyba při zpracování dotazu: {error_msg}\n\n"
        
        # Přidáme informace o nalezené společnosti
        if company_name and company_name != "Unknown" and company_name != "neznámá společnost":
            response_text += f"Identifikoval jsem společnost: {company_name}, "
            response_text += f"a pokusil jsem se provést {analysis_type} analýzu, ale došlo k problému.\n\n"
            response_text += "Zkuste prosím upřesnit váš dotaz nebo se zeptat na jinou společnost."
        else:
            response_text += "Nepodařilo se mi identifikovat společnost v dotazu. Zkuste prosím dotaz přeformulovat."
    
    elif hasattr(state, "analysis_result") and state.analysis_result:
        # Úspěšná odpověď s výsledky analýzy
        result = state.analysis_result
        company_name = result.get("company_name", company_name)
        analysis_type = result.get("analysis_type", analysis_type)
        summary = result.get("summary", f"Analýza společnosti {company_name}")
        
        response_text = f"{summary}\n\n"
        
        # Přidání klíčových zjištění
        key_findings = result.get("key_findings", [])
        if key_findings:
            response_text += "Klíčová zjištění:\n"
            for finding in key_findings:
                response_text += f"- {finding}\n"
                
        # Přidání detailů podle typu analýzy
        if analysis_type == "risk_comparison":
            risk_score = result.get("risk_score")
            if risk_score:
                response_text += f"\nRizikové skóre: {risk_score}\n"
                
            risk_factors = result.get("risk_factors", [])
            if risk_factors:
                response_text += "\nIdentifikované rizikové faktory:\n"
                for factor in risk_factors[:5]:  # Zobrazíme maximálně 5 faktorů
                    factor_text = factor.get("factor", "")
                    category = factor.get("category", "")
                    level = factor.get("level", "")
                    response_text += f"- {factor_text} (kategorie: {category}, úroveň: {level})\n"
                
                if len(risk_factors) > 5:
                    response_text += f"...a dalších {len(risk_factors) - 5} rizikových faktorů.\n"
                    
        elif analysis_type == "supplier_analysis":
            suppliers = result.get("suppliers", [])
            if suppliers:
                response_text += "\nHlavní dodavatelé:\n"
                for supplier in suppliers[:5]:
                    name = supplier.get("name", "")
                    tier = supplier.get("tier", "")
                    response_text += f"- {name} (tier: {tier})\n"
                    
                if len(suppliers) > 5:
                    response_text += f"...a dalších {len(suppliers) - 5} dodavatelů.\n"
    
    else:
        # Záložní odpověď, když nemáme žádné výsledky
        response_text = "Nepodařilo se získat dostatek informací pro odpověď na váš dotaz.\n\n"
        
        # Přidáme informace o nalezené společnosti
        if company_name and company_name != "Unknown" and company_name != "neznámá společnost":
            response_text += f"Identifikoval jsem společnost: {company_name}, ale nemám o ní dostatek dat.\n"
            response_text += f"Pokusil jsem se provést {analysis_type} analýzu, ale potřebná data nejsou dostupná."
        else:
            response_text += "Nepodařilo se mi identifikovat společnost v dotazu. Zkuste prosím dotaz přeformulovat."
    
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
            # Všechny ostatní známé typy explicitně přesměrovat na error handler
            "error": "handle_error",
            "person": "handle_error",
            "relationship": "handle_error", 
            "custom": "handle_error",
            "unknown": "handle_error"
        }
    )
    
    # Optimalizovaný company workflow s podporou typů analýzy
    builder.add_edge("prepare_company_query", "retrieve_additional_company_data")
    
    # Podmíněné větve podle typu analýzy pro retrieve_additional_company_data
    builder.add_conditional_edges(
        "retrieve_additional_company_data",
        lambda x: "error" if hasattr(x, "error_state") else "continue",
        {
            "continue": "analyze_company_data",
            "error": "handle_error"
        }
    )
    
    # Standardní dokončení workflow pro všechny typy analýz
    builder.add_edge("analyze_company_data", "generate_response")
    
    # Error handling
    builder.add_edge("handle_error", "generate_response")
    
    # Odpověď je koncovým bodem
    builder.add_edge("generate_response", END)
    
    # Vytvoření checkpointeru pro persistenci stavu
    memory_checkpointer = MemorySaver()
    
    # Kompilace grafu s checkpointerem
    return builder.compile(checkpointer=memory_checkpointer)

# Vytvoření grafu pro nasazení na LangGraph Platform
graph = create_graph()

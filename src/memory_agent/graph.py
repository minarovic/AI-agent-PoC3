"""
StateGraph workflow pro Memory Agent PoC-3.

Tento modul obsahuje implementaci grafu workflow pro zpracování uživatelských dotazů,
detekci typu analýzy a generování optimalizovaných odpovědí.
Upraveno pro kompatibilitu s LangGraph Platform.
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
    route_query,
    prepare_company_query,
    retrieve_company_data,
    analyze_company_data,
    plan_company_analysis,
    retrieve_additional_company_data,
    prepare_person_query,
    retrieve_person_data,
    analyze_person_data,
    prepare_relationship_query,
    retrieve_relationship_data,
    analyze_relationship_data,
    prepare_custom_query,
    execute_custom_query,
    analyze_custom_results,
    generate_response,
    handle_error
)
from memory_agent.configuration import get_config, Config

# Nastavení loggeru
logger = logging.getLogger(__name__)

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

    # Přidání uzlů workflow
    builder.add_node("route_query", route_query)
    builder.add_node("prepare_company_query", prepare_company_query)
    builder.add_node("retrieve_company_data", retrieve_company_data)
    builder.add_node("analyze_company_data", analyze_company_data)
    builder.add_node("plan_company_analysis", plan_company_analysis)
    builder.add_node("retrieve_additional_company_data", retrieve_additional_company_data)
    builder.add_node("prepare_person_query", prepare_person_query)
    builder.add_node("retrieve_person_data", retrieve_person_data)
    builder.add_node("analyze_person_data", analyze_person_data)
    builder.add_node("prepare_relationship_query", prepare_relationship_query)
    builder.add_node("retrieve_relationship_data", retrieve_relationship_data)
    builder.add_node("analyze_relationship_data", analyze_relationship_data)
    builder.add_node("prepare_custom_query", prepare_custom_query)
    builder.add_node("execute_custom_query", execute_custom_query)
    builder.add_node("analyze_custom_results", analyze_custom_results)
    builder.add_node("generate_response", generate_response)
    builder.add_node("handle_error", handle_error)
    
    # Definice základního workflow
    builder.add_edge(START, "route_query")
    
    # Definice cest pro jednotlivé typy dotazů
    builder.add_conditional_edges(
        "route_query",
        lambda x: x.query_type,  # x je přímo objekt State, ne slovník
        {
            "company": "prepare_company_query",
            "person": "prepare_person_query",
            "relationship": "prepare_relationship_query",
            "custom": "prepare_custom_query",
            "error": "handle_error"
        }
    )
    
    # Company workflow
    builder.add_edge("prepare_company_query", "retrieve_company_data")
    builder.add_edge("retrieve_company_data", "plan_company_analysis")
    builder.add_edge("plan_company_analysis", "retrieve_additional_company_data")
    builder.add_edge("retrieve_additional_company_data", "analyze_company_data")
    builder.add_edge("analyze_company_data", "generate_response")
    
    # Person workflow
    builder.add_edge("prepare_person_query", "retrieve_person_data")
    builder.add_edge("retrieve_person_data", "analyze_person_data")
    builder.add_edge("analyze_person_data", "generate_response")
    
    # Relationship workflow
    builder.add_edge("prepare_relationship_query", "retrieve_relationship_data")
    builder.add_edge("retrieve_relationship_data", "analyze_relationship_data")
    builder.add_edge("analyze_relationship_data", "generate_response")
    
    # Custom query workflow
    builder.add_edge("prepare_custom_query", "execute_custom_query")
    builder.add_edge("execute_custom_query", "analyze_custom_results")
    builder.add_edge("analyze_custom_results", "generate_response")
    
    # Error handling
    builder.add_edge("handle_error", "generate_response")
    
    # Odpověď je koncovým bodem
    builder.add_edge("generate_response", END)
    
    # Kompilace grafu
    return builder.compile()

# Vytvoření grafu pro nasazení na LangGraph Platform
graph = create_graph()

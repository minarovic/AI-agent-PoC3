"""
Explicitní StateGraph workflow pro Memory Agent.

Tento modul obsahuje implementaci explicitního StateGraph workflow, který nahrazuje
původní ReAct agent workflow s explicitním řízením toku a podmíněným větvením.

Struktura workflow:
1. route_query - analýza dotazu a určení typu
2. prepare_company_query - příprava dotazu a načtení základních dat
3. retrieve_additional_company_data - načtení dodatečných dat podle typu analýzy
4. analyze_company_data - analýza dat podle typu
5. format_response_node - formátování výsledné odpovědi

Podporované typy analýz:
- general: obecné informace o společnosti
- risk_comparison: analýza rizik a compliance
- supplier_analysis: analýza dodavatelských vztahů
"""

import logging
from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph

from .configuration import Configuration
from .graph_nodes import (
    analyze_company_data,
    format_response_node,
    prepare_company_query,
    retrieve_additional_company_data,
    route_query,
)
from .state import State

# Nastavení loggeru
logger = logging.getLogger(__name__)


def create_explicit_stategraph():
    """
    Vytvoří explicitní StateGraph workflow pro Memory Agent.
    
    Tento graf implementuje explicitní řízení workflow s podmíněným větvením
    na základě typu analýzy. Každý uzel má jasně definovanou zodpovědnost
    a LLM nikdy nevolá tools přímo - vše je řízeno explicitně.
    
    Returns:
        CompiledStateGraph: Zkompilovaný graf připravený k použití
    """
    logger.info("Vytvářím explicitní StateGraph workflow")
    
    # Inicializace StateGraph s naším State typem
    workflow = StateGraph(State)
    
    # Přidání uzlů do grafu
    workflow.add_node("route_query", route_query)
    workflow.add_node("prepare_company_query", prepare_company_query)
    workflow.add_node("retrieve_additional_company_data", retrieve_additional_company_data)
    workflow.add_node("analyze_company_data", analyze_company_data)
    workflow.add_node("format_response_node", format_response_node)
    workflow.add_node("error_node", handle_error_state)
    
    # Nastavení vstupního bodu
    workflow.set_entry_point("route_query")
    
    # Definice podmíněného větvení na základě typu analýzy
    def analyze_branch(state: State) -> Literal["analyze_company_data", "error_node"]:
        """
        Rozhodovací funkce pro směrování po načtení dat.
        
        Args:
            state: Aktuální stav workflow
            
        Returns:
            Název následujícího uzlu
        """
        # Kontrola chybového stavu
        if hasattr(state, 'error_state') and state.error_state:
            logger.warning("Detekován chybový stav, směruji na error_node")
            return "error_node"
            
        # Kontrola typu analýzy
        analysis_type = getattr(state, 'analysis_type', None)
        
        if analysis_type in ["general", "risk_comparison", "supplier_analysis"]:
            logger.info(f"Směruji na analýzu dat pro typ: {analysis_type}")
            return "analyze_company_data"
        else:
            logger.warning(f"Neznámý typ analýzy: {analysis_type}, směruji na chybový uzel")
            return "error_node"
    
    def query_branch(state: State) -> Literal["prepare_company_query", "error_node"]:
        """
        Rozhodovací funkce po route_query.
        
        Args:
            state: Aktuální stav workflow
            
        Returns:
            Název následujícího uzlu
        """
        # Kontrola chybového stavu
        if hasattr(state, 'error_state') and state.error_state:
            logger.warning("Chyba při analýze dotazu, směruji na error_node")
            return "error_node"
            
        # Kontrola, zda byl identifikován typ dotazu
        query_type = getattr(state, 'query_type', None)
        
        if query_type == "error":
            logger.warning("Typ dotazu označen jako chyba")
            return "error_node"
        elif query_type:
            logger.info(f"Dotaz úspěšně analyzován (typ: {query_type})")
            return "prepare_company_query"
        else:
            logger.warning("Nepodařilo se určit typ dotazu")
            return "error_node"
    
    def data_preparation_branch(state: State) -> Literal["retrieve_additional_company_data", "error_node"]:
        """
        Rozhodovací funkce po prepare_company_query.
        
        Args:
            state: Aktuální stav workflow
            
        Returns:
            Název následujícího uzlu
        """
        # Kontrola chybového stavu
        if hasattr(state, 'error_state') and state.error_state:
            logger.warning("Chyba při přípravě dotazu, směruji na error_node")
            return "error_node"
            
        # Kontrola, zda máme základní data o společnosti
        company_data = getattr(state, 'company_data', None)
        company_name = getattr(state, 'company_name', None)
        
        if company_data and company_name:
            logger.info(f"Základní data připravena pro {company_name}")
            return "retrieve_additional_company_data"
        else:
            logger.warning("Chybí základní data o společnosti")
            return "error_node"
    
    # Přidání hran s podmíněným větvením
    workflow.add_conditional_edges(
        "route_query",
        query_branch,
        {
            "prepare_company_query": "prepare_company_query",
            "error_node": "error_node",
        },
    )
    
    workflow.add_conditional_edges(
        "prepare_company_query", 
        data_preparation_branch,
        {
            "retrieve_additional_company_data": "retrieve_additional_company_data",
            "error_node": "error_node",
        },
    )
    
    workflow.add_conditional_edges(
        "retrieve_additional_company_data",
        analyze_branch,
        {
            "analyze_company_data": "analyze_company_data",
            "error_node": "error_node",
        },
    )
    
    # Jednoduché hrany pro dokončení workflow
    workflow.add_edge("analyze_company_data", "format_response_node")
    workflow.add_edge("error_node", "format_response_node")
    
    # Nastavení koncového bodu
    workflow.set_finish_point("format_response_node")
    
    # Inicializace checkpointeru pro persistenci
    checkpointer = InMemorySaver()
    
    # Kompilace grafu s checkpointerem
    try:
        app = workflow.compile(checkpointer=checkpointer)
        logger.info("✅ Explicitní StateGraph workflow úspěšně zkompilován")
        return app
    except Exception as e:
        logger.error(f"❌ Chyba při kompilaci StateGraph: {str(e)}")
        raise


def handle_error_state(state: State) -> State:
    """
    Uzel pro zpracování chybových stavů.
    
    Args:
        state: Aktuální stav s chybovými informacemi
        
    Returns:
        Aktualizovaný stav s chybovými zprávami připravenými pro výstup
    """
    logger.info("Zpracovávám chybový stav")
    
    # Získání chybových informací
    error_state = getattr(state, 'error_state', {})
    
    if not error_state:
        error_state = {
            "error": "Neznámá chyba ve workflow",
            "error_type": "unknown_error"
        }
    
    # Příprava chybové zprávy pro uživatele
    error_message = error_state.get('error', 'Došlo k neočekávané chybě')
    error_type = error_state.get('error_type', 'unknown')
    
    logger.warning(f"Zpracována chyba typu {error_type}: {error_message}")
    
    # Vytvoření strukturované chybové odpovědi
    error_output = {
        "status": "error",
        "error_type": error_type,
        "message": error_message,
        "suggestions": get_error_suggestions(error_type)
    }
    
    return {
        "output": error_output,
        "analysis_result": {
            "status": "failed",
            "error": error_message,
            "error_type": error_type
        }
    }


def get_error_suggestions(error_type: str) -> list[str]:
    """
    Vrátí návrhy na řešení podle typu chyby.
    
    Args:
        error_type: Typ chyby
        
    Returns:
        Seznam návrhů na řešení
    """
    suggestions_map = {
        "missing_data": [
            "Zkontrolujte, zda je název společnosti správně napsán",
            "Zkuste použít jiný název nebo identifikátor společnosti",
            "Ujistěte se, že společnost existuje v naší databázi"
        ],
        "data_access_error": [
            "Zkuste dotaz znovu za chvíli",
            "Zkontrolujte připojení k datovým zdrojům",
            "Kontaktujte podporu, pokud problém přetrvává"
        ],
        "analysis_error": [
            "Zkuste zjednodušit váš dotaz",
            "Použijte konkrétnější název společnosti",
            "Zkontrolujte, zda požadovaný typ analýzy je podporován"
        ],
        "unknown_error": [
            "Zkuste dotaz znovu",
            "Zkontrolujte formát vašeho dotazu",
            "Kontaktujte podporu s detaily o chybě"
        ]
    }
    
    return suggestions_map.get(error_type, suggestions_map["unknown_error"])


def create_react_agent_legacy():
    """
    Fallback funkce pro vytvoření původního ReAct agenta.
    
    Tato funkce slouží jako záložní řešení, pokud explicitní StateGraph
    z nějakého důvodu nefunguje nebo je potřeba kompatibilita se starším kódem.
    
    Returns:
        ReAct agent z původního graph.py modulu
    """
    logger.info("Vytvářím fallback ReAct agenta")
    
    try:
        from .graph import create_memory_agent
        return create_memory_agent()
    except Exception as e:
        logger.error(f"❌ Chyba při vytváření fallback agenta: {str(e)}")
        raise


# Lazy initialization to avoid immediate execution at import time
def get_memory_agent_stategraph():
    """
    Lazy inicializace Memory Agent s explicitním StateGraph.
    
    Tato funkce se pokusí vytvořit explicitní StateGraph workflow,
    a pokud se to nepodaří, použije fallback na původního ReAct agenta.
    
    Returns:
        Zkompilovaný graf nebo ReAct agent
    """
    try:
        logger.info("Pokus o vytvoření explicitního StateGraph workflow")
        return create_explicit_stategraph()
    except Exception as e:
        logger.warning(f"⚠️ Explicitní StateGraph selhal: {str(e)}")
        logger.info("Přepínám na fallback ReAct agenta")
        return create_react_agent_legacy()


# Pro LangGraph Platform deployment - lazy initialization
def get_graph_for_deployment():
    """
    Vrátí graf pro deployment na LangGraph Platform.
    
    Používá lazy initialization, aby se předešlo chybám při importu
    v prostředích bez API klíčů.
    
    Returns:
        Zkompilovaný graf
    """
    try:
        return get_memory_agent_stategraph()
    except Exception as e:
        logger.error(f"❌ Nelze vytvořit graf pro deployment: {str(e)}")
        # Vytvoříme minimální placeholder graf pro schema introspection
        return create_placeholder_graph()


def create_placeholder_graph():
    """
    Vytvoří minimální placeholder graf pro případy, kdy není možné
    vytvořit plnohodnotný graf (např. chybí API klíče).
    
    Returns:
        Minimální StateGraph pro schema introspection
    """
    from langgraph.graph import StateGraph
    
    def placeholder_node(state: State) -> State:
        """Placeholder node pro schema introspection."""
        return {
            "output": {
                "status": "placeholder",
                "message": "Graf není plně inicializován - chybí konfigurace"
            }
        }
    
    workflow = StateGraph(State)
    workflow.add_node("placeholder", placeholder_node)
    workflow.set_entry_point("placeholder")
    workflow.set_finish_point("placeholder")
    
    return workflow.compile()


# Lazy export - pouze při explicitním zavolání
memory_agent_stategraph = None
graph_stategraph = None

# Export pro externí použití
__all__ = [
    "create_explicit_stategraph",
    "create_react_agent_legacy", 
    "get_memory_agent_stategraph",
    "get_graph_for_deployment",
    "create_placeholder_graph"
]
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

from langgraph.graph import StateGraph

from .state import State

# Nastavení loggeru
logger = logging.getLogger(__name__)


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
    error_state = getattr(state, "error_state", {})

    if not error_state:
        error_state = {
            "error": "Neznámá chyba ve workflow",
            "error_type": "unknown_error",
        }

    # Příprava chybové zprávy pro uživatele
    error_message = error_state.get("error", "Došlo k neočekávané chybě")
    error_type = error_state.get("error_type", "unknown")

    logger.warning(f"Zpracována chyba typu {error_type}: {error_message}")

    # Vytvoření strukturované chybové odpovědi
    error_output = {
        "status": "error",
        "error_type": error_type,
        "message": error_message,
        "suggestions": get_error_suggestions(error_type),
    }

    return {
        "output": error_output,
        "analysis_result": {
            "status": "failed",
            "error": error_message,
            "error_type": error_type,
        },
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
            "Ujistěte se, že společnost existuje v naší databázi",
        ],
        "data_access_error": [
            "Zkuste dotaz znovu za chvíli",
            "Zkontrolujte připojení k datovým zdrojům",
            "Kontaktujte podporu, pokud problém přetrvává",
        ],
        "analysis_error": [
            "Zkuste zjednodušit váš dotaz",
            "Použijte konkrétnější název společnosti",
            "Zkontrolujte, zda požadovaný typ analýzy je podporován",
        ],
        "unknown_error": [
            "Zkuste dotaz znovu",
            "Zkontrolujte formát vašeho dotazu",
            "Kontaktujte podporu s detaily o chybě",
        ],
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
        logger.error(f"Chyba při vytváření fallback agenta: {str(e)}")
        raise


# Lazy initialization to avoid immediate execution at import time
def get_memory_agent_stategraph():
    """
    Lazy inicializace Memory Agent s fallback na ReAct agenta.

    Tato funkce používá fallback na původního ReAct agenta.

    Returns:
        ReAct agent
    """
    logger.info("Používám fallback ReAct agenta")
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

    def placeholder_node(state: State) -> State:
        """Placeholder node pro schema introspection."""
        return {
            "output": {
                "status": "placeholder",
                "message": "Graf není plně inicializován - chybí konfigurace",
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
    "create_react_agent_legacy",
    "get_memory_agent_stategraph",
    "get_graph_for_deployment",
    "create_placeholder_graph",
]

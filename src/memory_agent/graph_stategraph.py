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

from langgraph.graph import StateGraph, START, END

from .state import State
from .graph_nodes import (
    route_query,
    prepare_company_query,
    retrieve_additional_company_data,
    analyze_company_data,
)

# Nastavení loggeru
logger = logging.getLogger(__name__)


def format_response_node(state: State) -> State:
    """
    Uzel pro formátování finální odpovědi uživateli.

    Args:
        state: Aktuální stav s výsledky analýzy

    Returns:
        Aktualizovaný stav s formátovanou odpovědí
    """
    logger.info("Formátuji finální odpověď")

    # Získání výsledků analýzy
    analysis_result = getattr(state, "analysis_result", {})
    analysis_type = getattr(state, "analysis_type", "general")
    company_name = getattr(state, "company_name", "Neznámá společnost")

    if not analysis_result:
        # Fallback pokud nemáme výsledky analýzy
        output = {
            "status": "completed",
            "analysis_type": analysis_type,
            "company_name": company_name,
            "message": f"Analýza společnosti {company_name} byla dokončena, ale nejsou k dispozici detailní výsledky.",
        }
    else:
        # Formátování podle typu analýzy
        if analysis_type == "risk_comparison":
            risk_score = analysis_result.get("risk_score")
            risk_factors = analysis_result.get("risk_factors", [])

            output = {
                "status": "completed",
                "analysis_type": analysis_type,
                "company_name": company_name,
                "summary": analysis_result.get(
                    "summary", f"Analýza rizik pro {company_name}"
                ),
                "risk_score": risk_score,
                "risk_factors_count": len(risk_factors),
                "key_findings": analysis_result.get("key_findings", []),
                "data_quality": analysis_result.get("data_quality", "unknown"),
            }

        elif analysis_type == "supplier_analysis":
            suppliers = analysis_result.get("suppliers", [])

            output = {
                "status": "completed",
                "analysis_type": analysis_type,
                "company_name": company_name,
                "summary": analysis_result.get(
                    "summary", f"Analýza dodavatelů pro {company_name}"
                ),
                "suppliers_count": len(suppliers),
                "key_findings": analysis_result.get("key_findings", []),
                "data_quality": analysis_result.get("data_quality", "unknown"),
            }

        else:  # general analysis
            output = {
                "status": "completed",
                "analysis_type": analysis_type,
                "company_name": company_name,
                "summary": analysis_result.get(
                    "summary", f"Obecná analýza pro {company_name}"
                ),
                "basic_info": analysis_result.get("basic_info", {}),
                "key_findings": analysis_result.get("key_findings", []),
                "data_quality": analysis_result.get("data_quality", "unknown"),
            }

    logger.info(f"Formátování dokončeno pro analýzu typu {analysis_type}")

    return {"output": output}


def check_for_errors(state: State) -> Literal["error", "continue"]:
    """
    Funkce pro kontrolu chybových stavů v workflow.

    Args:
        state: Aktuální stav workflow

    Returns:
        "error" pokud je v stavu chyba, jinak "continue"
    """
    error_state = getattr(state, "error_state", {})
    if error_state and error_state.get("error"):
        logger.warning(f"Detekována chyba: {error_state.get('error')}")
        return "error"
    return "continue"


def route_analysis_type(
    state: State,
) -> Literal["general", "risk_comparison", "supplier_analysis"]:
    """
    Funkce pro směrování podle typu analýzy.

    Args:
        state: Aktuální stav s typem analýzy

    Returns:
        Typ analýzy pro podmíněné větvení
    """
    analysis_type = getattr(state, "analysis_type", "general")
    logger.info(f"Směrování podle typu analýzy: {analysis_type}")

    if analysis_type in ["risk_comparison", "supplier_analysis", "general"]:
        return analysis_type
    else:
        logger.warning(f"Neznámý typ analýzy {analysis_type}, použiji general")
        return "general"


def create_explicit_stategraph():
    """
    Vytvoří explicitní StateGraph workflow pro Memory Agent.

    Tento workflow nahrazuje ReAct agenta explicitním řízením toku
    s podmíněným větvením podle typu analýzy. Každý krok je deterministicky
    řízen stavem bez LLM rozhodování o použití nástrojů.

    Returns:
        Zkompilovaný StateGraph workflow
    """
    logger.info("Vytvářím explicitní StateGraph workflow")

    try:
        # Vytvoření StateGraph instance s explicitním typem
        workflow = StateGraph(State)

        # === WRAPPER FUNKCE PRO UZLY ===
        # Vytvoříme wrapper funkce které zajistí správnou kompatibilitu s LangGraph

        def safe_route_query(state: State) -> State:
            """Wrapper pro route_query s error handling."""
            try:
                result = route_query(state)
                # Ujistíme se, že result je dict a obsahuje jen povolená pole
                if isinstance(result, dict):
                    return {k: v for k, v in result.items() if hasattr(state, k)}
                return {}
            except Exception as e:
                logger.error(f"Chyba v route_query: {str(e)}")
                return {"error_state": {"error": str(e), "error_type": "route_error"}}

        def safe_prepare_company_query(state: State) -> State:
            """Wrapper pro prepare_company_query s error handling."""
            try:
                result = prepare_company_query(state)
                if isinstance(result, dict):
                    return {k: v for k, v in result.items() if hasattr(state, k)}
                return {}
            except Exception as e:
                logger.error(f"Chyba v prepare_company_query: {str(e)}")
                return {"error_state": {"error": str(e), "error_type": "prepare_error"}}

        def safe_retrieve_additional_company_data(state: State) -> State:
            """Wrapper pro retrieve_additional_company_data s error handling."""
            try:
                result = retrieve_additional_company_data(state)
                if isinstance(result, dict):
                    return {k: v for k, v in result.items() if hasattr(state, k)}
                return {}
            except Exception as e:
                logger.error(f"Chyba v retrieve_additional_company_data: {str(e)}")
                return {
                    "error_state": {"error": str(e), "error_type": "retrieve_error"}
                }

        def safe_analyze_company_data(state: State) -> State:
            """Wrapper pro analyze_company_data s error handling."""
            try:
                result = analyze_company_data(state)
                if isinstance(result, dict):
                    return {k: v for k, v in result.items() if hasattr(state, k)}
                return {}
            except Exception as e:
                logger.error(f"Chyba v analyze_company_data: {str(e)}")
                return {
                    "error_state": {"error": str(e), "error_type": "analysis_error"}
                }

        # === PŘIDÁNÍ UZLŮ ===

        # Krok 1: Analýza dotazu a určení typu
        workflow.add_node("route_query", safe_route_query)

        # Krok 2: Příprava dotazu a načtení základních dat
        workflow.add_node("prepare_company_query", safe_prepare_company_query)

        # Krok 3: Načtení dodatečných dat podle typu analýzy
        workflow.add_node(
            "retrieve_additional_company_data", safe_retrieve_additional_company_data
        )

        # Krok 4: Analýza dat podle typu
        workflow.add_node("analyze_company_data", safe_analyze_company_data)

        # Krok 5: Formátování výsledné odpovědi
        workflow.add_node("format_response_node", format_response_node)

        # Uzel pro zpracování chyb
        workflow.add_node("error_node", handle_error_state)

        # === NASTAVENÍ VSTUPNÍHO BODU ===
        workflow.set_entry_point("route_query")

        # === PŘIDÁNÍ HRAN A PODMÍNĚNÉHO VĚTVENÍ ===

        # Z route_query -> kontrola chyb -> prepare_company_query nebo error_node
        workflow.add_conditional_edges(
            "route_query",
            check_for_errors,
            {"error": "error_node", "continue": "prepare_company_query"},
        )

        # Z prepare_company_query -> kontrola chyb -> retrieve_additional_company_data nebo error_node
        workflow.add_conditional_edges(
            "prepare_company_query",
            check_for_errors,
            {"error": "error_node", "continue": "retrieve_additional_company_data"},
        )

        # Z retrieve_additional_company_data -> kontrola chyb -> analyze_company_data nebo error_node
        workflow.add_conditional_edges(
            "retrieve_additional_company_data",
            check_for_errors,
            {"error": "error_node", "continue": "analyze_company_data"},
        )

        # Z analyze_company_data -> kontrola chyb -> format_response_node nebo error_node
        workflow.add_conditional_edges(
            "analyze_company_data",
            check_for_errors,
            {"error": "error_node", "continue": "format_response_node"},
        )

        # Z format_response_node a error_node -> END
        workflow.add_edge("format_response_node", END)
        workflow.add_edge("error_node", END)

        # Kompilace workflow
        compiled_graph = workflow.compile()

        logger.info("✅ Explicitní StateGraph workflow úspěšně vytvořen")
        return compiled_graph

    except Exception as e:
        logger.error(f"Chyba při vytváření StateGraph: {str(e)}")
        logger.error("Podrobnosti chyby:", exc_info=True)
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
    Vytvoří a vrátí explicitní StateGraph workflow pro Memory Agent.

    Tato funkce používá nový explicitní StateGraph workflow místo ReAct agenta.
    Při chybě se může fallback na původní ReAct agenta.

    Returns:
        Zkompilovaný StateGraph workflow
    """
    try:
        logger.info("Vytvářím explicitní StateGraph workflow")
        return create_explicit_stategraph()
    except Exception as e:
        logger.error(f"Chyba při vytváření explicitního StateGraph: {str(e)}")
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
        logger.error(f"Nelze vytvořit graf pro deployment: {str(e)}")
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
    "create_explicit_stategraph",
    "create_react_agent_legacy",
    "get_memory_agent_stategraph",
    "get_graph_for_deployment",
    "create_placeholder_graph",
]

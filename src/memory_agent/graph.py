"""
Memory Agent pomocí LangGraph create_react_agent.

Minimální implementace podle LangGraph dokumentace s podporou pro node-specific assistant settings.

"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from .analyzer import analyze_company
from .api_validation import diagnose_api_key_issue, get_validated_openai_api_key
from .configuration import Configuration
from .node_config import export_studio_config, validate_node_configs
from .prompts import SYSTEM_PROMPT, PromptRegistry


def create_memory_agent():
    """
    Vytvoří Memory Agent pomocí LangGraph create_react_agent.

    Obsahuje node-specific assistant settings pro LangGraph Studio.


    Podporuje editaci promptů v LangGraph Studio:
    1. Přímou editaci uzlů
    2. LangSmith Playground integraci


    Returns:
        Nakonfigurovaný agent připravený k použití
    """
    # Validate and retrieve OpenAI API key from environment variables
    try:
        get_validated_openai_api_key()
    except EnvironmentError as e:
        # Provide detailed diagnosis
        diagnosis = diagnose_api_key_issue()
        raise EnvironmentError(f"{str(e)}\n\n{diagnosis}")

    # Validace node konfigurací pro LangGraph Studio
    validation_result = validate_node_configs()
    if not validation_result["valid"]:
        print(
            f"Warning: Node configuration validation failed: {validation_result['errors']}"
        )

    # Nastavení modelu pomocí string syntax (preferovaný způsob podle dokumentace)
    model = "openai:gpt-4"

    # Nastavení checkpointeru pro persistenci
    checkpointer = InMemorySaver()

    # Získání system promptu z PromptRegistry pro centralizovanou správu
    system_prompt = PromptRegistry.get_prompt("system_prompt") or SYSTEM_PROMPT

    # Kombinace s business intelligence instrukcemi
    enhanced_prompt = (
        f"{system_prompt}\n\n"
        "Use the analyze_company tool to get detailed information about companies "
        "and provide structured, insightful analysis based on the retrieved data."
    )

    # Vytvoření agenta s tool funkcí a enhanced prompt
    agent = create_react_agent(
        model=model,
        tools=[analyze_company],
        prompt=enhanced_prompt,
        checkpointer=checkpointer,
        config_schema=Configuration,
    )

    # Ponechání čistého grafu bez speciálních atributů pro LangGraph API server
    # Studio konfigurace je dostupná přes standalone funkce níže

    return agent


# Lazy initialization pro development/testing
def get_memory_agent():
    """Vrátí memory agent s lazy initialization."""
    if not hasattr(get_memory_agent, "_agent"):
        get_memory_agent._agent = create_memory_agent()
    return get_memory_agent._agent


# Para LangGraph Platform deployment - crear un graf que expone el schema incluso sin API keys
def create_schema_graph():
    """
    Crear un graph básico que expone el configuration schema sin necesidad de API keys.
    Usado por LangGraph Platform para introspección del schema.
    """
    try:
        # Intenta crear el agent completo
        return create_memory_agent()
    except EnvironmentError:
        # Si faltan API keys, crear un graph minimal solo para exponer el schema
        from langgraph.graph import MessagesState, StateGraph

        def placeholder_node(state: MessagesState) -> MessagesState:
            """Placeholder node for schema introspection."""
            return {"messages": []}

        # Crear un StateGraph básico con configuration schema
        workflow = StateGraph(MessagesState, config_schema=Configuration)
        workflow.add_node("placeholder", placeholder_node)
        workflow.set_entry_point("placeholder")
        workflow.set_finish_point("placeholder")

        return workflow.compile()


# Para LangGraph Platform deployment - solo intentar crear si el API key está disponible
try:
    memory_agent = create_memory_agent()
    # Alias para compatibilidad con langgraph.json
    graph = memory_agent
except EnvironmentError:

    # Durante testing o cuando no hay API key, usar None
    memory_agent = None
    graph = None


def get_node_assistant_settings():
    """
    Vrátí assistant settings pro jednotlivé nodes v grafu.
    Tato funkce odpovídá na otázku LangGraph Studio:
    "Have assistant settings that are specific to a node in your graph?"

    Returns:
        Dict obsahující assistant settings pro každý node
    """
    # Statická konfigurace node assistant settings
    return {
        "main_agent": {
            "model": "openai:gpt-4",
            "temperature": 0.1,
            "system_prompt": "You are a helpful business intelligence assistant.",
            "tools": ["analyze_company"],
            "description": "Main ReAct agent for company analysis",
        },
        "analysis_node": {
            "model": "openai:gpt-4",
            "temperature": 0.0,
            "system_prompt": "You are a specialized business analyst. Provide structured, data-driven analysis.",
            "tools": ["analyze_company"],
            "description": "Specialized analysis node for company data processing",
        },
        "data_node": {
            "model": "openai:gpt-3.5-turbo",
            "temperature": 0.0,
            "system_prompt": "You are a data loading assistant. Focus on efficient data retrieval and validation.",
            "tools": ["analyze_company"],
            "description": "Data loading and preprocessing node",
        },
    }


def get_studio_config():
    """
    Vrátí kompletní konfiguraci pro LangGraph Studio.

    Returns:
        Dict s konfigurací kompatibilní s LangGraph Studio
    """
    # Export z node_config modulu
    return export_studio_config()

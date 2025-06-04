"""
Memory Agent pomocí LangGraph create_react_agent.
Minimální implementace podle LangGraph dokumentace.
"""

import os
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from .analyzer import analyze_company
from .configuration import Configuration


def create_memory_agent():
    """
    Vytvoří Memory Agent pomocí LangGraph create_react_agent.

    Returns:
        Nakonfigurovaný agent připravený k použití
    """
    # Retrieve OpenAI API key from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    # Nastavení modelu pomocí string syntax (preferovaný způsob podle dokumentace)
    model = "openai:gpt-4"

    # Nastavení checkpointeru pro persistenci
    checkpointer = InMemorySaver()

    # Vytvoření agenta s tool funkcí, string syntax pro model a config schema
    agent = create_react_agent(
        model=model,
        tools=[analyze_company],
        prompt="You are a helpful business intelligence assistant. Use the analyze_company tool to get information about companies and provide detailed, structured analysis based on the retrieved data.",
        checkpointer=checkpointer,
        config_schema=Configuration,
    )

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
        from langchain_core.runnables import RunnableLambda
        from langgraph.graph import StateGraph, MessagesState
        from typing import Literal
        
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
    # Durante schema introspection o cuando no hay API key, usar schema graph
    memory_agent = create_schema_graph()
    graph = memory_agent

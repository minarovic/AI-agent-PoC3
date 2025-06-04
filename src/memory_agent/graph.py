"""
Memory Agent pomocí LangGraph create_react_agent.
Minimální implementace podle LangGraph dokumentace.
"""

import os
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from .analyzer import analyze_company
from .api_validation import get_validated_openai_api_key, diagnose_api_key_issue


def create_memory_agent():
    """
    Vytvoří Memory Agent pomocí LangGraph create_react_agent.

    Returns:
        Nakonfigurovaný agent připravený k použití
    """
    # Validate and retrieve OpenAI API key from environment variables
    try:
        openai_api_key = get_validated_openai_api_key()
    except EnvironmentError as e:
        # Provide detailed diagnosis
        diagnosis = diagnose_api_key_issue()
        raise EnvironmentError(f"{str(e)}\n\n{diagnosis}")

    # Nastavení modelu pomocí string syntax (preferovaný způsob podle dokumentace)
    model = "openai:gpt-4"

    # Nastavení checkpointeru pro persistenci
    checkpointer = InMemorySaver()

    # Vytvoření agenta s tool funkcí a string syntax pro model
    agent = create_react_agent(
        model=model,
        tools=[analyze_company],
        prompt="You are a helpful business intelligence assistant. Use the analyze_company tool to get information about companies and provide detailed, structured analysis based on the retrieved data.",
        checkpointer=checkpointer,
    )

    return agent


# Lazy initialization pro development/testing
def get_memory_agent():
    """Vrátí memory agent s lazy initialization."""
    if not hasattr(get_memory_agent, "_agent"):
        get_memory_agent._agent = create_memory_agent()
    return get_memory_agent._agent


# Para LangGraph Platform deployment - solo intentar crear si el API key está disponible
try:
    memory_agent = create_memory_agent()
    # Alias para compatibilidad con langgraph.json
    graph = memory_agent
except EnvironmentError:
    # Durante testing o cuando no hay API key, usar None
    memory_agent = None
    graph = None

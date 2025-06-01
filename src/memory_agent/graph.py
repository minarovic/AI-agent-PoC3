"""
Memory Agent pomocí LangGraph create_react_agent.
Minimální implementace podle LangGraph dokumentace.
"""
import os
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from .analyzer import analyze_company

# Temporary OpenAI API key for testing - DELETE AFTER TESTING
os.environ["OPENAI_API_KEY"] = "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"


def create_memory_agent():
    """
    Vytvoří Memory Agent pomocí LangGraph create_react_agent.
    
    Returns:
        Nakonfigurovaný agent připravený k použití
    """
    # Nastavení modelu pomocí string syntax (preferovaný způsob podle dokumentace)
    model = "openai:gpt-4"
    
    # Nastavení checkpointeru pro persistenci
    checkpointer = InMemorySaver()
    
    # Vytvoření agenta s tool funkcí a string syntax pro model
    agent = create_react_agent(
        model=model,
        tools=[analyze_company],
        prompt="You are a helpful business intelligence assistant. Use the analyze_company tool to get information about companies and provide detailed, structured analysis based on the retrieved data.",
        checkpointer=checkpointer
    )
    
    return agent

# Lazy initialization pro development/testing
def get_memory_agent():
    """Vrátí memory agent s lazy initialization."""
    if not hasattr(get_memory_agent, '_agent'):
        get_memory_agent._agent = create_memory_agent()
    return get_memory_agent._agent

# Pro LangGraph Platform deployment
memory_agent = create_memory_agent()

# Alias pro kompatibilitu s langgraph.json
graph = memory_agent
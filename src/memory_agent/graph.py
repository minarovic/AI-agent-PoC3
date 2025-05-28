"""
Memory Agent pomocí LangGraph create_react_agent.
Minimální implementace podle LangGraph dokumentace.
"""
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from memory_agent.analyzer import analyze_company


def create_memory_agent():
    """
    Vytvoří Memory Agent pomocí LangGraph create_react_agent.
    
    Returns:
        Nakonfigurovaný agent připravený k použití
    """
    # Nastavení checkpointeru pro persistenci
    checkpointer = InMemorySaver()
    
    # Vytvoření agenta s tool funkcí
    agent = create_react_agent(
        model="openai:gpt-4",
        tools=[analyze_company],
        prompt="You are a helpful business intelligence assistant. Use the analyze_company tool to get information about companies and provide detailed, structured analysis based on the retrieved data.",
        checkpointer=checkpointer
    )
    
    return agent


# Vytvoření agenta pro nasazení na LangGraph Platform
memory_agent = create_memory_agent()

# Alias pro kompatibilitu s langgraph.json
graph = memory_agent
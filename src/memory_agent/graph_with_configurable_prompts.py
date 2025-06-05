"""
Enhanced Memory Agent with configurable prompts for LangGraph Studio.

This implementation demonstrates how to make prompts editable in LangGraph Studio using:
1. ConfigurableField for direct node editing
2. LangSmith Playground integration
"""

import os
from typing import Any, Dict, Sequence

from langchain_core.messages import BaseMessage
from langchain_core.runnables import ConfigurableField, RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from typing_extensions import Annotated, TypedDict

from .analyzer import analyze_company
from .prompts import SYSTEM_PROMPT, PromptRegistry


class ConfigurableState(TypedDict):
    """State for configurable agent with message history."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_configurable_memory_agent():
    """
    Create Memory Agent with configurable prompts for LangGraph Studio editing.

    This version supports:
    1. Direct prompt editing in Studio nodes
    2. LangSmith Playground integration
    3. Dynamic prompt updates through ConfigurableField

    Returns:
        Configured agent with editable prompts
    """
    # Retrieve OpenAI API key from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    # Create configurable LLM model
    # This allows model configuration in Studio
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        openai_api_key=openai_api_key,
    ).configurable_fields(
        model_name=ConfigurableField(id="model_name"),
        temperature=ConfigurableField(id="temperature"),
    )

    # Create agent with configurable components
    checkpointer = InMemorySaver()

    # Using the enhanced prompt system
    enhanced_prompt = (
        "You are a helpful business intelligence assistant specializing in company analysis. "
        "Use the analyze_company tool to get detailed information about companies and provide "
        "structured, insightful analysis based on the retrieved data. "
        f"Additional instructions: {SYSTEM_PROMPT}"
    )

    agent = create_react_agent(
        model=llm,
        tools=[analyze_company],
        prompt=enhanced_prompt,
        checkpointer=checkpointer,
    )

    return agent


def create_advanced_configurable_agent():
    """
    Create an advanced configurable agent with explicit prompt management.

    This version provides more granular control over prompt editing.
    """
    # Create StateGraph for more control
    workflow = StateGraph(ConfigurableState)

    def get_configurable_prompt(config: RunnableConfig = None) -> str:
        """Get prompt from configuration or default."""
        if config and config.get("configurable", {}).get("system_prompt"):
            return config["configurable"]["system_prompt"]
        return PromptRegistry.get_prompt("company_analysis") or SYSTEM_PROMPT

    def agent_node(
        state: ConfigurableState, config: RunnableConfig = None
    ) -> Dict[str, Any]:
        """Agent node with configurable prompt."""
        # Get current prompt configuration
        current_prompt = get_configurable_prompt(config)

        # Create LLM with current configuration
        llm = ChatOpenAI(
            model=(
                config.get("configurable", {}).get("model_name", "gpt-4")
                if config
                else "gpt-4"
            ),
            temperature=(
                config.get("configurable", {}).get("temperature", 0.1)
                if config
                else 0.1
            ),
        )

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools([analyze_company])

        # Process messages with current prompt
        messages = state["messages"]
        if not any(msg.type == "system" for msg in messages):
            from langchain_core.messages import SystemMessage

            messages = [SystemMessage(content=current_prompt)] + list(messages)

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def tools_node(state: ConfigurableState) -> Dict[str, Any]:
        """Tools execution node."""
        from langgraph.prebuilt import ToolNode

        tool_node = ToolNode([analyze_company])
        return tool_node.invoke(state)

    def should_continue(state: ConfigurableState) -> str:
        """Determine if we should continue or end."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "__end__"

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)

    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "__end__": "__end__"}
    )
    workflow.add_edge("tools", "agent")

    # Compile with checkpointer
    checkpointer = InMemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    return app


def create_prompt_editable_agent():
    """
    Create agent optimized for LangGraph Studio prompt editing.

    This combines the simplicity of create_react_agent with configurability.
    """
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    # Default prompts that can be edited in Studio
    default_prompts = {
        "system_prompt": SYSTEM_PROMPT,
        "company_analysis_prompt": PromptRegistry.get_prompt("company_analysis"),
        "error_handling_prompt": PromptRegistry.get_prompt("error_handling"),
    }

    # Create agent with prompt that references configurable fields
    agent = create_react_agent(
        model="openai:gpt-4",
        tools=[analyze_company],
        prompt=default_prompts["system_prompt"],
        checkpointer=InMemorySaver(),
    )

    # Add configuration metadata for Studio
    if hasattr(agent, "config"):
        agent.config = agent.config or {}
        agent.config.update(
            {
                "configurable": {
                    "system_prompt": {
                        "id": "system_prompt",
                        "name": "System Prompt",
                        "description": "Main system prompt for the agent",
                        "default": default_prompts["system_prompt"],
                    },
                    "analysis_style": {
                        "id": "analysis_style",
                        "name": "Analysis Style",
                        "description": "Style of analysis (detailed, summary, technical)",
                        "default": "detailed",
                    },
                    "response_format": {
                        "id": "response_format",
                        "name": "Response Format",
                        "description": "Format for responses (markdown, plain, json)",
                        "default": "markdown",
                    },
                }
            }
        )

    return agent


# Create the configurable agent instances
try:
    configurable_memory_agent = create_configurable_memory_agent()
    advanced_configurable_agent = create_advanced_configurable_agent()
    prompt_editable_agent = create_prompt_editable_agent()
except EnvironmentError:
    # During testing when API key is not available
    configurable_memory_agent = None
    advanced_configurable_agent = None
    prompt_editable_agent = None


# Utility functions for Studio integration
def update_agent_prompt(agent, new_prompt: str) -> bool:
    """
    Update agent prompt dynamically.

    Args:
        agent: The agent instance
        new_prompt: New system prompt text

    Returns:
        bool: True if update was successful
    """
    try:
        # Update the prompt in PromptRegistry
        PromptRegistry.update_prompt("system_prompt", new_prompt)
        return True
    except Exception as e:
        print(f"Error updating prompt: {e}")
        return False


def get_agent_configuration_schema() -> Dict[str, Any]:
    """
    Get the configuration schema for LangGraph Studio.

    Returns:
        Dict containing the configuration schema
    """
    return {
        "configurable": {
            "system_prompt": {
                "type": "string",
                "title": "System Prompt",
                "description": "The main system prompt that defines agent behavior",
                "default": SYSTEM_PROMPT,
            },
            "model_name": {
                "type": "string",
                "title": "Model Name",
                "description": "OpenAI model to use",
                "default": "gpt-4",
                "enum": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            },
            "temperature": {
                "type": "number",
                "title": "Temperature",
                "description": "Temperature for response generation",
                "default": 0.1,
                "minimum": 0.0,
                "maximum": 1.0,
            },
            "analysis_style": {
                "type": "string",
                "title": "Analysis Style",
                "description": "Style of company analysis",
                "default": "detailed",
                "enum": ["detailed", "summary", "technical", "executive"],
            },
        }
    }


def demonstrate_prompt_editing():
    """
    Demonstrate prompt editing capabilities for verification.
    """
    print("=== Demonstrating Prompt Editing Capabilities ===")

    # Show original prompt
    original_prompt = PromptRegistry.get_prompt("company_analysis")
    print(f"Original prompt (truncated): {original_prompt[:100]}...")

    # Update prompt
    new_prompt = """
    Provide a BRIEF executive summary analysis for company {company_name}.

    Focus on:
    - Key business metrics
    - Major risks and opportunities
    - Strategic recommendations

    Keep response under 200 words.
    """

    success = PromptRegistry.update_prompt("company_analysis", new_prompt)
    print(f"Prompt update successful: {success}")

    # Verify update
    updated_prompt = PromptRegistry.get_prompt("company_analysis")
    print(f"Updated prompt (truncated): {updated_prompt[:100]}...")

    return success


if __name__ == "__main__":
    # Demonstration of prompt editing
    demonstrate_prompt_editing()

    # Show configuration schema
    schema = get_agent_configuration_schema()
    print(f"\nConfiguration schema: {schema}")

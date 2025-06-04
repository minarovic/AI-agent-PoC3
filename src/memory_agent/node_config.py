"""
Node-specific assistant configurations for LangGraph Studio.

This module defines assistant settings that are specific to individual nodes
in the graph, as required by LangGraph Studio for proper operation.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class AssistantConfig:
    """Configuration for a specific assistant/node in the graph."""
    
    model: str = "openai:gpt-4"
    """The LLM model to use for this node."""
    
    temperature: float = 0.1
    """Temperature setting for the model."""
    
    max_tokens: Optional[int] = None
    """Maximum tokens for model responses."""
    
    system_prompt: Optional[str] = None
    """Node-specific system prompt."""
    
    tools: List[str] = field(default_factory=list)
    """List of tools available to this node."""
    
    timeout: int = 30
    """Timeout in seconds for this node."""
    
    retries: int = 3
    """Number of retries for this node."""


@dataclass
class NodeConfig:
    """Complete configuration for a graph node."""
    
    name: str
    """Name of the node."""
    
    description: str
    """Description of what this node does."""
    
    assistant: AssistantConfig
    """Assistant configuration for this node."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata for the node."""


# Default configurations for different types of nodes
DEFAULT_ASSISTANT_CONFIG = AssistantConfig(
    model="openai:gpt-4",
    temperature=0.1,
    system_prompt="You are a helpful business intelligence assistant.",
    tools=["analyze_company"]
)

ANALYSIS_ASSISTANT_CONFIG = AssistantConfig(
    model="openai:gpt-4",
    temperature=0.0,  # More deterministic for analysis
    system_prompt="You are a specialized business analyst. Provide structured, data-driven analysis.",
    tools=["analyze_company"]
)

ROUTER_ASSISTANT_CONFIG = AssistantConfig(
    model="openai:gpt-3.5-turbo",  # Faster model for routing decisions
    temperature=0.0,
    system_prompt="You are a routing assistant. Determine the appropriate analysis type based on user queries.",
    tools=[]
)

# Node configurations for the memory agent graph
NODE_CONFIGURATIONS: Dict[str, NodeConfig] = {
    "agent": NodeConfig(
        name="agent",
        description="Main ReAct agent for company analysis",
        assistant=DEFAULT_ASSISTANT_CONFIG,
        metadata={
            "type": "react_agent",
            "role": "primary",
            "capabilities": ["company_analysis", "data_retrieval", "response_generation"]
        }
    ),
    
    "analyze_node": NodeConfig(
        name="analyze_node", 
        description="Specialized analysis node for company data processing",
        assistant=ANALYSIS_ASSISTANT_CONFIG,
        metadata={
            "type": "analysis",
            "role": "secondary",
            "capabilities": ["data_analysis", "pattern_recognition"]
        }
    ),
    
    "load_data_node": NodeConfig(
        name="load_data_node",
        description="Data loading and preprocessing node", 
        assistant=AssistantConfig(
            model="openai:gpt-3.5-turbo",
            temperature=0.0,
            system_prompt="You are a data loading assistant. Focus on efficient data retrieval and validation.",
            tools=["analyze_company"]
        ),
        metadata={
            "type": "data_loader",
            "role": "utility",
            "capabilities": ["data_loading", "validation"]
        }
    ),
    
    "format_response_node": NodeConfig(
        name="format_response_node",
        description="Response formatting and presentation node",
        assistant=AssistantConfig(
            model="openai:gpt-4",
            temperature=0.3,  # Slightly more creative for formatting
            system_prompt="You are a presentation assistant. Format data into clear, professional responses.",
            tools=[]
        ),
        metadata={
            "type": "formatter",
            "role": "utility", 
            "capabilities": ["formatting", "presentation"]
        }
    )
}


def get_node_config(node_name: str) -> Optional[NodeConfig]:
    """
    Get configuration for a specific node.
    
    Args:
        node_name: Name of the node
        
    Returns:
        NodeConfig if found, None otherwise
    """
    return NODE_CONFIGURATIONS.get(node_name)


def get_assistant_config(node_name: str) -> Optional[AssistantConfig]:
    """
    Get assistant configuration for a specific node.
    
    Args:
        node_name: Name of the node
        
    Returns:
        AssistantConfig if found, None otherwise
    """
    node_config = get_node_config(node_name)
    return node_config.assistant if node_config else None


def list_configured_nodes() -> List[str]:
    """
    Get list of all configured node names.
    
    Returns:
        List of node names that have configurations
    """
    return list(NODE_CONFIGURATIONS.keys())


def validate_node_configs() -> Dict[str, Any]:
    """
    Validate all node configurations.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "node_count": len(NODE_CONFIGURATIONS)
    }
    
    for node_name, config in NODE_CONFIGURATIONS.items():
        # Validate model format
        if not config.assistant.model or ":" not in config.assistant.model:
            results["errors"].append(f"Node {node_name}: Invalid model format")
            results["valid"] = False
            
        # Validate temperature range
        if not (0.0 <= config.assistant.temperature <= 2.0):
            results["warnings"].append(f"Node {node_name}: Temperature outside recommended range")
            
        # Validate required fields
        if not config.name or not config.description:
            results["errors"].append(f"Node {node_name}: Missing required fields")
            results["valid"] = False
    
    return results


# Export configuration for LangGraph Studio
def export_studio_config() -> Dict[str, Any]:
    """
    Export configuration in format expected by LangGraph Studio.
    
    Returns:
        Dictionary with studio-compatible configuration
    """
    studio_config = {
        "nodes": {},
        "assistants": {},
        "metadata": {
            "version": "1.0",
            "description": "Memory Agent node configurations for LangGraph Studio",
            "node_count": len(NODE_CONFIGURATIONS)
        }
    }
    
    for node_name, config in NODE_CONFIGURATIONS.items():
        # Node configuration
        studio_config["nodes"][node_name] = {
            "description": config.description,
            "metadata": config.metadata,
            "assistant_ref": f"{node_name}_assistant"
        }
        
        # Assistant configuration  
        studio_config["assistants"][f"{node_name}_assistant"] = {
            "model": config.assistant.model,
            "temperature": config.assistant.temperature,
            "max_tokens": config.assistant.max_tokens,
            "system_prompt": config.assistant.system_prompt,
            "tools": config.assistant.tools,
            "timeout": config.assistant.timeout,
            "retries": config.assistant.retries
        }
    
    return studio_config
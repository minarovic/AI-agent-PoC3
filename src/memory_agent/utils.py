"""
Utility functions for Memory Agent.

Tento modul obsahuje obecné utility funkce používané v Memory Agent.
"""

from typing import Tuple, Optional, Dict, Any


def split_model_and_provider(model_name: str) -> Tuple[Optional[str], str]:
    """
    Split a model name into provider and model parts.
    
    Args:
        model_name: Model name string, optionally with provider (e.g. "anthropic/claude-3-sonnet-20240229")
        
    Returns:
        Tuple of (provider, model_name), where provider may be None if not specified
    """
    if "/" in model_name:
        provider, model = model_name.split("/", 1)
        return provider, model
    return None, model_name


def create_mcp_connector_from_config(config_dict: Dict[str, Any]) -> Any:
    """
    Vytvoří instanci MockMCPConnector z konfiguračního slovníku.
    
    Tato funkce je užitečná pro LangGraph Platform, kde potřebujeme
    vytvářet instance z serializovaných konfigurací.
    
    Args:
        config_dict: Konfigurační slovník obsahující data_path
        
    Returns:
        Any: Nová instance MockMCPConnector
    """
    from memory_agent.tools import MockMCPConnector
    from memory_agent.schema import MockMCPConnectorConfig
    
    # Vytvoříme Pydantic model z slovníku
    if isinstance(config_dict, dict):
        config = MockMCPConnectorConfig(**config_dict)
    else:
        config = config_dict
    
    # Vytvoříme instanci konektoru
    return MockMCPConnector(data_path=config.data_path)

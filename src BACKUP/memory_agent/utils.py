"""
Pomocné utility funkce pro Memory Agent.

Tento modul obsahuje pomocné funkce pro práci s modely, konfigurací
a dalšími komponentami Memory Agenta.
"""

from typing import Dict, Any, Tuple, Optional, Union
from memory_agent.schema import MockMCPConnectorConfig
from memory_agent.tools import MockMCPConnector

def split_model_and_provider(model_name: str) -> Tuple[str, str]:
    """
    Rozdělí název modelu na poskytovatele a název modelu.
    
    Args:
        model_name: Název modelu ve formátu "poskytovatel:model"
        
    Returns:
        Tuple obsahující (poskytovatel, model)
    """
    if ":" in model_name:
        provider, model = model_name.split(":", 1)
        return provider, model
    else:
        # Pro případy bez explicitního poskytovatele předpokládáme OpenAI
        return "openai", model_name

def create_mcp_connector_from_config(config_dict: Union[Dict[str, Any], MockMCPConnectorConfig]) -> MockMCPConnector:
    """
    Vytvoří instanci MockMCPConnector z konfiguračního objektu.
    
    Args:
        config_dict: Konfigurační slovník nebo instance MockMCPConnectorConfig
        
    Returns:
        Instance MockMCPConnector
    """
    if isinstance(config_dict, dict):
        config = MockMCPConnectorConfig(**config_dict)
    else:
        config = config_dict
    
    return MockMCPConnector(data_path=config.data_path)
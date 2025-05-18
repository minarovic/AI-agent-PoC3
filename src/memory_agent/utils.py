"""
Utility functions for Memory Agent.

Tento modul obsahuje obecné utility funkce používané v Memory Agent.
"""

from typing import Tuple, Optional


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

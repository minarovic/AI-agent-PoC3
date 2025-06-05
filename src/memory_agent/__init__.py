"""Memory Agent package."""

# Conditional imports to avoid API key requirement during development
try:
    from .graph import get_node_assistant_settings, get_studio_config, memory_agent
    from .node_config import export_studio_config, validate_node_configs

    __all__ = [
        "memory_agent",
        "get_node_assistant_settings",
        "get_studio_config",
        "export_studio_config",
        "validate_node_configs",
    ]
except Exception:
    # For development/testing without API keys
    __all__ = []

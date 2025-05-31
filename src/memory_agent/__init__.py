"""Memory Agent package."""

# Conditional imports to avoid API key requirement during development
try:
    from .graph import memory_agent
    __all__ = ["memory_agent"]
except Exception:
    # For development/testing without API keys
    __all__ = []

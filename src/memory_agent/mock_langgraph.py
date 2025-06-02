"""
Mock implementace pro langgraph moduly pro účely testování.

Tento soubor definuje náhradní implementace pro langgraph moduly,
které mohou být potřebné pro testování.
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar


# Mock pro langgraph.graph.add_messages
def add_messages(
    left: Optional[List[Any]] = None, right: Optional[List[Any]] = None
) -> List[Any]:
    """Mock implementace pro add_messages."""
    if left is None:
        left = []
    if right is None:
        right = []

    return left + right


# Mock pro další funkce z langgraph, když budou potřeba

# Exportované symboly
__all__ = ["add_messages"]

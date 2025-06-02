"""
Jednoduchý test pro kontrolu syntaxe a importů v kódu.
Tento test nevyžaduje API klíče a může běžet na CI.
"""

import importlib
import os
import sys
import pytest


def test_all_modules_importable():
    """Test, že všechny Python moduly v src lze importovat."""
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
    )

    # Přidání src do pythonpath pro import
    sys.path.insert(0, os.path.dirname(src_dir))

    # Seznam všech .py souborů
    importable_modules = []
    for root, _, files in os.walk(src_dir):
        package_path = os.path.relpath(root, os.path.dirname(src_dir)).replace(
            os.sep, "."
        )
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                module_name = file[:-3]
                full_module_name = (
                    f"{package_path}.{module_name}"
                    if package_path != "."
                    else module_name
                )
                importable_modules.append(full_module_name)

    # Testování, že každý modul lze importovat
    for module_name in importable_modules:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            pytest.fail(f"Modul {module_name} nelze importovat: {str(e)}")


def test_package_imports():
    """Test, že základní balíček lze importovat."""
    try:
        import memory_agent  # noqa: F401
        assert memory_agent is not None
    except ImportError as e:
        pytest.fail(f"Nelze importovat memory_agent: {str(e)}")


def test_graph_exports():
    """Test, že graph.py exportuje potřebné objekty."""
    try:
        from memory_agent.graph import memory_agent, graph  # noqa: F401
        assert memory_agent is not None
        assert graph is not None
    except ImportError as e:
        pytest.fail(
            f"Nelze importovat memory_agent a graph z memory_agent.graph: {str(e)}"
        )

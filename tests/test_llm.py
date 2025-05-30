"""
Test pro kontrolu LLM funkcionality a správné struktury ReAct agenta.
Test simuluje LLM volání bez potřeby skutečných API klíčů.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Přidání src do pythonpath pro import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# Mock třídy a funkce
class MockChatModel:
    def __init__(self, *args, **kwargs):
        pass
    
    def invoke(self, *args, **kwargs):
        return MagicMock()

class MockResponse:
    def __init__(self, content=None, additional_kwargs=None):
        self.content = content or "To analyze this company, I need to gather information."
        self.additional_kwargs = additional_kwargs or {"tool_calls": [{"name": "analyze_company", "args": {"query": "example company"}}]}

def test_agent_structure():
    """Test, že agent má správnou strukturu a může být vytvořen."""
    from memory_agent.graph import create_memory_agent, memory_agent, graph
    
    # Ověření, že agent a graph objekty existují
    assert memory_agent is not None
    assert graph is not None
    
    # Ověření, že create_memory_agent je volatelná funkce
    assert callable(create_memory_agent)

@patch("langgraph.prebuilt.create_react_agent")
def test_create_react_agent_called(mock_create_react_agent):
    """Test, že create_react_agent je volán se správnými parametry."""
    mock_create_react_agent.return_value = MagicMock()
    
    from memory_agent.graph import create_memory_agent
    
    # Zavolání testované funkce
    create_memory_agent()
    
    # Ověření, že create_react_agent byl volán
    mock_create_react_agent.assert_called_once()
    
    # Ověření, že má správné parametry (bez kontroly konkrétních hodnot)
    args, kwargs = mock_create_react_agent.call_args
    assert "model" in kwargs
    assert "tools" in kwargs
    assert "prompt" in kwargs
    assert "checkpointer" in kwargs

@patch("langchain.chat_models.base._init_chat_model_helper")
@patch("langchain.chat_models.base.init_chat_model")
def test_agent_initialization(mock_init_chat_model, mock_init_chat_model_helper):
    """Test, že agent inicializace správně nastaví model."""
    # Mock pro init_chat_model
    mock_init_chat_model.return_value = MockChatModel()
    mock_init_chat_model_helper.return_value = MockChatModel()
    
    # Import musí být až po nastavení mocků
    from memory_agent.graph import create_memory_agent
    
    # Tvorba agenta by měla proběhnout bez chyby
    try:
        agent = create_memory_agent()
        assert agent is not None
    except Exception as e:
        pytest.fail(f"create_memory_agent vyvolal výjimku: {str(e)}")

@patch("memory_agent.tools.MockMCPConnector")
def test_analyze_company_tool(mock_connector):
    """Test, že analyze_company tool funguje správně."""
    # Mock pro MockMCPConnector
    connector_instance = MagicMock()
    mock_connector.return_value = connector_instance
    
    # Mock návratových hodnot pro metody conectoru
    connector_instance.get_company_by_name.return_value = {"id": "123", "name": "Test Company"}
    connector_instance.get_company_financials.return_value = {"revenue": 1000000}
    connector_instance.get_company_relationships.return_value = [{"type": "supplier", "entity": "Other Company"}]
    
    # Import funkce analyze_company
    from memory_agent.analyzer import analyze_company
    
    # Test volání
    result = analyze_company("Test Company")
    
    # Ověření, že výsledek je string (JSON)
    assert isinstance(result, str)
    
    # Ověření, že connector byl volán
    connector_instance.get_company_by_name.assert_called_once_with("Test Company")
    connector_instance.get_company_financials.assert_called_once()
    connector_instance.get_company_relationships.assert_called_once()

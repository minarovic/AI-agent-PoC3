"""
Test pro ověření správné funkčnosti API volání OpenAI modelu.
Tento test předpokládá, že API klíče jsou dostupné v GitHub secrets.
"""

import os
import sys
import pytest
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Přidání src do pythonpath pro import
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)


def test_openai_api_connection():
    """Test, že můžeme úspěšně volat OpenAI API."""
    try:
        # Předpokládá se, že OPENAI_API_KEY je nastaven v prostředí
        # V GitHub Actions to bude nastaveno z secrets
        chat_model = ChatOpenAI(model="gpt-3.5-turbo")

        # Jednoduché API volání
        response = chat_model.invoke([HumanMessage(content="Say hello")])

        # Ověření, že odpověď není prázdná
        assert response.content.strip(), "Odpověď od OpenAI API je prázdná"
        print(f"OpenAI API odpověď: {response.content}")
    except Exception as e:
        pytest.fail(f"OpenAI API volání selhalo: {str(e)}")


def test_memory_agent_imports():
    """Test, že memory_agent lze importovat a má očekávaná rozhraní."""
    try:
        from memory_agent.graph import memory_agent

        # Ověření, že memory_agent má očekávané metody
        assert hasattr(memory_agent, "invoke"), "memory_agent nemá metodu invoke"
    except ImportError as e:
        pytest.fail(f"Nelze importovat memory_agent: {str(e)}")


def test_analyze_company_tool():
    """Test, že funkce analyze_company existuje a má správnou signaturu."""
    try:
        from memory_agent.analyzer import analyze_company
        import inspect

        # Ověření, že analyze_company je funkce s jedním parametrem
        sig = inspect.signature(analyze_company)
        assert len(sig.parameters) == 1, "analyze_company nemá očekávanou signaturu"

        # Test, že analyze_company vrací string při volání s dummy vstupem
        # Nezávisí přímo na API, protože používá mock data
        result = analyze_company("Test Company")
        assert isinstance(result, str), "analyze_company nevrací řetězec"
        assert len(result) > 0, "analyze_company vrací prázdný řetězec"
    except ImportError as e:
        pytest.fail(f"Nelze importovat analyze_company: {str(e)}")

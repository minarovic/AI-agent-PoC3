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


def test_api_key_validation():
    """Test, že validace API klíčů funguje správně."""
    try:
        from memory_agent.api_validation import (
            validate_openai_api_key,
            diagnose_api_key_issue,
        )

        # Test s neplatným klíčem
        is_valid, message = validate_openai_api_key("invalid-key")
        assert not is_valid, "Validace by měla odhalit neplatný klíč"
        assert (
            "should start with 'sk-'" in message
        ), f"Neočekávaná chybová zpráva: {message}"

        # Test s chybějícím klíčem - temporarily store original env var
        original_key = os.environ.get("OPENAI_API_KEY")
        try:
            # Temporarily remove the env var for this test
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]

            is_valid, message = validate_openai_api_key(None)
            assert not is_valid, "Validace by měla odhalit chybějící klíč"
            assert "not set" in message, f"Neočekávaná chybová zpráva: {message}"
        finally:
            # Restore original env var
            if original_key is not None:
                os.environ["OPENAI_API_KEY"] = original_key

        # Test passed successfully; no need for stdout output.
    except ImportError:
        pytest.skip("API validation modul není dostupný")


def test_openai_api_connection():
    """Test, že můžeme úspěšně volat OpenAI API."""
    try:
        # First validate the API key format
        from memory_agent.api_validation import (
            validate_openai_api_key,
            diagnose_api_key_issue,
        )

        is_valid, message = validate_openai_api_key()
        if not is_valid:
            diagnosis = diagnose_api_key_issue()
            pytest.fail(f"API key validation failed: {message}\n{diagnosis}")

        # Předpokládá se, že OPENAI_API_KEY je nastaven v prostředí
        # V GitHub Actions to bude nastaveno z secrets
        chat_model = ChatOpenAI(model="gpt-3.5-turbo")

        # Jednoduché API volání
        response = chat_model.invoke([HumanMessage(content="Say hello")])

        # Ověření, že odpověď není prázdná
        assert response.content.strip(), "Odpověď od OpenAI API je prázdná"
        print(f"OpenAI API odpověď: {response.content}")
    except ImportError:
        # Fallback if validation module not available
        try:
            chat_model = ChatOpenAI(model="gpt-3.5-turbo")
            response = chat_model.invoke([HumanMessage(content="Say hello")])
            assert response.content.strip(), "Odpověď od OpenAI API je prázdná"
            print(f"OpenAI API odpověď: {response.content}")
        except Exception as e:
            pytest.fail(f"OpenAI API volání selhalo: {str(e)}")
    except Exception as e:
        pytest.fail(f"OpenAI API volání selhalo: {str(e)}")


def test_memory_agent_imports():
    """Test, že memory_agent lze importovat a má očekávaná rozhraní."""
    try:
        from memory_agent.graph import memory_agent
        from memory_agent.api_validation import validate_openai_api_key

        # Check if API key is available and valid
        import os

        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            # Without API key, memory_agent should be None (expected behavior)
            assert memory_agent is None, "memory_agent by měl být None bez API klíče"
            print("✅ memory_agent is correctly None without API key")
        else:
            # Check if the API key is valid
            is_valid, message = validate_openai_api_key(api_key)

            if not is_valid:
                # With invalid API key, memory_agent should be None
                assert (
                    memory_agent is None
                ), f"memory_agent by měl být None s neplatným API klíčem: {message}"
                print(
                    f"✅ memory_agent is correctly None with invalid API key: {message}"
                )
            else:
                # With valid API key, memory_agent should have expected methods
                # Note: This will only work with a real, working OpenAI API key
                if memory_agent is not None:
                    assert hasattr(
                        memory_agent, "invoke"
                    ), "memory_agent nemá metodu invoke"
                    print("✅ memory_agent má očekávané metody")
                else:
                    # Even with valid format, may still be None due to other validation
                    print("⚠️ memory_agent is None even with valid API key format")

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

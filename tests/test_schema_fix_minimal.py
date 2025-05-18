#!/usr/bin/env python
"""
Minimální test pro ověření oprav schématu JSON pro LangGraph Platform.

Tento skript testuje:
1. Vytvoření State objektu s MockMCPConnectorConfig
2. Vytvoření MockMCPConnector z konfigurace
3. Serializaci konfigurace přes model_dump()
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Instalace závislostí, pokud chybí
try:
    import pydantic
except ImportError:
    print("Instaluji chybějící závislosti...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic", "langchain-core", "langgraph", "unidecode"])

# Přidání cesty k src adresáři do Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Import potřebných modulů
    from src.memory_agent.schema import MockMCPConnectorConfig
    from src.memory_agent.tools import MockMCPConnector
    from src.memory_agent.state import State
    
    # Test 1: Vytvoření a serializace MockMCPConnectorConfig
    def test_mcp_config():
        print("Test 1: Vytvoření a serializace MockMCPConnectorConfig")
        config = MockMCPConnectorConfig(data_path="/test/path")
        
        # Kontrola serializace
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict), "model_dump() by měl vrátit slovník"
        assert "data_path" in config_dict, "data_path chybí v serializovaném výstupu"
        assert config_dict["data_path"] == "/test/path", "Nesprávná hodnota data_path"
        
        print("[✅] MockMCPConnectorConfig lze serializovat")
        return config
    
    # Test 2: Vytvoření State s konfigurací
    def test_state_with_config(config):
        print("Test 2: Vytvoření State s konfigurací")
        state = State(mcp_connector_config=config, messages=[])
        
        # Kontrola get_mcp_connector metody
        connector = state.get_mcp_connector()
        assert isinstance(connector, MockMCPConnector), "get_mcp_connector() vrátil nesprávný typ"
        assert connector.data_path == "/test/path", "Nesprávná data_path v konektoru"
        
        print("[✅] State lze vytvořit s MockMCPConnectorConfig")
        print("[✅] State.get_mcp_connector() funguje správně")
    
    # Spuštění testů
    if __name__ == "__main__":
        print("Spouštím testy pro opravu JSON schématu...")
        config = test_mcp_config()
        test_state_with_config(config)
        print("Všechny testy prošly!")

except Exception as e:
    print(f"Chyba při testování: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

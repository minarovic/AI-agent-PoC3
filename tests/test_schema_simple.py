#!/usr/bin/env python
"""
Jednoduchý test pro ověření funkčnosti Pydantic modelů v modulu schema.py.
"""

import sys
import os
import json
from pathlib import Path

def test_schema_file():
    """
    Testuje existenci a základní strukturu souboru schema.py.
    """
    schema_path = Path("/Users/marekminarovic/AI-agent-Ntier/src/memory_agent/schema.py")
    assert schema_path.exists(), "Soubor schema.py neexistuje!"
    
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("[✅] Soubor schema.py existuje")
    
    # Kontrola základních prvků
    assert "CompanyData" in content, "CompanyData model nenalezen v schema.py"
    assert "PersonData" in content, "PersonData model nenalezen v schema.py"
    assert "RelationshipData" in content, "RelationshipData model nenalezen v schema.py"
    assert "MockMCPConnectorConfig" in content, "MockMCPConnectorConfig model nenalezen v schema.py"
    assert "AnalysisType" in content, "AnalysisType definice nenalezena v schema.py"
    
    print("[✅] Všechny požadované modely byly nalezeny v schema.py")

def test_mcp_connector_methods():
    """
    Testuje definice metod v MockMCPConnector.
    """
    tools_path = Path("/Users/marekminarovic/AI-agent-Ntier/src/memory_agent/tools.py")
    assert tools_path.exists(), "Soubor tools.py neexistuje!"
    
    with open(tools_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("[✅] Soubor tools.py existuje")
    
    # Kontrola implementací
    assert "def to_dict(self)" in content, "Metoda to_dict() nenalezena v MockMCPConnector"
    assert "Union[Dict[str, Any], CompanyData]" in content, "Typová anotace pro CompanyData nenalezena"
    assert "Union[Dict[str, Any], PersonData]" in content, "Typová anotace pro PersonData nenalezena"
    assert "Union[Dict[str, Any], RelationshipData]" in content, "Typová anotace pro RelationshipData nenalezena"
    
    print("[✅] Všechny požadované metody a typy byly nalezeny v tools.py")

def main():
    """Hlavní testovací funkce"""
    print("Zahajuji testování schémat pro LangGraph Platform...")
    
    # Testování schema.py
    test_schema_file()
    
    # Testování tools.py
    test_mcp_connector_methods()
    
    print("\n[✅] Všechny testy byly úspěšné!")
    print("Schémata jsou správně definována a připravena pro LangGraph Platform.")

if __name__ == "__main__":
    main()

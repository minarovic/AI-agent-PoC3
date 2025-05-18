"""
Test skript pro ověření funkčnosti schémat a serializace.

Tento skript testuje základní funkčnost modulu schema a třídy MockMCPConnector
s fokusem na správnou serializaci a deserializaci objektů.
"""

import json
import sys
from pathlib import Path

# Přidání cesty k projektu do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from memory_agent.schema import (
        CompanyData,
        PersonData, 
        RelationshipData,
        MockMCPConnectorConfig
    )
    from memory_agent.tools import MockMCPConnector
    
    print("1. Test importů: OK")
    
    # Test vytvoření konfigurace
    config = MockMCPConnectorConfig(data_path="/tmp/mock_data")
    print(f"2. Vytvoření konfigurace: {config}")
    
    # Test serializace konfigurace
    config_dict = config.model_dump()
    config_json = json.dumps(config_dict)
    print(f"3. Serializace konfigurace: {config_json}")
    
    # Test vytvoření konektoru
    connector = MockMCPConnector(data_path="/tmp/mock_data")
    print(f"4. Vytvoření konektoru: {connector}")
    
    # Test serializace konektoru
    connector_dict = connector.to_dict()
    connector_json = json.dumps(connector_dict)
    print(f"5. Serializace konektoru: {connector_json}")
    
    # Test vytvoření datových objektů
    company = CompanyData(id="test-1", name="Test Company")
    person = PersonData(id="test-2", name="Test Person")
    relationship = RelationshipData(
        source_id="test-1", 
        target_id="test-2",
        relationship_type="owns"
    )
    
    print(f"6. Vytvoření datových objektů: OK")
    print(f"   - Company: {company}")
    print(f"   - Person: {person}")
    print(f"   - Relationship: {relationship}")
    
    # Test serializace datových objektů
    company_json = json.dumps(company.model_dump())
    person_json = json.dumps(person.model_dump())
    relationship_json = json.dumps(relationship.model_dump())
    
    print(f"7. Serializace datových objektů: OK")
    
    # Test deserializace datových objektů
    company2 = CompanyData.model_validate_json(company_json)
    person2 = PersonData.model_validate_json(person_json)
    relationship2 = RelationshipData.model_validate_json(relationship_json)
    
    print(f"8. Deserializace datových objektů: OK")
    print(f"   - Company: {company2}")
    print(f"   - Person: {person2}")
    print(f"   - Relationship: {relationship2}")
    
    print("\nVšechny testy proběhly úspěšně!")
    
except Exception as e:
    print(f"CHYBA: {str(e)}")
    import traceback
    traceback.print_exc()

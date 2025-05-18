"""
Jednoduchý skript pro ověření, že synchronní wrapper analyze_query_sync funguje správně.
"""

import asyncio
from memory_agent.analyzer import analyze_query_sync
from memory_agent.tools import MockMCPConnector

def test_analyze_query_sync():
    """Test pro analyze_query_sync."""
    print("Spouštím test pro analyze_query_sync...")
    
    # Vytvoření instance MockMCPConnector
    mock_connector = MockMCPConnector(data_path="./mock_data")
    
    # Test s dotazem na společnost
    company_query = "Co je to MB TOOL?"
    company_result = analyze_query_sync(company_query, None, None, mock_connector)
    print(f"Dotaz společnosti: '{company_query}' → '{company_result}'")
    
    # Test s dotazem na osobu
    person_query = "Kdo je Jan Novák?"
    person_result = analyze_query_sync(person_query, None, None, mock_connector)
    print(f"Dotaz osoby: '{person_query}' → '{person_result}'")

    # Test s dotazem na vztah
    relationship_query = "Jaké jsou vztahy mezi MB TOOL a jeho dodavateli?"
    relationship_result = analyze_query_sync(relationship_query, None, None, mock_connector)
    print(f"Dotaz vztahů: '{relationship_query}' → '{relationship_result}'")

    # Test s obecným dotazem
    custom_query = "Jak se daří českému průmyslu?"
    custom_result = analyze_query_sync(custom_query, None, None, mock_connector)
    print(f"Obecný dotaz: '{custom_query}' → '{custom_result}'")
    
    print("Test dokončen.")

if __name__ == "__main__":
    test_analyze_query_sync()

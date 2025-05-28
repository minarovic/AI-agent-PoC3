#!/usr/bin/env python3
"""
Test pro ověření aktuálního stavu - zda analyze_query_sync vrací "company".
"""

import sys
import os

# Přidání src adresáře do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_analyze_query_sync():
    """Test funkce analyze_query_sync s dotazem 'MB TOOL'"""
    try:
        from memory_agent.analyzer import analyze_query_sync
        
        # Test dotaz z iterace 33
        test_query = "MB TOOL"
        result = analyze_query_sync(test_query)
        
        print(f"Dotaz: '{test_query}'")
        print(f"Výsledek: '{result}'")
        print(f"Typ výsledku: {type(result)}")
        
        # Kontrola, zda vrací "company"
        if result == "company":
            print("✅ ÚSPĚCH: Funkce vrací 'company' jak má")
            return True
        else:
            print(f"❌ PROBLÉM: Funkce vrací '{result}' místo 'company'")
            return False
            
    except Exception as e:
        print(f"❌ CHYBA při testu: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_route_query():
    """Test funkce route_query z graph_nodes.py"""
    try:
        from memory_agent.graph_nodes import route_query
        from memory_agent.state import State
        
        # Vytvoření testovacího stavu
        state = State()
        state.current_query = "MB TOOL"
        
        print(f"\n=== Test route_query ===")
        print(f"Vstupní dotaz: '{state.current_query}'")
        
        # Volání route_query
        result = route_query(state)
        
        print(f"Výsledek route_query: {result}")
        
        # Kontrola query_type
        query_type = result.get("query_type")
        print(f"query_type: '{query_type}'")
        
        if query_type == "company":
            print("✅ ÚSPĚCH: route_query vrací query_type: 'company'")
            return True
        else:
            print(f"❌ PROBLÉM: route_query vrací query_type: '{query_type}' místo 'company'")
            return False
            
    except Exception as e:
        print(f"❌ CHYBA při testu route_query: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Test aktuálního stavu ===")
    
    # Test 1: analyze_query_sync
    success1 = test_analyze_query_sync()
    
    # Test 2: route_query 
    success2 = test_route_query()
    
    # Celkový výsledek
    if success1 and success2:
        print(f"\n✅ VŠECHNY TESTY PROŠLY - problém je vyřešen!")
    else:
        print(f"\n❌ PROBLÉMY STÁLE EXISTUJÍ")
        if not success1:
            print("  - analyze_query_sync nevrací 'company'")
        if not success2:
            print("  - route_query nevrací správný query_type")
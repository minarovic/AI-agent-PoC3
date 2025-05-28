#!/usr/bin/env python3
"""
Přímý test funkce analyze_query_sync bez závislostí na LangGraph.
"""

def test_analyze_query_sync_direct():
    """Test funkce analyze_query_sync přímo ze souboru"""
    
    # Načtení obsahu analyzer.py
    with open('/Users/marekminarovic/AI-agent-Ntier/src/memory_agent/analyzer.py', 'r') as f:
        analyzer_content = f.read()
    
    print("=== Kontrola obsahu analyzer.py ===")
    
    # Hledání definice analyze_query_sync
    lines = analyzer_content.split('\n')
    
    found_function = False
    function_body = []
    inside_function = False
    
    for i, line in enumerate(lines, 1):
        if 'def analyze_query_sync(' in line:
            found_function = True
            inside_function = True
            function_body.append(f"{i}: {line}")
            print(f"✅ Nalezena funkce analyze_query_sync na řádku {i}")
            continue
            
        if inside_function:
            # Ukončení funkce = další def nebo konec souboru
            if line.strip().startswith('def ') and not line.strip().startswith('def analyze_query_sync'):
                inside_function = False
            else:
                function_body.append(f"{i}: {line}")
    
    if found_function:
        print("\n=== Obsah funkce analyze_query_sync ===")
        for line in function_body:
            print(line)
        
        # Kontrola, zda funkce vrací "company"
        function_code = '\n'.join([line.split(':', 1)[1] if ':' in line else line for line in function_body])
        
        if 'return "company"' in function_code:
            print("\n✅ OVĚŘENO: Funkce obsahuje 'return \"company\"'")
            return True
        else:
            print("\n❌ PROBLÉM: Funkce neobsahuje 'return \"company\"'")
            return False
    else:
        print("❌ Funkce analyze_query_sync nebyla nalezena!")
        return False

def check_imports_in_analyzer():
    """Kontrola importů v analyzer.py"""
    with open('/Users/marekminarovic/AI-agent-Ntier/src/memory_agent/analyzer.py', 'r') as f:
        content = f.read()
    
    print("\n=== Kontrola importů v analyzer.py ===")
    
    # Problematické importy
    problematic_imports = [
        'from langchain_anthropic import ChatAnthropic',
        'from langchain_openai import ChatOpenAI'
    ]
    
    for import_line in problematic_imports:
        if import_line in content:
            print(f"⚠️  NALEZEN: {import_line}")
        else:
            print(f"✅ CHYBÍ: {import_line}")

if __name__ == "__main__":
    print("=== Přímý test bez závislostí ===")
    
    # Test obsahu funkce
    success = test_analyze_query_sync_direct()
    
    # Kontrola importů
    check_imports_in_analyzer()
    
    if success:
        print(f"\n✅ FUNKCE JE SPRÁVNĚ IMPLEMENTOVÁNA")
        print("💡 Problém může být jinde nebo už je vyřešen")
    else:
        print(f"\n❌ FUNKCE NENÍ SPRÁVNĚ IMPLEMENTOVÁNA")
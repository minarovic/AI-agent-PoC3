# Zjednodušení analyzéru pomocí N8N přístupu

## Shrnutí změn
Analyzér v modulu `src/memory_agent/analyzer.py` byl zjednodušen s využitím přístupu inspirovaného z N8N. Hlavní změny:

1. **Odstranění složitých LCEL řetězců** - Původní implementace používala komplexní LCEL řetězce, fallbacky a asynchronní zpracování.
2. **Jednoduchý prompt-based přístup** - Nová implementace používá jednoduchý prompt ve formátu "Company Name; analysis_type".
3. **Spolehlivější detekce společností** - Vyřešen problém s detekcí společností v dotazech jako "Má MB TOOL nějaké sankce?".
4. **Žádné fallbacky na regex** - Veškerá detekce společností a typu analýzy je svěřena LLM s vhodným promptem.
5. **Zachování API kompatibility** - Funkce `analyze_query_sync` stále vrací stejné typy výsledků pro kompatibilitu s ostatními částmi aplikace.

## Použitý prompt
```
Analyze the user's input to extract company name and analysis type.

The format should follow the pattern: "Company Name; analysis_type"
Where analysis_type can be:
- risk_comparison (for risk analysis, compliance, sanctions, etc.)
- common_suppliers (for supplier relationships, supply chain, etc.)
- general (for general information about the company)

Examples:
- Input: "Find risks for Apple Inc"
  Output: "Apple Inc; risk_comparison"
  
- Input: "Show me suppliers for Samsung Electronics"
  Output: "Samsung Electronics; common_suppliers"
  
- Input: "I need information about Microsoft"
  Output: "Microsoft; general"

- Input: "Má MB TOOL nějaké sankce?"
  Output: "MB TOOL; risk_comparison"

- Input: "Jaké jsou vztahy mezi ŠKODA AUTO a jejími dodavateli?"
  Output: "ŠKODA AUTO; common_suppliers"

- Input: "Co je to Flídr plast?"
  Output: "Flídr plast; general"

Input: {query}

Only respond with the structured output in the format "Company Name; analysis_type" - no other text.
```

## Testování změn
Byly vytvořeny nové testy:
- `test_analyzer_direct.py` - Přímý test funkce `analyze_company_query` s Anthropic API
- `test_n8n_analyzer.py` - Test N8N přístupu k analýze dotazů
- `test_openai_analyzer.py` - Test s OpenAI API

Testy potvrzují, že nový přístup je efektivní pro detekci společností v různých typech dotazů, včetně problematických případů jako "Má MB TOOL nějaké sankce?".

## Postup integrace do hlavní větve
1. Zkontrolujte výsledky testů a ujistěte se, že všechny fungují správně.
2. V lokálním prostředí ověřte, že zjednodušený analyzér pracuje správně s ostatními komponenty (např. `graph_nodes.py`).
3. Proveďte merge větve `simplified-analyzer` do hlavní větve.
4. Po nasazení monitorujte výkon analyzéru, zejména správnou detekci společností a typů analýzy.

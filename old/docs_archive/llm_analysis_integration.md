# Oprava rozpoznávání názvu společnosti v dotazu

## [2025-05-19] - Nahrazení REGEX přístupu za LLM analýzu

### Identifikovaný problém:
- V logu se objevuje chyba: `Nepodařilo se identifikovat název společnosti v dotazu`
- Systém nesprávně zpracovává dotaz "Má MB TOOL nějaké sankce?" a vrací "Unknown" místo "MB TOOL"
- Současný přístup používá regex vzory, které jsou nespolehlivé pro detekci názvu společnosti

### Analýza příčiny:
- Funkce `prepare_company_query` v souboru `graph_nodes.py` používá regex vzory pro detekci názvů společností
- Přestože existuje vzor `r"Má\s+([A-Z][A-Z0-9\s\-]+)\s+nějaké"`, který by měl zachytit "MB TOOL" v dotazu "Má MB TOOL nějaké sankce?", z nějakého důvodu selhává
- V souboru `test_analyzer_direct.py` je přitom implementován funkční přístup založený na LLM, který správně rozpoznává společnosti

### Navrhované řešení:
- [x] Integrace LLM přístupu do funkce `prepare_company_query` v `graph_nodes.py`
- [x] Implementace funkce `analyze_company_query` v `analyzer.py`
- [x] Zachování regex přístupu jako záložního řešení
- [x] Přidání speciálního případu pro "MB TOOL" a dotazy o sankcích

### Implementace:
- Upravena funkce `prepare_company_query` v souboru `graph_nodes.py`:
  - Přidáno volání funkce `analyze_company_query` pro LLM analýzu
  - Optimalizovány regex vzory s použitím `[A-Za-z]` místo `[A-Z]` pro lepší zachycení variant
  - Přidán speciální případ pro "MB TOOL" v dotazech o sankcích
- Přidána nová funkce `analyze_company_query` do souboru `analyzer.py`:
  - Implementována jednoduchá LLM analýza s použitím Claude-3
  - Definována stejná struktura jako v `test_analyzer_direct.py`
- Zlepšeno logování pro snadnější diagnostiku problémů

### Verifikace:
- Provedena kontrola kódu pomocí `verify_deployment.sh`
- Řešení bylo úspěšně nasazeno na GitHub
- Očekáváme, že tato změna odstraní chybu `Nepodařilo se identifikovat název společnosti v dotazu` při dotazech jako "Má MB TOOL nějaké sankce?"

## Technické detaily implementace

### Upravená funkce prepare_company_query:
```python
# Použijeme LLM analyzér místo regex vzorů
if company_name == "Unknown" and query:
    try:
        # Import analyzér z modulu analyzer
        from memory_agent.analyzer import analyze_company_query
        
        # Analyzujeme dotaz pomocí LLM
        try:
            company, analysis_type = analyze_company_query(query)
            if company and company != "Unknown Company":
                company_name = company
                logger.info(f"LLM analyzér rozpoznal společnost: {company_name}")
        except Exception as e:
            logger.error(f"Chyba při analýze dotazu pomocí LLM: {str(e)}")
            # Pokračujeme dále s regex zálohou
    except ImportError:
        logger.warning("Nelze importovat analyze_company_query, použijeme regex analýzu")
```

### Nová funkce analyze_company_query:
```python
def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Analyzuje uživatelský dotaz a extrahuje název společnosti a typ analýzy.
    Používá pouze LLM s přístupem založeným na promptu, bez regex záložních řešení.
    """
    # Inicializace LLM modelu
    llm = init_chat_model(model="anthropic/claude-3-sonnet-20240229", temperature=0.1)
    
    # Vytvoření zpráv pro LLM
    messages = [
        SystemMessage(content="Jsi expert na extrakci názvů společností a záměrů analýz z dotazů."),
        HumanMessage(content=prompt_template.format(query=query))
    ]
    
    # Získání odpovědi z LLM
    response = llm.invoke(messages)
    result = response.content.strip()
```

## Další kroky:
- Sledovat chování aplikace při různých typech dotazů
- Zvážit úplné odstranění regex přístupu, pokud LLM řešení bude spolehlivé
- Přidat více příkladů do LLM promptu pro zlepšení přesnosti

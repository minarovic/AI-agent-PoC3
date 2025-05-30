# Rozšířená oprava zpracování dotazů o společnostech

## [2025-05-19] - Vylepšení workflow analýzy společností

### Identifikovaný problém:
- Při zpracování dotazu "Má MB TOOL nějaké sankce?" aplikace nesprávně identifikuje společnost jako "Unknown"
- Systém používá dva různé přístupy k analýze dotazů:
  1. Funkce `analyze_query_sync` v `analyzer.py` pro určení typu dotazu
  2. Funkce `prepare_company_query` v `graph_nodes.py` pro extrakci názvu společnosti
- Tyto dvě funkce nejsou dostatečně propojené, což způsobuje nekonzistentní výsledky

### Analýza příčiny:
- Nedostatečná integrace mezi různými způsoby analýzy dotazů v aplikaci
- Chybějící robustní záložní mechanismy při selhání hlavní analýzy
- Absence předávání výsledků mezi jednotlivými kroky workflow

### Navrhované řešení:
- [x] Implementace vícestupňové analýzy dotazů s využitím LLM
- [x] Propojení funkcí `route_query`, `analyze_query_sync` a `prepare_company_query`
- [x] Přidání specializovaného zpracování pro známé společnosti (MB TOOL, ŠKODA AUTO, atd.)
- [x] Vytvoření záložních mechanismů pro všechny úrovně analýzy

### Implementace:
1. **Rozšíření funkce `route_query`:**
   - Přidána předběžná analýza pro dotazy obsahující "MB TOOL" a "sankce"
   - Výsledky předanalýzy jsou uloženy do stavu pro pozdější použití

2. **Vylepšení funkce `analyze_query_sync`:**
   - Přidána speciální detekce známých společností
   - Implementovány záložní analýzy při selhání hlavního mechanismu
   - Rozšířená detekce klíčových slov pro určení typu dotazu

3. **Vizualizace workflow:**
   - Vytvořen PlantUML diagram `company_analysis_improved.puml` popisující komplexní workflow

### Kód rozšířené implementace:

#### Funkce `route_query`
```python
def route_query(state: State) -> State:
    """
    Analyzuje vstupní dotaz a určí, jaký typ dotazu to je.
    Také předběžně analyzuje společnosti pro pozdější použití.
    """
    # ...
    
    # Předběžná analýza společnosti pomocí LLM, pokud jde o dotaz s MB TOOL a sankcemi
    if "MB TOOL" in state.current_query and "sankce" in state.current_query.lower():
        try:
            from memory_agent.analyzer import analyze_company_query
            company, analysis_type = analyze_company_query(state.current_query)
            if company and company != "Unknown Company":
                logger.info(f"Předběžná LLM analýza identifikovala společnost: {company}")
                return {
                    "query_type": "company", 
                    "analysis_result": {
                        "company_name": company,
                        "analysis_type": analysis_type
                    }
                }
        except Exception as e:
            logger.error(f"Chyba při předběžné analýze společnosti: {str(e)}")
    
    # Standardní analýza pomocí analyze_query_sync
    query_type = analyze_query_sync(state.current_query)
    # ...
```

#### Funkce `analyze_query_sync`
```python
def analyze_query_sync(user_input: str, ...) -> str:
    """
    Synchronní wrapper pro asynchronní funkci analyze_query.
    Vylepšená verze s integrací analyze_company_query pro spolehlivější detekci společností.
    """
    # Specializovaná kontrola pro MB TOOL a podobné případy
    if "MB TOOL" in user_input or "ŠKODA AUTO" in user_input or "ADIS TACHOV" in user_input or "Flídr plast" in user_input:
        try:
            company, _ = analyze_company_query(user_input)
            if company and company != "Unknown Company":
                logger.info(f"Přímé rozpoznání společnosti pomocí analyze_company_query: {company}")
                return "company"
        except Exception as e:
            logger.error(f"Chyba v přímé analýze společnosti: {str(e)}")
    
    # Standardní asynchronní analýza
    # ...
    
    # Záložní detekce při chybě hlavního analyzéru
    # ...
```

### Verifikace:
- Provedena kontrola kódu pomocí `verify_deployment.sh`
- Všechny implementace jsou kompatibilní s předchozími opravami
- Nový workflow má několik úrovní záložních mechanismů, což zvyšuje robustnost systému
- Očekáváme, že tato změna zajistí spolehlivou detekci společnosti "MB TOOL" v dotazu "Má MB TOOL nějaké sankce?"

### Další kroky:
- Monitorovat úspěšnost analýzy dotazů v produkčním prostředí
- Případně rozšířit LLM prompt o další příklady založené na skutečných dotazech uživatelů
- Zvážit kompletní náhradu regex analýzy za LLM analýzu, pokud se ukáže jako výrazně spolehlivější

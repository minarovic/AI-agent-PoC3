# Deployment Plan for LangGraph Schema Fix

## Souhrn změn

Implementovali jsme řešení pro opravu chyby při generování JSON schémat pro LangGraph Platform, která se projevovala chybou:

```
Failed to get input schema for graph agent with error: `Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'memory_agent.tools.MockMCPConnector'>)
```

### Provedené změny:

1. **Úprava State třídy**:
   - Změneno `mcp_connector` na `mcp_connector_config`
   - Přidána metoda `get_mcp_connector()` pro vytváření instancí z konfigurace

2. **Vytvoření utility funkce**:
   - Přidána funkce `create_mcp_connector_from_config()` do utils.py

3. **Přidání synchronní verze analyze_query**:
   - Vytvořena synchronní verze `analyze_query` pro kompatibilitu s grafovými uzly
   - Původní asynchronní verze přejmenována na `analyze_query_async`

4. **Úprava route_query uzlu**:
   - Aktualizována logika pro správné zpracování výstupu z analyze_query

### Aktualizované soubory:
- `src/memory_agent/state.py`
- `src/memory_agent/utils.py`
- `src/memory_agent/analyzer.py`
- `src/memory_agent/graph_nodes.py`

## Deployment plán

1. **Vytvoř Git branch**:
   ```
   git checkout -b langraph-schema-fix
   ```

2. **Přidej změněné soubory**:
   ```
   git add src/memory_agent/state.py src/memory_agent/utils.py src/memory_agent/analyzer.py src/memory_agent/graph_nodes.py
   ```

3. **Commitu změny**:
   ```
   git commit -m "Fix LangGraph JSON schema generation"
   ```

4. **Push na GitHub**:
   ```
   git push origin langraph-schema-fix
   ```

5. **Lokální testování**:
   ```
   # Spustit lokální LangGraph server
   ./run_langgraph_dev.sh
   ```

6. **Merge do main branch**:
   Po úspěšném testování vytvořit Pull Request a sloučit do main branch

7. **Nasazení do produkce**:
   ```
   # Sestavení a nasazení na LangGraph Platform
   ./deploy_to_langgraph_platform.sh
   # Zvolit možnost 2 - Sestavení a nasazení na LangGraph Platform
   ```

## Verifikace nasazení

1. Zkontroluj logy po nasazení - měla by zmizet chyba "Cannot generate a JsonSchema"
2. Ověř, že API dokumentace se správně generuje v LangGraph Platform
3. Proveď smoke test konverzace s agentem přes LangGraph Platform UI

## Fallback plán

Pokud by řešení nefungovalo:
1. Vrátit změny (`git revert`)
2. Prozkoumat alternativní přístupy, např. úplná eliminace třídy MockMCPConnector a nahrazení funkcionálním přístupem

## Záznam změn

Tento dokument bude aktualizován s výsledky nasazení a případnými dodatečnými úpravami.


-----


# Kontrola stavu nasazení AI-agent-Ntier

## [2025-05-18] - Aktualizace: Oprava chyby indentace v Python kódu

### Nový problém: IndentationError v GitHub Action

GitHub Action selhal s chybou:
```
2025-05-18T12:59:49.7857827Z 1     E999 IndentationError: unexpected indent
```

### Provedené kroky pro řešení problému:

- [x] Identifikace problému: Nesprávně indentované řádky v souboru `src/memory_agent/analyzer.py`
- [x] Analýza příčiny: Pozůstatky kódu po přesunu definice `AnalysisResult` do `schema.py`
- [x] Odstranění nesprávně indentovaných řádků z `analyzer.py`
- [x] Přidání chybějících polí (`is_company_analysis` a `confidence`) do `AnalysisResult` v `schema.py`
- [x] Vytvoření dokumentace opravy v `deploy_logs/indentation_fix_18_05_2025.md`
- [ ] Ověření opravy pomocí nového běhu GitHub Action

## [2025-05-18] - Aktualizace: Oprava JSON Schema problému

### Nový problém: Failed to generate JSON Schema

LangGraph Platform reportoval chybu při generování JSON schématu pro grafy:
```
Failed to get input schema for graph agent with error: `Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'memory_agent.tools.MockMCPConnector'>)
```

### Provedené kroky pro řešení JSON Schema problému:

- [x] Identifikace problému: Nelze serializovat třídu MockMCPConnector do JSON schématu
- [x] Analýza příčiny: Přímá reference na instance třídy ve State objektu
- [x] Vytvoření Pydantic modelu MockMCPConnectorConfig pro konfiguraci konektoru
- [x] Refaktorování State třídy a nahrazení instance za konfigurační objekt
- [x] Přidání metody get_mcp_connector() pro vytváření instancí z konfigurace
- [x] Implementace utility funkce create_mcp_connector_from_config()
- [x] Přidání synchronní verze analyze_query funkce
- [x] Vytvoření testovacího skriptu pro ověření změn
- [x] Vytvoření vizuální dokumentace pomocí PlantUML
- [x] Vytvoření Git branch langraph-schema-fix pro změny
- [x] Commit a push změn do repozitáře

### Provedené kroky pro řešení chyby s chybějícím modulem langchain_community (předchozí problém):

- [x] Identifikace problému v logu: `ModuleNotFoundError: No module named 'langchain_community'`
- [x] Analýza příčiny: rozdělení knihovny LangChain do specializovaných balíčků
- [x] Přidání chybějícího balíčku do requirements.txt
- [x] Vytvoření requirements-platform.txt pro LangGraph Platform
- [x] Aktualizace langgraph.json pro zahrnutí obou souborů s požadavky
- [x] Aktualizace GitHub Actions workflow 
- [x] Commit a push změn do repozitáře

### Následující kroky pro dokončení nasazení:

- [ ] Sestavení projektu pomocí langgraph build --tag ai-agent-ntier:latest
- [ ] Kontrola výsledku GitHub Actions workflow (v sekci Actions v repozitáři)
- [ ] Nasazení artefaktu na LangGraph Platform
- [ ] Verifikace odstranění chyby při generování JSON schématu v logech
- [ ] Ověření správného generování API dokumentace
- [ ] Testování agenta přes API v produkčním prostředí
- [ ] Sloučení změn do hlavní větve

### Poznámky:
- Obě série změn (langchain_community fix a JSON schema fix) by měly být nyní aplikované
- Po úspěšné verifikaci změn pro obě opravy je třeba změny sloučit do hlavní větve
- Pro nasazení použít skript ./deploy_to_langgraph_platform.sh a zvolit možnost 2 (sestavení a nasazení)

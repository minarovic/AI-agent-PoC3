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

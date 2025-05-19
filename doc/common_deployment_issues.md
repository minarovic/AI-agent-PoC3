# Časté problémy při nasazení na LangGraph Platform

Tento dokument obsahuje řešení nejčastějších problémů při nasazení aplikace AI-agent-Ntier na LangGraph Platform.

## 1. Problémy s build procesem

### 1.1. "Cannot generate a JsonSchema for core_schema.IsInstanceSchema"

**Příznak problému**: Build selže s chybou o nemožnosti generovat JSON schéma pro některou třídu.

**Příčina**: Třída nebo objekt ve stavu grafu není serializovatelný do JSON formátu. Častým případem jsou instance tříd jako `MockMCPConnector`, které jsou přímo uložené ve stavu.

**Řešení**:
1. Nahradit přímou referenci na instanci třídy za serializovatelnou konfiguraci:
   ```python
   # Špatně
   mcp_connector: MockMCPConnector = None
   
   # Správně
   mcp_connector_config: Optional[Dict[str, Any]] = None
   ```
2. Přidat metodu pro vytváření instancí za běhu:
   ```python
   def get_mcp_connector(self):
       if self.mcp_connector_config is None:
           self.mcp_connector_config = {"data_path": "default_path"}
       return MockMCPConnector(**self.mcp_connector_config)
   ```

### 1.2. "ModuleNotFoundError: No module named 'X'"

**Příznak problému**: Build selže s chybou o chybějícím modulu.

**Příčina**: Modul není zahrnut v `requirements.txt` nebo není dostupný v Python Package Index.

**Řešení**:
1. Přidat chybějící závislost do `requirements.txt`
2. Pokud je modul vlastní, ujistit se, že je zahrnut ve zdrojovém kódu a správně instalován v `setup.py`

### 1.3. "Docker build failed"

**Příznak problému**: V logu je hlášeno, že Docker build selhal.

**Příčina**: Konflikt mezi lokálními Docker soubory a LangGraph Platform build procesem.

**Řešení**:
1. Odstraňte všechny Docker soubory z GitHub repozitáře
2. Používejte `deploy_to_github.sh` pro správné nahrání kódu bez Docker souborů
3. Nechte LangGraph Platform provést build podle `langgraph.json`

## 2. Problémy s konfigurací grafu

### 2.1. "Graph module not found"

**Příznak problému**: Build selže s chybou, že modul grafu nebyl nalezen.

**Příčina**: Nesprávná cesta k modulu grafu v `langgraph.json`.

**Řešení**:
```json
// Správně
"graphs": {
  "agent": "./src/memory_agent/graph.py:graph"
}

// Špatně
"graphs": {
  "agent": "src/memory_agent/graph.py:graph"
}
```

### 2.2. "ImportError: cannot import name X from Y"

**Příznak problému**: Build selže s chybou importu konkrétního objektu z modulu.

**Příčina**: Nesprávný import nebo chybějící definice.

**Řešení**:
1. Zkontrolujte, že importovaný objekt je definován v daném modulu
2. Zkontrolujte, že modul je správně zahrnut v balíčku
3. Opravte importy a ujistěte se, že jsou všechny závislosti nainstalovány

### 2.3. "AttributeError: module has no attribute X"

**Příznak problému**: Build selže s chybou chybějícího atributu v modulu.

**Příčina**: Objekt není exportován z modulu, nebo je modul nesprávně importován.

**Řešení**:
1. Zkontrolujte `__init__.py` a ujistěte se, že objekt je exportován
2. Upravte import pro použití správného názvu atributu
3. Přidejte objekt do `__all__` seznamu v modulu

## 3. Problémy s asynchronními funkcemi

### 3.1. "RuntimeError: This event loop is already running"

**Příznak problému**: Aplikace selže při spuštění s chybou o běžícím event loop.

**Příčina**: Pokus o volání asynchronní funkce synchronně v grafu LangGraph.

**Řešení**:
1. Vytvořte synchronní wrapper pro asynchronní funkce:
   ```python
   def analyze_query_sync(state):
       import asyncio
       loop = asyncio.new_event_loop()
       result = loop.run_until_complete(analyze_query(state))
       loop.close()
       return result
   ```
2. Použijte tento wrapper místo přímého volání asynchronní funkce v grafu

### 3.2. "TypeError: object X is not subscriptable"

**Příznak problému**: Chyba při přístupu k atributu stavu jako ke slovníku.

**Příčina**: Pokus o přístup k poli jako ke slovníku místo přes atribut.

**Řešení**:
```python
# Špatně
next_node = state["query_type"]

# Správně
next_node = state.query_type
```

## 4. Problémy s nasazením po úspěšném buildu

### 4.1. "API vrací chybu 500"

**Příznak problému**: API je dostupné, ale vrací chybu 500 při volání.

**Příčina**: Interní chyba v aplikaci, často problém s konfigurací nebo chybějícími proměnnými prostředí.

**Řešení**:
1. Zkontrolujte logy v administraci LangGraph Platform
2. Ujistěte se, že všechny potřebné proměnné prostředí jsou správně nastaveny
3. Zkontrolujte konfiguraci aplikace a ověřte, že všechny závislosti jsou správně nastaveny

### 4.2. "API vrací chybu 401 nebo 403"

**Příznak problému**: API vrací chybu autorizace nebo přístupu.

**Příčina**: Neplatný nebo chybějící API klíč nebo nedostatečná oprávnění.

**Řešení**:
1. Zkontrolujte, že všechny potřebné API klíče jsou správně nastaveny v proměnných prostředí
2. Ověřte, že API klíče mají dostatečná oprávnění
3. Zkontrolujte, zda klíče nejsou expirovány

## 5. Problémy s integrací GitHub

### 5.1. "GitHub webhook selhal"

**Příznak problému**: Commit byl odeslán do GitHub, ale build nebyl spuštěn.

**Příčina**: Nesprávná konfigurace webhooků nebo nedostatečná oprávnění.

**Řešení**:
1. Zkontrolujte nastavení webhooků v GitHub repozitáři
2. Ověřte, že LangGraph Platform má správná oprávnění k repozitáři
3. Zkontrolujte logy webhooků pro případné chyby

### 5.2. "Cannot access private repository"

**Příznak problému**: LangGraph Platform nemůže přistupovat k privátnímu repozitáři.

**Příčina**: Nedostatečná oprávnění nebo expirace přístupového tokenu.

**Řešení**:
1. Obnovte autorizaci mezi GitHub a LangGraph Platform
2. Zkontrolujte oprávnění pro LangGraph GitHub App
3. Zajistěte, že repozitář je dostupný pro LangGraph Platform

## Závěr

Při řešení problémů s nasazením na LangGraph Platform je důležité:

1. **Systematicky postupovat** - nejprve identifikovat chybu, analyzovat příčinu, navrhnout řešení
2. **Kontrolovat logy** - logy v administraci LangGraph Platform poskytují detailní informace o chybách
3. **Sledovat best practices** - vždy používat `deploy_to_github.sh` pro push čistého kódu
4. **Dokumentovat řešení** - zaznamenat postup řešení problému do `deploy_logs/notes.md`

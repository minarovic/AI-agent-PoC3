# Oprava problému s checkpointy a MockMCPConnector

## Identifikovaný problém

Při používání checkpointů v LangGraph workflow docházelo k chybě:

```
AttributeError: 'MockMCPConnector' object has no attribute 'copy'
```

Chyba se vyskytovala v uzlu `retrieve_additional_company_data` a byla způsobena tím, že instance třídy `MockMCPConnector` byly ukládány přímo do stavu (State), ale nejsou serializovatelné pro checkpointy. Konkrétně při pokusu o serializaci stavu se LangGraph pokoušel zavolat metodu `copy()` na objektu `MockMCPConnector`, který tuto metodu neimplementuje.

## Analýza příčiny

1. **Ukládání neserializovatelného objektu do stavu**: V funkcích `prepare_company_query` a `retrieve_additional_company_data` byla instance `MockMCPConnector` ukládána přímo do stavu, který je následně persistován v checkpointech.

2. **Chybějící ošetření v reducer funkci**: Funkce `merge_dict_values` v `state.py` vyvolala chybu při pokusu o zavolání metody `copy()` na objektu `MockMCPConnector`.

3. **Nekonzistentní zacházení s thread_id**: Některé volání grafu nemusela správně předávat `thread_id` v konfiguraci, což mohlo vést k problémům s checkpointy.

## Implementované řešení

### 1. Úprava reducer funkce `merge_dict_values` v `state.py`

Přidáno robustní zpracování objektů, které nemají metodu `copy()`:

```python
# Bezpečné kopírování: řeší problém s objekty, které nemají metodu copy()
if left is None:
    result = {}
else:
    try:
        result = left.copy()
    except AttributeError:
        # Pokud objekt nemá metodu copy(), vytvoříme nový slovník
        result = {}
        logger.warning(f"Objekt typu {type(left)} nemá metodu copy(), vytvářím nový slovník")
```

### 2. Odstranění `mcp_connector` ze stavu v uzlech grafu

V funkcích `prepare_company_query` a `retrieve_additional_company_data` bylo odstraněno ukládání instance `MockMCPConnector` do stavu:

```python
# Ukládáme pouze základní data do state (bez MCP konektoru, který není serializovatelný)
return {
    "company_name": company_name,
    "analysis_type": analysis_type,
    "company_data": company_data
    # NEUKLÁDAT mcp_connector do state - není serializovatelný pro checkpointy
}
```

### 3. Vytvoření nové instance `MockMCPConnector` při každém volání

Místo spoléhání na uloženou instanci `mcp_connector` ve stavu je nyní v každém volání `retrieve_additional_company_data` vytvořena nová instance:

```python
# Vždy vytvoříme novou instanci MockMCPConnector - neukládáme ji do stavu
from memory_agent.tools import MockMCPConnector
logger.info("Vytvářím novou instanci MockMCPConnector")
mcp_connector = MockMCPConnector()
```

### 4. Testování opravy

Byl vytvořen testovací skript `test_checkpoint_fix.py`, který ověřuje, že:
- Checkpointy jsou správně ukládány
- Kontext je zachován mezi voláními
- `MockMCPConnector` není součástí serializovaného stavu

## Obecné doporučení pro práci s checkpointy

1. **Serializovatelnost objektů**: Do stavu ukládejte pouze serializovatelné objekty (slovníky, seznamy, primitivní typy).

2. **Neukládejte komplexní objekty**: Instance tříd, spojení s databází, apod. by neměly být součástí stavu.

3. **Správné předávání thread_id**: Při každém volání grafu vždy předávejte stejný thread_id v konfiguraci pro zachování kontextu mezi voláními:

```python
config = {"configurable": {"thread_id": "unikátní-id-konverzace"}}
response = graph.invoke({"messages": [...]}, config=config)
```

4. **Monitorování checkpointů**: Pro debugování kontrolujte obsah checkpointů pomocí `graph.get_state(config)` a `graph.get_state_history(config)`.

## Testování a další kroky

Pro ověření, že oprava byla úspěšná, spusťte připravený test:

```bash
python test_checkpoint_fix.py
```

Další kroky pro rozšíření podpory checkpointů:
1. Aktualizovat všechny testy a skript pro správné předávání thread_id
2. Implementovat `PostgresSaver` pro produkční nasazení
3. Přidat monitorovací nástroje pro správu checkpointů

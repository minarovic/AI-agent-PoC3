# Doporučení pro práci s checkpointy v Memory Agent

## Úvod

Tento dokument obsahuje souhrnná doporučení pro práci s checkpointy v projektu Memory Agent. Jsou zde uvedeny osvědčené postupy, které pomohou předejít problémům se serializací stavů a zajistit správné fungování persistentního kontextu mezi voláními grafu.

## Základní principy checkpointů

Checkpointy v LangGraph zajišťují:
- **Persistenci stavu** mezi jednotlivými voláními grafu
- **Zachování kontextu** celé konverzace
- **Time Travel** (možnost vrátit se k předchozím stavům)
- **Monitoring** stavu aplikace

## Pravidla pro správnou implementaci

### 1. Serializovatelnost objektů ve stavu

Do stavu ukládejte pouze objekty, které jsou serializovatelné:

- **ANO**: Slovníky, seznamy, řetězce, čísla, boolean hodnoty
- **NE**: Objekty tříd bez metody `copy()`, připojení k databázi, souborové handlery, apod.

```python
# Správně
return {
    "company_data": {"name": "MB TOOL", "id": "123"},
    "analysis_type": "risk_comparison"
}

# Špatně
return {
    "connector": mcp_connector,  # instance třídy bez copy()
    "database": db_connection     # připojení k DB
}
```

### 2. Správné předávání thread_id

Při každém volání grafu je nutné předat `thread_id` v konfiguraci:

```python
# Vytvoření konfigurace s thread_id
config = {"configurable": {"thread_id": "conversation-123"}}

# Správné volání grafu
response = graph.invoke({"messages": [HumanMessage(content=query)]}, config=config)
```

**Doporučení**: Pro každého uživatele nebo konverzaci používejte unikátní thread_id, který je konzistentně používán ve všech voláních.

### 3. Vytváření objektů mimo stav

Pokud potřebujete pracovat s komplexními objekty, vytvářejte je při každém volání znovu, místo ukládání do stavu:

```python
def retrieve_data(state: State) -> State:
    # Vytvořit novou instanci při každém volání, NE z předchozího stavu
    connector = MockMCPConnector()
    
    # Použít instanci pro získání dat
    data = connector.get_data(state.company_id)
    
    # Vrátit pouze data, NE instanci
    return {
        "company_data": data
    }
```

### 4. Práce s checkpointy v kódu

Pro práci s checkpointy lze použít následující metody:

```python
# Získání aktuálního stavu
state = graph.get_state(config)

# Získání historie stavů
state_history = list(graph.get_state_history(config))

# Time Travel - návrat k předchozímu stavu
config_with_checkpoint = {
    "configurable": {
        "thread_id": "conversation-123",
        "checkpoint_id": previous_checkpoint_id
    }
}
response = graph.invoke(None, config=config_with_checkpoint)
```

### 5. Monitoring a ladění checkpointů

Pro efektivní ladění využívejte:

```python
def log_checkpoint_state(graph, thread_id):
    """Vypíše aktuální stav checkpointu pro daný thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)
    
    if state:
        print(f"Checkpoint pro thread_id {thread_id}:")
        print(f"- Konfigurace: {state.config}")
        print(f"- Metadata: {state.metadata}")
        print(f"- Obsah: {state.values}")
    else:
        print(f"Žádný checkpoint nenalezen pro thread_id {thread_id}")
```

## Produkční nasazení

Pro produkční prostředí je doporučeno:

1. **Používat perzistentní úložiště** pro checkpointy:
   ```python
   from langgraph_checkpoint_postgres import PostgresSaver
   checkpointer = PostgresSaver(connection_string="...")
   graph = builder.compile(checkpointer=checkpointer)
   ```

2. **Implementovat správu thread_id** na úrovni aplikace:
   ```python
   # Přiřazení thread_id k uživateli/konverzaci
   user_thread_id = f"user-{user_id}-{conversation_id}"
   ```

3. **Přidat monitorování a expirace** starých checkpointů:
   ```python
   # Odstranění starých checkpointů
   for old_thread_id in expired_threads:
       checkpointer.delete_thread(old_thread_id)
   ```

## Nástroje pro kontrolu a verifikaci

V projektu jsou k dispozici následující nástroje:

- `test_checkpoint_fix.py` - Test ověřující opravu problému s MockMCPConnector
- `verify_thread_id_usage.py` - Kontrola správného používání thread_id v testovacích souborech
- `verify_and_test_checkpoints.sh` - Celková verifikace funkčnosti checkpointů

Doporučené spuštění před commit:
```bash
./verify_and_test_checkpoints.sh
```

## Závěr

Správná implementace checkpointů je klíčová pro fungující multi-turn konverzaci v Memory Agent. Dodržováním těchto principů předejdete problémům s serializací stavu a zajistíte správnou persistenci kontextu mezi jednotlivými voláními.

Pro jakékoli dotazy týkající se implementace checkpointů se obraťte na dokumentaci LangGraph nebo na tým vývoje Memory Agent.

**Poslední aktualizace:** 21.05.2025

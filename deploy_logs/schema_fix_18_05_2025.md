# LangGraph Platform JSON Schema Fix

## Problém

LangGraph Platform reportuje chybu při generování JSON schématu pro grafy, což má dopad na generování dokumentace API a testování:

```
Failed to get input schema for graph agent with error: `Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'memory_agent.tools.MockMCPConnector'>)
```

Problém je způsoben třídou `MockMCPConnector` v objektu `State`, která není serializovatelná do JSON formátu.

## Řešení

### 1. Úprava State objektu

Hlavní úprava spočívá v nahrazení přímé reference na `MockMCPConnector` třídou v State objektu za serializovatelný Pydantic model:

```python
# Původní verze
mcp_connector: Optional[MockMCPConnector] = None

# Nová verze
mcp_connector_config: Optional[MockMCPConnectorConfig] = None
```

Zároveň byla přidána metoda pro vytváření instance z konfigurace:

```python
def get_mcp_connector(self) -> MockMCPConnector:
    """
    Vytvoří nebo vrátí instanci MockMCPConnector na základě konfigurace.
    """
    if self.mcp_connector_config is None:
        self.mcp_connector_config = MockMCPConnectorConfig()
    
    return MockMCPConnector(data_path=self.mcp_connector_config.data_path)
```

### 2. Synchronní wrapper pro analyze_query

Pro kompatibilitu s grafovými uzly byla přidána synchronní verze `analyze_query` funkce, která volá asynchronní verzi:

```python
def analyze_query(...) -> AnalysisResult:
    """
    Synchronní verze funkce analyze_query pro přímé použití v grafových uzlech.
    """
    import asyncio
    
    def run_async(coroutine):
        # ...
    
    return run_async(analyze_query_async(...))
```

### 3. Aktualizace importů

Odstraněny zastaralé importy z `langchain_core.pydantic_v1` a nahrazeny přímými importy z `pydantic`.

## Výsledek

- LangGraph Platform může nyní generovat správné JSON schéma
- Odstraněna varování o zastaralých importech
- Zachována plná funkčnost původní implementace
- Zlepšena kompatibilita s nejnovějším LangGraph CLI

## Testování

Pro ověření správnosti změn byl vytvořen testovací skript `test_schema_fix_minimal.py`, který testuje:

1. Vytvoření a serializaci `MockMCPConnectorConfig`
2. Vytvoření `State` objektu s konfigurací
3. Funkčnost metody `get_mcp_connector()`

## Diagram

Vizuální dokumentace řešení se nachází v `/Users/marekminarovic/AI-agent-Ntier/doc/PlantUML/LangGraphSchema_Fix.plantuml`.

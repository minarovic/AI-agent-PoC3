# Přehled schémat pro LangGraph Platform

## Úvod

LangGraph Platform vyžaduje, aby všechny objekty používané ve stavovém grafu byly serializovatelné do JSON schématu. Tento dokument popisuje správný způsob definice a použití schémat v projektu AI-agent-Ntier.

## Základní principy

1. **Pydantic modely**: Všechny datové struktury, které jsou součástí vstupů nebo výstupů grafu, by měly být definovány jako Pydantic modely
2. **TypedDict**: Pro definici stavů grafu používejte `TypedDict` z balíčku `typing_extensions`
3. **Explicitní typy**: Vždy definujte explicitní typy pro všechny parametry a návratové hodnoty

## Schémata v projektu AI-agent-Ntier

### Definice schémat
Všechna schémata jsou centrálně definována v souboru `src/memory_agent/schema.py`:

```python
# Příklad definice schématu
class CompanyData(BaseModel):
    id: str = Field(..., description="Jedinečný identifikátor společnosti")
    name: str = Field(..., description="Název společnosti")
    # Další pole...
```

### Použití schémat v grafu

Graf používá schémata pro definici vstupů a výstupů:

```python
from typing_extensions import TypedDict
from memory_agent.schema import CompanyData

class GraphState(TypedDict):
    company_data: CompanyData
    # Další pole...
```

### Serializace nestandardních objektů

Pro třídy, které nejsou Pydantic modely, ale musí být součástí stavu grafu:

1. Vytvořte Pydantic model pro konfiguraci
2. Implementujte metodu `to_dict()` pro serializaci
3. Používejte tento model v rámci stavu

Příklad:
```python
class MockMCPConnectorConfig(BaseModel):
    data_path: str = Field(...)

class MockMCPConnector:
    def __init__(self, config: MockMCPConnectorConfig):
        self.config = config
        # Inicializace...
    
    def to_dict(self):
        return self.config.model_dump()
```

## Známé problémy a jejich řešení

### 1. JSON Schema generování

Problém: LangGraph nedokáže vygenerovat schéma pro složité objekty ve stavu grafu.

Řešení:
- Používat Pydantic modely s explicitními typy
- Pro složité objekty implementovat serializaci

### 2. Deprecated Pydantic imports

Problém: LangChain používá `langchain_core.pydantic_v1`, což způsobuje varování.

Řešení:
- Importovat přímo z `pydantic`
- Pro zachování kompatibility implementovat vlastní adaptéry mezi verzemi

### 3. Komplexní objekty ve stavu

Problém: Některé objekty obsahují funkce, které nejsou serializovatelné.

Řešení:
- Oddělit konfiguraci od implementace
- Uchovávat pouze data, ne funkce

## Nejlepší postupy

1. **Dokumentace**: Přidat popisy do všech polí pomocí `Field(description="...")`
2. **Validace**: Využívat validátory Pydantic pro ověření dat
3. **Kompatibilita**: Používat `model_config = ConfigDict(extra="allow")` pro zpětnou kompatibilitu
4. **Rozdělení**: Oddělovat modely vstupů, výstupů a interních stavů

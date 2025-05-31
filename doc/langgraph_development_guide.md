# LangGraph Development Guide pro Memory Agent

Tento komplexní návod slouží jako hlavní zdroj informací pro vývojáře, kteří chtějí rozšiřovat a vyvíjet Memory Agent aplikaci na LangGraph Platform.

## Obsah

1. [Architektura aplikace](#architektura-aplikace)
2. [Rozšiřování aplikace](#rozšiřování-aplikace)
3. [Přidání nových typů analýz](#přidání-nových-typů-analýz)
4. [Práce s LangGraph funkcemi](#práce-s-langgraph-funkcemi)
5. [Vývojářské best practices](#vývojářské-best-practices)
6. [Testování a debugging](#testování-a-debugging)
7. [Deployment workflow](#deployment-workflow)
8. [Troubleshooting](#troubleshooting)

## Architektura aplikace

Memory Agent je postavena na LangGraph `create_react_agent` vzoru a využívá minimalistický přístup pro jednoduchost nasazení na LangGraph Platform.

### Klíčové komponenty

```
src/memory_agent/
├── graph.py         # Hlavní LangGraph definice
├── analyzer.py      # Nástroj pro analýzu společností
├── tools.py         # MockMCPConnector a další utility
├── state.py         # Definice stavu workflow
├── schema.py        # Pydantic modely pro validaci
└── configuration.py # Konfigurace aplikace
```

### LangGraph vzor

Aplikace používá `create_react_agent` vzor, který je optimalizován pro:
- **Jednoduchost**: Minimální konfigurační overhead
- **Robustnost**: Automatické zpracování chyb a retry logika
- **Rozšiřitelnost**: Snadné přidávání nových tools

```python
# src/memory_agent/graph.py
agent = create_react_agent(
    model="openai:gpt-4",
    tools=[analyze_company],  # Seznam nástrojů
    prompt="...",             # System prompt
    checkpointer=checkpointer # Persistenční vrstva
)
```

## Rozšiřování aplikace

### 1. Přidání nového nástroje

Nejjednodušší způsob rozšíření aplikace je přidání nového nástroje:

```python
# src/memory_agent/analyzer.py

def analyze_market_trends(query: str) -> str:
    """
    Analyze market trends for specific industry or region.
    
    Args:
        query: User query about market trends
        
    Returns:
        JSON string with market analysis results
    """
    # Implementace nástroje
    result = {
        "query_type": "market_trends",
        "trends_data": {...},
        "analysis_complete": True,
        "query": query
    }
    return json.dumps(result, indent=2)
```

Poté přidejte nástroj do grafu:

```python
# src/memory_agent/graph.py
from memory_agent.analyzer import analyze_company, analyze_market_trends

agent = create_react_agent(
    model="openai:gpt-4",
    tools=[analyze_company, analyze_market_trends],  # Přidání nového nástroje
    prompt="...",
    checkpointer=checkpointer
)
```

### 2. Rozšíření MockMCPConnector

Pro přidání nových datových zdrojů rozšiřte MockMCPConnector:

```python
# src/memory_agent/tools.py - přidání nové metody

def get_market_data(self, market_id: str) -> Dict[str, Any]:
    """
    Načte data o trhu podle ID.
    
    Args:
        market_id: Identifikátor trhu
        
    Returns:
        Dict s daty o trhu
    """
    file_path = os.path.join(self.data_path, f"market_{market_id}.json")
    return self._load_json_file(file_path)
```

### 3. Rozšíření State objektu

Pro sledování nových typů dat přidejte pole do State:

```python
# src/memory_agent/state.py

@dataclass(kw_only=True)
class State:
    # Existující pole...
    
    market_data: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    """Data o trzích získaná během analýzy."""
    
    trend_analysis: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    """Výsledky analýzy trendů."""
```

## Přidání nových typů analýz

Aplikace aktuálně podporuje tři typy analýz: `general`, `risk_comparison`, `supplier_analysis`. Přidání nového typu zahrnuje několik kroků:

### 1. Rozšíření detekce typu analýzy

```python
# src/memory_agent/analyzer.py - pokud budete rozšiřovat detekci

def detect_analysis_type(query: str) -> str:
    """Rozšířená detekce typů analýz."""
    query = query.lower()
    
    # Existující klíčová slova...
    
    # Nový typ analýzy
    market_keywords = [
        "market", "trend", "industry", "sector", "growth", 
        "forecast", "outlook", "competition"
    ]
    
    if any(kw in query for kw in market_keywords):
        return "market_analysis"
    
    # Existující logika...
```

### 2. Přidání nových mock dat

Vytvořte nové JSON soubory v `mock_data_2/`:

```json
// mock_data_2/market_automotive.json
{
  "market_id": "automotive_cz",
  "industry": "Automotive",
  "region": "Czech Republic",
  "trends": {
    "growth_rate": "3.2%",
    "key_drivers": ["Electric vehicles", "Industry 4.0"],
    "challenges": ["Supply chain disruptions", "Regulation changes"]
  },
  "competitors": [...]
}
```

### 3. Rozšíření nástroje pro analýzu

```python
# src/memory_agent/analyzer.py

def analyze_company(query: str) -> str:
    """Rozšířená verze s podporou nových typů analýz."""
    try:
        connector = MockMCPConnector()
        
        # Detekce typu analýzy
        analysis_type = detect_analysis_type(query)
        
        # Různé cesty podle typu analýzy
        if analysis_type == "market_analysis":
            # Logika pro market analýzu
            market_data = connector.get_market_data(market_id)
            result = {
                "query_type": "market_analysis",
                "market_data": market_data,
                "analysis_complete": True
            }
        else:
            # Existující logika pro ostatní typy
            # ...
            
        return json.dumps(result, indent=2)
```

## Práce s LangGraph funkcemi

### Checkpointing a persistence

LangGraph poskytuje robustní checkpointing systém:

```python
# Různé typy checkpointers
from langgraph.checkpoint.memory import InMemorySaver  # Vývoj
from langgraph.checkpoint.sqlite import SqliteCheckpoint  # Produkce

# Pro vývoj
checkpointer = InMemorySaver()

# Pro produkci
checkpointer = SqliteCheckpoint("checkpoints.db")
```

### Threading a paralelní zpracování

```python
# Použití thread_id pro izolaci konverzací
config = {"configurable": {"thread_id": "user_123"}}
response = agent.invoke({"messages": [user_message]}, config=config)
```

### Konfigurace a environment variables

```python
# src/memory_agent/configuration.py

class Configuration:
    """Centralizovaná konfigurace aplikace."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "openai:gpt-4")
        self.mock_data_path = os.getenv("MOCK_DATA_PATH", "mock_data_2")
```

## Vývojářské best practices

### 1. Struktura kódu

- **Jednoduchá tools**: Každý nástroj by měl mít jednu jasnou odpovědnost
- **JSON výstupy**: Všechny tools by měly vracet strukturované JSON
- **Error handling**: Vždy ošetřte chyby a vraťte validní JSON
- **Logging**: Přidejte logování pro debugging

```python
def my_tool(query: str) -> str:
    """Template pro nový nástroj."""
    try:
        # Logování vstupu
        logger.info(f"Zpracování dotazu: {query[:50]}...")
        
        # Hlavní logika
        result = process_query(query)
        
        # Strukturovaný výstup
        return json.dumps({
            "query_type": "my_tool",
            "result": result,
            "analysis_complete": True,
            "query": query
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Chyba v my_tool: {str(e)}")
        return json.dumps({
            "error": str(e),
            "query_type": "my_tool", 
            "analysis_complete": False,
            "query": query
        })
```

### 2. Testování

```python
# tests/test_new_tool.py

def test_my_tool():
    """Test nového nástroje."""
    result = my_tool("test query")
    data = json.loads(result)
    
    assert data["query_type"] == "my_tool"
    assert data["analysis_complete"] is True
    assert "result" in data
```

### 3. Dokumentace

- Dokumentujte každou novou funkci s docstrings
- Přidejte examples do dokumentace
- Aktualizujte README.md při významných změnách

## Testování a debugging

### Lokální testování

```bash
# Spuštění základních testů
python -m pytest tests/ -v

# Test konkrétního nástroje
python -c "from src.memory_agent.analyzer import analyze_company; print(analyze_company('test'))"

# Test celého grafu
python -c "
from src.memory_agent.graph import memory_agent
result = memory_agent.invoke({'messages': [{'role': 'user', 'content': 'Test'}]})
print(result)
"
```

### Debugging s LangSmith

```python
# Přidání LangSmith trackingu
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "memory-agent-dev"
```

### Mock data testování

```python
# Testování s různými mock daty
from src.memory_agent.tools import MockMCPConnector

connector = MockMCPConnector("tests/mock_data")
result = connector.get_company_by_name("Test Company")
```

## Deployment workflow

### 1. Příprava na deployment

```bash
# 1. Zkontrolujte tests
python -m pytest tests/ -v

# 2. Validace kódu
python -c "from src.memory_agent.graph import memory_agent; print('Graph OK')"

# 3. Zkontrolujte langgraph.json
cat langgraph.json
```

### 2. GitHub workflow

```yaml
# .github/workflows/test.yml
name: Test and Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v
```

### 3. LangGraph Platform deployment

Aplikace se automaticky nasadí na LangGraph Platform při push do `main` větve díky GitHub integraci.

Sledování nasazení:
1. GitHub Actions logy
2. LangGraph Platform administrace
3. Funkční testy na produkční URL

## Troubleshooting

### Časté problémy

#### 1. Import chyby
```
ModuleNotFoundError: No module named 'memory_agent'
```

**Řešení**: Zkontrolujte, že `src/` je v Python path:
```python
import sys
sys.path.append('src')
```

#### 2. JSON serialization chyby
```
TypeError: Object of type 'datetime' is not JSON serializable
```

**Řešení**: Použijte JSON-kompatibilní typy nebo custom encoder:
```python
import json
from datetime import datetime

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

json.dumps(data, default=json_serializer)
```

#### 3. Mock data nenalezena
```
FileNotFoundError: Mock data file not found
```

**Řešení**: Zkontrolujte cesty a existence souborů:
```python
import os
data_path = "mock_data_2"
print(f"Data path exists: {os.path.exists(data_path)}")
print(f"Files: {os.listdir(data_path) if os.path.exists(data_path) else 'N/A'}")
```

#### 4. LangGraph Platform chyby

**Chyba**: `Configuration schema not found`
**Řešení**: Zkontrolujte `langgraph.json` syntax:
```json
{
  "dependencies": ["."],
  "graphs": {
    "memory_agent": "src.memory_agent.graph:memory_agent"
  },
  "env": ".env"
}
```

**Chyba**: `Environment variables not set`
**Řešení**: Nastavte variables v LangGraph Platform administration:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` 
- `MOCK_DATA_PATH` (volitelně)

### Debug postupy

1. **Lokální test**: Vždy nejprve otestujte lokálně
2. **Log kontrola**: Zkontrolujte logs v GitHub Actions
3. **Incremental changes**: Malé změny, časté deploymenty
4. **Rollback plán**: Před deploymentem si připravte rollback strategii

## Další zdroje

- [LangGraph dokumentace](https://langchain-ai.github.io/langgraph/)
- [LangGraph Platform guides](https://platform.langgraph.com/docs)
- [Projekt README](../README.md)
- [Analýza typů analýz](./Analyza_typu_analyz.md)
- [Platform integration guide](./langgraph_platform_integration.md)

---

**Pro další pomoc nebo dotazy kontaktujte tým vývojářů nebo vytvořte issue v GitHub repository.**
# AI-Ntier: Development Workflow

## 🎯 DEVELOPMENT PHASE
Aplikace je úspěšně nasazena na LangGraph Platform. Nyní se zaměřujeme na přidávání nových funkcí a vylepšení.

## 📁 PRODUKČNÍ STRUKTURA
```
src/memory_agent/
├── analyzer.py      # ✅ 40 řádků - Core analysis tool
├── graph.py         # ✅ 20 řádků - create_react_agent
├── graph_nodes.py   # 🔄 Volitelné - pro složitější workflow
├── tools.py         # ✅ MockMCPConnector API
├── state.py         # ✅ Minimální state definice
└── __init__.py      # ✅ Package initialization

Konfigurace:
├── langgraph.json   # ✅ Python import syntax
├── requirements.txt # ✅ Core dependencies
├── setup.py         # ✅ Pro GitHub Actions
└── requirements-dev.txt # ✅ Development tools
```

## 🔧 DEVELOPMENT WORKFLOW

### 1. Před přidáním nové funkce:
1. **Přečti posledních 3 iterace** z testing_iteration_log.md
2. **Identifikuj podobné změny** - co fungovalo/nefungovalo
3. **Minimální implementace** - začni s nejjednoduším řešením
4. **GitHub Actions first** - netestuj lokálně

### 2. Typy změn:
- **New Tools:** Přidej do tools.py, registruj v graph.py
- **Analysis Types:** Rozšiř analyzer.py minimalisticky
- **Workflow Changes:** Aktualizuj graph.py (preferuj create_react_agent)
- **Dependencies:** Aktualizuj requirements.txt + requirements-dev.txt

### 3. Testing Strategy:
- **GitHub Actions:** Primární validace
- **LangGraph Platform:** Deployment testing
- **Lokální testing:** POUZE když explicitně řečeno

## 📝 CODE STYLE

### Minimalistický přístup:
```python
# ✅ GOOD - jednoduchá funkce
def analyze_company(query: str) -> str:
    """Analyze company query using MCP."""
    return connector.process_query(query)

# ❌ AVOID - složitá logika
def analyze_company_advanced(query: str, context: dict, options: list) -> dict:
    # 50+ řádků komplexní logiky
```

### Error Handling:
```python
# ✅ GOOD - základní handling
try:
    result = api_call()
    return result
except Exception as e:
    return f"Error: {str(e)}"

# ❌ AVOID - komplexní error hierarchie
```

## 🚨 DEPLOYMENT REQUIREMENTS

### GitHub Actions musí mít:
- **setup.py** - pro `pip install -e .`
- **requirements-dev.txt** - pro development dependencies
- **Všechny importy** - ověř že existují před commitem

### LangGraph Platform potřebuje:
- **Python import syntax** v langgraph.json
- **String model syntax** - `"openai:gpt-4"` místo objektů
- **ConfigSchema** - pro runtime konfiguraci

## 🔄 ITERATIVE DEVELOPMENT
1. **Změna** → Commit → GitHub Actions
2. **Actions OK** → Deploy na Platform
3. **Platform OK** → Pokračuj dalším feature
4. **Error** → Oprav podle logů → Repeat
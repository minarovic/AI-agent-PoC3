# LangGraph Platform - Požadavky a Kontrolní Body

## Instrukce pro Copilot

Tento prompt obsahuje kritické požadavky a kontrolní body pro vývoj AI agenta na LangGraph Platform. **VŽDY** ověř tyto body před nasazením nebo při řešení problémů s kompatibilitou. Tento prompt použij jako checklist během celého vývojového procesu.

## 🔥 KRITICKÉ POVINNÉ KOMPONENTY

Každá LangGraph aplikace **MUSÍ** obsahovat:

### 1. StateGraph Definition
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# Povinné schéma stavu
class MyState(TypedDict):
    messages: list  # nebo použij MessagesState
    # další atributy...

# Povinná definice grafu
builder = StateGraph(MyState)
builder.add_node("node_name", node_function)
builder.add_edge(START, "node_name")
graph = builder.compile()  # POVINNÉ!
```

### 2. Správné Importy
```python
# POVINNÉ importy pro základní funkcionalnost
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages  # pro zprávy
from typing_extensions import TypedDict

# Pro pokročilé funkce
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
```

### 3. Exportovaný Graf
```python
# V main modulu (např. src/memory_agent/graph.py)
# Graf MUSÍ být exportován pro LangGraph Platform
graph = builder.compile()

# NEBO pojmenovaný export
my_agent = builder.compile()
```

## 📋 KONTROLNÍ CHECKLIST

### Před každým commitem:
- [ ] **StateGraph je správně definován** s TypedDict schématem
- [ ] **Všechny uzly mají implementované funkce** (ne jen None)
- [ ] **Graf končí END nebo má return hodnotu**
- [ ] **Všechny importy jsou z oficiálních balíčků**
- [ ] **Žádné lokální/relativní importy mimo projekt**

### Před nasazením:
- [ ] **langgraph.json existuje a je validní JSON**
- [ ] **requirements.txt obsahuje všechny závislosti**
- [ ] **Graf se kompiluje bez chyb** (`graph.compile()`)
- [ ] **Žádné Docker soubory v produkčním kódu**
- [ ] **Žádné testovací soubory v src/**

### Po nasazení:
- [ ] **Graf je dostupný na deployment URL**
- [ ] **API klíče jsou správně nakonfigurovány**
- [ ] **Základní invoke test prochází**

## 🚨 NEJČASTĚJŠÍ CHYBY A ŘEŠENÍ

### ImportError: cannot import name 'StateGraph'
```python
# ❌ ŠPATNĚ
from langgraph import StateGraph

# ✅ SPRÁVNĚ  
from langgraph.graph import StateGraph
```

### AttributeError: 'NoneType' object has no attribute 'compile'
```python
# ❌ ŠPATNĚ - chybí node implementace
builder.add_node("agent", None)

# ✅ SPRÁVNĚ - každý node musí mít funkci
def agent_node(state):
    return {"messages": "response"}

builder.add_node("agent", agent_node)
```

### KeyError v langgraph.json
```json
// ✅ MINIMÁLNÍ VALIDNÍ langgraph.json
{
    "dependencies": ["."],
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    },
    "env": ".env"
}
```

### Concurrent Update Errors
```python
# ❌ ŠPATNĚ - více uzlů updatuje stejný klíč současně
def node1(state): return {"result": "value1"}
def node2(state): return {"result": "value2"}
builder.add_edge(START, "node1")
builder.add_edge(START, "node2")  # CONFLICT!

# ✅ SPRÁVNĚ - použij reducers nebo sekvenční flow
from typing import Annotated
def merge_results(left, right): 
    return left + right

class State(TypedDict):
    result: Annotated[str, merge_results]
```

## 🔧 DEBUGGING A OVĚŘOVÁNÍ

### Rychlá validace kódu:
```python
# Test kompilace grafu
try:
    graph = builder.compile()
    print("✅ Graf se zkompiloval úspěšně")
except Exception as e:
    print(f"❌ Chyba kompilace: {e}")

# Test základního invoke
try:
    result = graph.invoke({"messages": []})
    print("✅ Graf funguje")
except Exception as e:
    print(f"❌ Chyba běhu: {e}")
```

### Kontrola závislostí:
```bash
# Ověř, že máš správné verze
pip show langgraph langchain-core
```

### Validace langgraph.json:
```python
import json
with open('langgraph.json') as f:
    config = json.load(f)
    assert 'graphs' in config
    print("✅ langgraph.json je validní")
```

## 📚 PROPOJENÍ S DALŠÍMI PROMPTY

- **Po implementaci** → použij `testing.prompt.md`
- **Při chybách importů** → použij `compatibility_fix.prompt.md` 
- **Pro nasazení** → použij `deploy.prompt.md`
- **Pro PoC změny** → použij `master.prompt.md`

## ⚡ RYCHLÉ REFERENCE

### Minimální working graf:
```python
from langgraph.graph import StateGraph, START
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str

def process(state):
    return {"output": f"Processed: {state['input']}"}

graph = (StateGraph(State)
    .add_node("process", process)
    .add_edge(START, "process")
    .compile())
```

### Povinné soubory pro deployment:
```
├── src/
│   └── your_agent/
│       ├── __init__.py
│       ├── graph.py          # exportuje 'graph'
│       └── state.py         # definuje State
├── langgraph.json           # POVINNÉ
├── requirements.txt         # POVINNÉ
└── setup.py                # POVINNÉ
```

---

## 💡 DŮLEŽITÉ PŘIPOMÍNKY

1. **LangGraph Platform je specifické prostředí** - ne všechno co funguje lokálně funguje tam
2. **Používej Context7 pro aktuální API dokumentaci** - API se rychle mění
3. **Minimalizuj komplexitu** - jednodušší grafy mají méně problémů
4. **Testuj po každé změně** - malé iterace jsou bezpečnější
5. **Dokumentuj workaroundy** - pomohou při budoucích problémech

**Zapamatuj si:** Pokud graf nelze zkompilovat lokálně, nebude fungovat ani na platformě!
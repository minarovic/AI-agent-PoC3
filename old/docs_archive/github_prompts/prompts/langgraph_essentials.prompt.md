# LangGraph Platform - Základní Povinnosti pro AI Agenty

## Instrukce pro Copilot Agent

**TENTO PROMPT JE POVINNÁ KONTROLNÍ LISTA PŘED KAŽDÝM COMMITEM A NASAZENÍM.**

Každý AI agent pro LangGraph Platform MUSÍ splňovat tyto požadavky. Nedodržení jakéhokoliv bodu způsobí selhání nasazení nebo runtime chyby. **VŽDY ověř všechny body před implementací změn.**

---

## 🚨 KRITICKÉ KOMPONENTY - POVINNÉ PRO KAŽDÝ AGENT

### 1. StateGraph Definition (POVINNÉ)
```python
# ✅ SPRÁVNĚ - Povinná struktura
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class MyState(TypedDict):
    messages: list  # nebo použij MessagesState
    # další state atributy...

builder = StateGraph(MyState)
builder.add_node("my_node", my_function)
builder.add_edge(START, "my_node")
builder.add_edge("my_node", END)
graph = builder.compile()  # POVINNÉ!

# ❌ CHYBA - Chybí StateGraph nebo compilation
graph = None  # Způsobí runtime error
```

### 2. Správné Importy (POVINNÉ)
```python
# ✅ POVINNÉ základní importy
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages  # pro zprávy

# ✅ Pro pokročilé funkce
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# ❌ CHYBA - Špatné importy
from langgraph import StateGraph  # NEEXISTUJE
```

### 3. Node Functions (POVINNÉ)
```python
# ✅ SPRÁVNĚ - Každý node má implementovanou funkci
def my_node(state: MyState) -> MyState:
    return {"messages": ["response"]}

builder.add_node("my_node", my_node)

# ❌ CHYBA - Node bez implementace
builder.add_node("my_node", None)  # Způsobí chybu
```

### 4. Exportovaný Graf (POVINNÉ)
```python
# ✅ SPRÁVNĚ - Graf musí být exportován
# V main modulu (např. src/memory_agent/graph.py)
graph = builder.compile()

# ❌ CHYBA - Graf není exportován nebo není dostupný
# graph je definován jen lokálně
```

---

## 📋 KONTROLNÍ CHECKLIST - PŘED KAŽDÝM COMMITEM

### Základní Struktura:
- [ ] **StateGraph je definován** s TypedDict nebo compatible schématem
- [ ] **Všechny uzly mají implementované funkce** (ne None hodnoty)
- [ ] **Graf má jasný START a END** nebo return path
- [ ] **Graf je zkompilován** pomocí `.compile()`
- [ ] **Graf je exportován** v hlavním modulu

### State Management:
- [ ] **State schema je definováno** pomocí TypedDict
- [ ] **State obsahuje povinné klíče** pro workflow
- [ ] **Používáš správné reducers** pro složité state (add_messages)
- [ ] **Žádné concurrent updates** na stejný state klíč

### Importy a Závislosti:
- [ ] **Všechny importy jsou z officiálních balíčků**
- [ ] **Žádné relativní importy** mimo projekt
- [ ] **requirements.txt obsahuje všechny závislosti**
- [ ] **Verze balíčků jsou kompatibilní**

### LangGraph Specifika:
- [ ] **Používáš správné Message typy** (HumanMessage, AIMessage, etc.)
- [ ] **Tools mají správné docstringy** (kritické pro LLM)
- [ ] **Tools jsou správně vázané** pomocí `.bind_tools()`
- [ ] **Podmíněné hrany mají správnou logiku**

---

## 🔧 NEJČASTĚJŠÍ CHYBY A RYCHLÁ ŘEŠENÍ

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
    return {"messages": ["response"]}
builder.add_node("agent", agent_node)
```

### INVALID_CONCURRENT_GRAPH_UPDATE
```python
# ❌ ŠPATNĚ - více uzlů updatuje stejný klíč
class State(TypedDict):
    result: str  # Multiple nodes updating this simultaneously

# ✅ SPRÁVNĚ - použij reducer nebo sekvenční flow
from typing import Annotated
import operator

class State(TypedDict):
    result: Annotated[list, operator.add]  # Safe for concurrent updates
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

---

## 🧪 DEBUGGING A OVĚŘOVÁNÍ

### Rychlá validace kódu:
```python
# Test kompilace grafu - SPUSŤ PŘED KAŽDÝM COMMITEM
try:
    graph = builder.compile()
    print("✅ Graf se zkompiloval úspěšně")
except Exception as e:
    print(f"❌ Chyba kompilace: {e}")
    # NEPOKRAČUJ bez opravy této chyby!

# Test základního invoke
try:
    result = graph.invoke({"messages": []})
    print("✅ Graf funguje")
except Exception as e:
    print(f"❌ Chyba běhu: {e}")
    # NEPOKRAČUJ bez opravy této chyby!
```

### Kontrola závislostí:
```bash
# Ověř správné verze PŘED nasazením
pip show langgraph langchain-core
```

### Validace langgraph.json:
```python
# SPUSŤ PŘED KAŽDÝM NASAZENÍM
import json
try:
    with open('langgraph.json') as f:
        config = json.load(f)
        assert 'graphs' in config
        print("✅ langgraph.json je validní")
except Exception as e:
    print(f"❌ langgraph.json problém: {e}")
    # NEPOKRAČUJ bez opravy!
```

---

## 🎯 MINIMÁLNÍ WORKING AGENT

```python
# MINIMÁLNÍ TEMPLATE PRO NOVÝ AGENT
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str

def process_node(state: State) -> State:
    return {"output": f"Processed: {state['input']}"}

# Sestavení grafu
builder = StateGraph(State)
builder.add_node("process", process_node)
builder.add_edge(START, "process")
builder.add_edge("process", END)

# POVINNÉ - export grafu
graph = builder.compile()
```

---

## 📁 POVINNÉ SOUBORY PRO DEPLOYMENT

```
├── src/
│   └── your_agent/
│       ├── __init__.py       # POVINNÉ
│       ├── graph.py          # POVINNÉ - exportuje 'graph'
│       └── state.py         # Doporučené - definuje State
├── langgraph.json           # POVINNÉ
├── requirements.txt         # POVINNÉ
├── setup.py                # POVINNÉ pro LangGraph Platform
└── .env                    # Doporučené pro API klíče
```

---

## ⚡ RYCHLÉ REFERENCE

### Povinné Message Types:
- `HumanMessage` - uživatelské zprávy
- `AIMessage` - odpovědi AI
- `SystemMessage` - systémové instrukce
- `ToolMessage` - výsledky nástrojů

### Povinné Graph Komponenty:
- `StateGraph(State)` - hlavní graf
- `START` a `END` - vstupní a výstupní body
- `.add_node()` - přidání uzlů
- `.add_edge()` / `.add_conditional_edges()` - propojení
- `.compile()` - kompilace grafu

### Tools Patterns:
```python
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """POVINNÝ docstring - popisuje co tool dělá."""
    return "result"

# Vazba na LLM
llm_with_tools = llm.bind_tools([my_tool])
```

---

## 🚨 KRITICKÁ PRAVIDLA

1. **NIKDY nenahrávej graf bez kompilace** - `graph = builder.compile()` je POVINNÉ
2. **KAŽDÝ node musí mít implementovanou funkci** - žádné None hodnoty
3. **VŽDY testuj kompilaci lokálně** před push do repo
4. **State schema MUSÍ být TypedDict** nebo compatible typ
5. **Tools MUSÍ mít docstringy** - LLM je potřebuje pro rozhodování
6. **VŽDY kontroluj ImportError** - používej správné importy
7. **NIKDY nepoužívej lokální/relativní importy** mimo projekt

---

## 🔗 PROPOJENÍ S DALŠÍMI PROMPTY

- **Po implementaci** → `testing.prompt.md`
- **Při chybách nasazení** → `deploy.prompt.md`
- **Pro nové funkce** → `new_feature.prompt.md`
- **Při refaktorování** → `refactoring.prompt.md`

---

## 💡 ZAPAMATUJ SI

**Pokud graf nelze zkompilovat lokálně, nebude fungovat ani na LangGraph Platform!**

Každá chyba v této checklist může způsobit:
- Runtime selhání na platformě
- Deployment failure
- Neočekávané chování agenta
- Ztrátu času při debugování

**VŽDY projdi celou checklist před commitem!**
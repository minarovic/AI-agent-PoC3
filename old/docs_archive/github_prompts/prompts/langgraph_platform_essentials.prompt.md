# LangGraph Platform - Must Have Essentials

## Instrukce pro Copilot Agent

**KRITICKÉ MINIMUM** pro funkční AI agent na LangGraph Platform. Bez těchto komponent agent NEBUDE fungovat.

---

## 🚨 MUST HAVE #1: StateGraph Definition

```python
# POVINNÉ - Bez tohoto agent nefunguje
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list  # nebo MessagesState

builder = StateGraph(State)
graph = builder.compile()  # MUST HAVE!
```

---

## 🚨 MUST HAVE #2: Correct Imports

```python
# ✅ MUST HAVE - Správné importy
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# ❌ FATAL ERROR - Neexistuje
from langgraph import StateGraph  # CRASH!
```

---

## 🚨 MUST HAVE #3: Node Functions

```python
# ✅ MUST HAVE - Každý node musí mít funkci
def my_node(state: State):
    return {"messages": ["response"]}

builder.add_node("my_node", my_node)

# ❌ FATAL ERROR - Node bez funkce
builder.add_node("my_node", None)  # CRASH!
```

---

## 🚨 MUST HAVE #4: Graph Export

```python
# MUST HAVE - Graf musí být exportován pro LangGraph Platform
# V souboru jako src/memory_agent/graph.py
graph = builder.compile()
```

---

## 🚨 MUST HAVE #5: langgraph.json

```json
{
    "dependencies": ["."],
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    }
}
```

---

## 🚨 MUST HAVE #6: File Structure

```
├── src/
│   └── memory_agent/
│       ├── __init__.py      # MUST HAVE
│       └── graph.py         # MUST HAVE - exportuje graph
├── langgraph.json           # MUST HAVE
├── requirements.txt         # MUST HAVE
└── setup.py                # MUST HAVE
```

---

## 🚨 MUST HAVE #7: requirements.txt

```txt
langgraph>=0.2.0
langchain-core
```

---

## ⚡ VALIDATION TEST

```python
# SPUSŤ PŘED KAŽDÝM COMMITEM
try:
    graph = builder.compile()
    result = graph.invoke({"messages": []})
    print("✅ Agent funguje")
except Exception as e:
    print(f"❌ MUST FIX: {e}")
    # NEPOKRAČUJ BEZ OPRAVY!
```

---

## 🎯 MINIMAL WORKING AGENT

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str

def process(state):
    return {"output": f"Processed: {state['input']}"}

graph = (StateGraph(State)
    .add_node("process", process)
    .add_edge(START, "process")
    .add_edge("process", END)
    .compile())
```

**BEZ TĚCHTO 7 BODŮ AGENT NEBUDE FUNGOVAT NA LANGGRAPH PLATFORM!**
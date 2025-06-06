# Copilot Instructions – Vývoj StateGraph workflow pro Memory Agent

Tento projekt bude zásadně refaktorován: stávající ReAct agent bude nahrazen explicitním **StateGraph workflow** s podmíněným větvením podle typu dotazu a deterministickým řízením každého kroku. Následující instrukce upravují předchozí doporučení a postupy práce s ohledem na tuto změnu.

---

## 🔄 KLÍČOVÉ ZMĚNY PRO VÝVOJ

- **ReAct agent bude pouze fallback.** Všechny nové workflow implementace mají být vedeny přes StateGraph (viz `src/memory_agent/graph.py` nebo nový soubor `graph_stategraph.py`).
- **Každý krok workflow bude reprezentován explicitním uzlem v grafu.**  
  Např.: detekce typu dotazu, načtení dat, analýza, formátování odpovědi, error handling.
- **Větvení na základě typu analýzy (`state.analysis_type`).**  
  Všechny rozhodovací logiky musí být implementovány jako podmíněné hrany mezi uzly.
- **Tooly (např. MockMCPConnector) mohou být volány pouze z node funkcí – nikdy přímo z LLM.**  
  LLM slouží pouze pro generování odpovědi na základě připravených dat.

---

## 🏗️ DOPORUČENÝ POSTUP PRO COPILOTA

1. **Při generování nového workflow vždy použij LangGraph StateGraph.**
2. **Uzly workflow implementuj jako čisté Python funkce (např. `def route_query(state: State) -> State`).**
3. **Podmíněné větvení realizuj pomocí `add_conditional_edges` v LangGraph.**
4. **Error handling implementuj jako samostatný uzel (`error_node`), na který workflow přechází při chybě.**
5. **Exportuj hlavní entrypoint funkci (např. `create_explicit_stategraph()`).**
6. **Zachovej původní ReAct agenta pod jinou funkcí (např. `create_react_agent_legacy()`).**

---

## ✅ BEST PRACTICES

- **Každý node by měl mít detailní docstring vysvětlující jeho účel.**
- **Testy rozšiřuj tak, aby pokrývaly všechny větve StateGraphu včetně chybových stavů.**
- **Loguj vstupy/výstupy a případné chyby v každém uzlu pro snadné ladění.**
- **Nové typy analýz nebo rozšíření workflow vždy navrhuj jako přidání nového uzlu a/nebo větve.**
- **Všechny změny konzultuj v rámci hlavního issue/workflow v `docs/issue_stategraph_workflow.md`.**

---

## 🔗 DŮLEŽITÉ SOUBORY A ZDROJE

- [`src/memory_agent/graph.py`] – hlavní workflow (StateGraph)
- [`src/memory_agent/graph_nodes.py`] – implementace node funkcí
- [`src/memory_agent/state.py`] – definice State a reducerů
- [`src/memory_agent/analyzer.py`] – logika pro detekci/analýzu dotazu
- [`src/memory_agent/tools.py`] – MockMCPConnector a další utility
- [`docs/issue_stategraph_workflow.md`] – hlavní issue/workflow plán
- [LangGraph dokumentace](https://docs.langchain.com/v2/langgraph)

---

## 📝 POZNÁMKY PRO BUDOUCÍ REFLEKSI

- Po refaktoringu ponech stávající fallback ReAct agenta pro porovnání výsledků.
- Jakákoliv změna v API State nebo node funkcí by měla být okamžitě reflektována v testech a dokumentaci.
- Pokud Copilot agent generuje nový node nebo větvení, vždy ověř, že je správně napojen do grafu a flow je deterministické.



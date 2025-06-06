# AI-agent-Ntier - LangGraph Development Guide

## 🎯 PROJEKT OVERVIEW
**AI-agent-Ntier** - LangGraph aplikace s pokročilou analýzou dat hostovaná na LangGraph Platform

### Základní Info:
- **Platform:** LangGraph Platform (cloud hosting)
- **Framework:** LangGraph StateGraph pro multi-agent workflows
- **Data Access:** MockMCPConnector pro přístup k mock datům
- **Status:** Ve vývoji - fázovaná implementace
- **CI/CD:** GitHub Actions pipeline

## 🤖 Doporučení pro Copilot/AI agenta a vývojáře
- Tento projekt je optimalizovaný pro využití Copilot Coding Agenta a podobných AI nástrojů.
- **Copilot může generovat, analyzovat i refaktorovat kód podle této dokumentace.**
- Pro běžné úkoly (přidání typu analýzy, úprava dat, debugging) vždy postupuj podle níže uvedených kroků a struktur.
- **API klíče a secrets:**  
  Uchovávej runtime klíče (OpenAI, Anthropic atd.) v GitHub Secrets (`Settings → Secrets and variables → Actions`), případně v lokálním `.env` souboru (viz příklad níže).
- **Testy a lintery** běží jen ve workflow `test.yml` (produkční běh není závislý na testech).
- **Dev závislosti** (`requirements-dev.txt`) jsou určeny pouze pro CI a lokální vývoj.

### Příklad .env souboru pro lokální vývoj:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
LANGCHAIN_API_KEY=...
```

## 📁 STRUKTURA PROJEKTU
```
AI-agent-Ntier/
├── src/
│   └── memory_agent/
│       ├── __init__.py
│       ├── analyzer.py          # Analýza dotazů a detekce typu analýzy
│       ├── graph.py             # Hlavní StateGraph workflow
│       ├── prompts.py           # PromptRegistry - specializované prompty
│       └── tools.py             # MockMCPConnector pro přístup k datům
├── mock_data/                   # Testovací data
│   ├── companies/               # Data o společnostech
│   ├── internal_data/           # Interní data
│   ├── people/                  # Data o osobách
│   └── relationships/           # Data o vztazích
├── tests/                       # Unit a integrační testy
├── doc/                         # Dokumentace projektu
├── langgraph.json               # Platform konfigurace
├── requirements.txt             # Dependencies
└── run_langgraph_dev.sh         # Dev server script
```

## 🧩 KLÍČOVÉ KOMPONENTY

### StateGraph Workflow (`graph.py`)
- **Pydantic BaseModel** pro definici State
- **Podmíněné větvení** podle typu analýzy
- **Thread-based persistence** pro memory

### Analyzer (`analyzer.py`)
- **Few-shot prompting** s reasoning procesem
- **Detekce typu analýzy** z uživatelských dotazů
- **Error handling** a fallback mechanismy

### MockMCPConnector (`tools.py`)
- **JSON data loading** z mock_data adresářů
- **Company name normalization** 
- **Structured data access** pro různé entity

### PromptRegistry (`prompts.py`)
- **Centralizovaná správa promptů**
- **Specializované prompty** pro každý typ analýzy
- **Data formatters** pro prompt injection

## 🚀 DEVELOPMENT WORKFLOW

### Fázovaný přístup:
1. **Core komponenty** - Analyzer, MockMCPConnector, PromptRegistry
2. **StateGraph workflow** - Podmíněné větvení a error handling
3. **Testing & Debug** - Unit testy + end-to-end testy
4. **Deploy & Monitor** - Platform nasazení a dokumentace

### Deployment Process:
1. **Změna kódu** → Push to GitHub
2. **GitHub Actions** → Automatické testy
3. **LangGraph Platform** → Automatický deploy (při úspěchu)

### Klíčové soubory pro deployment:
- `langgraph.json` - Platform konfigurace
- `requirements.txt` - Dependencies  
- `src/memory_agent/graph.py` - StateGraph entry point

## ⚙️ DEVELOPMENT PRINCIPY
- **Mock-first development** - Používej mock_data pro testování
- **StateGraph patterns** - Následuj LangGraph best practices
- **Platform-optimized** - Optimalizováno pro LangGraph Platform hosting
- **Fázovaná implementace** - Postupné přidávání features

## 🔧 BĚŽNÉ ÚKOLY

### Přidat nový typ analýzy:
1. Přidej prompt do `prompts.py` (PromptRegistry)
2. Uprav detekci v `analyzer.py` 
3. Rozšiř StateGraph podmínky v `graph.py`
4. Přidej mock data pokud potřeba

### Upravit data access:
1. Uprav MockMCPConnector v `tools.py`
2. Přidaj/uprav JSON soubory v `mock_data/`
3. Aktualizuj normalizaci názvů

### Debugging workflow:
1. Zkontroluj StateGraph flow v `graph.py`
2. Ověř prompt formatting v `prompts.py`
3. Otestuj data access přes MockMCPConnector
4. Použij unit testy v `tests/`

### Aktualizovat dependencies:
1. Uprav `requirements.txt`
2. Test přes GitHub Actions
3. Deploy na LangGraph Platform

### Praktické příkazy:
- **Instalace production dependencies:**  
  `pip install -r requirements.txt`
- **Instalace dev dependencies:**  
  `pip install -r requirements-dev.txt`
- **Spuštění testů:**  
  `pytest`
- **Lokální spuštění/ladění:**  
  `bash run_langgraph_dev.sh` nebo `python -m src.memory_agent.graph`

## 🚦 TROUBLESHOOTING

### GitHub Actions selhání:
- Zkontroluj Python syntax v všech `.py` souborech
- Ověř dependencies v `requirements.txt`
- Zkontroluj import paths (`src.memory_agent.graph:memory_agent`)

### LangGraph Platform selhání:
- Zkontroluj `langgraph.json` konfiguraci
- Ověř StateGraph export v `graph.py`
- Zkontroluj Pydantic model definitions

### MockMCPConnector issues:
- Ověř JSON struktura v `mock_data/`
- Zkontroluj file paths a normalizaci názvů
- Test data loading v unit testech

### StateGraph debugging:
- Zkontroluj State model definici (Pydantic BaseModel)
- Ověř podmíněné hrany a node transitions
- Test thread persistence a memory

## 📝 QUICK REFERENCE
- **Entry point:** `src.memory_agent.graph:memory_agent` 
- **Platform config:** `langgraph.json`
- **StateGraph:** `src/memory_agent/graph.py`
- **Data access:** `src/memory_agent/tools.py` (MockMCPConnector)
- **Prompts:** `src/memory_agent/prompts.py` (PromptRegistry)
- **Mock data:** `mock_data/companies|people|relationships/`
- **Tests:** `tests/unit/` a `tests/integration/`

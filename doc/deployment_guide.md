# Nasazení na LangGraph Platform

Tento dokument popisuje kroky potřebné k nasazení AI-agent-Ntier na LangGraph Platform.

## Příprava projektu

### 1. Konfigurace repozitáře

Nastavte GitHub repozitář s následující strukturou:

```
AI-agent-Ntier/
├── src/
│   └── memory_agent/
│       ├── graph.py        # Definice StateGraph workflow
│       ├── analyzer.py     # Analýza dotazů a detekce typu
│       ├── prompts.py      # Specializované prompty
│       └── tools.py        # MockMCPConnector
├── mock_data/              # Testovací data
├── langgraph.json          # Konfigurace LangGraph Platform
├── requirements.txt        # Seznam závislostí
└── doc/                    # Dokumentace
```

### 2. Nastavení proměnných prostředí

Vytvořte soubor `.env` s následujícími hodnotami:

```bash
# API Keys pro LLM modely
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Logging
LOG_LEVEL=INFO
```

### 3. Ověření struktury projektu

Před nasazením zkontrolujte, zda projekt obsahuje:

- `langgraph.json` - Konfigurační soubor pro LangGraph Platform
- `src/memory_agent/graph.py` - Obsahuje definici grafu a exportuje proměnnou `graph`
- `mock_data/` - Adresář s testovacími daty
- `requirements.txt` - Seznam závislostí projektu

## Možnosti nasazení

### A. Nasazení pomocí GitHub integrace

1. **Registrace na LangGraph Platform**
   - Vytvořte si účet na [LangGraph Platform](https://smith.langchain.com/)
   - Získejte API klíč

2. **Vytvoření nového projektu**
   - V LangGraph Dashboard klikněte na "New Project"
   - Vyberte "Import from GitHub"
   - Vyberte svůj repozitář

3. **Konfigurace nasazení**
   - Platforma automaticky detekuje `langgraph.json`
   - Nastavte potřebné environment variables (API klíče)
   - Klikněte na "Deploy"

### B. Lokální vývojový server

```bash
# Instalace závislostí
pip install -r requirements.txt

# Spuštění lokálního vývojového serveru
langgraph dev
```

Server bude spuštěn na adrese `http://127.0.0.1:2024`.

Pro přístup k LangGraph Studio UI otevřete v prohlížeči:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## Environment proměnné

Pro správné fungování aplikace je třeba nastavit tyto proměnné prostředí:

- `OPENAI_API_KEY` - API klíč pro OpenAI modely
- `ANTHROPIC_API_KEY` - API klíč pro Anthropic modely (volitelné)

## Testování nasazení

Po nasazení můžete otestovat API:

```bash
curl -X POST https://your-deployment-url.langgraph.com/agents/agent/invoke \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [{"type": "human", "content": "Co je to MB TOOL?"}],
      "original_query": "Co je to MB TOOL?"
    },
    "config": {
      "configurable": {
        "thread_id": "test_thread_1"
      }
    }
  }'
```

## Debugging

Pokud nasazení selže, zkontrolujte:

1. **Logy nasazení** - Často obsahují informace o chybách
2. **Konfigurace grafu** - Zkontrolujte, zda je `graph` exportován v `graph.py`
3. **Mock data** - Ověřte, zda jsou data správně nakonfigurována
4. **Environment proměnné** - Zkontrolujte, zda jsou nastaveny všechny potřebné proměnné
# AI-agent-Ntier (PoC-3)

Implementace analytického agenta pomocí LangGraph Platform pro analýzu společností, hodnocení rizik a analýzu dodavatelských řetězců.

## Popis projektu

AI-agent-Ntier je proof-of-concept implementace analytického agenta, který využívá LangGraph Platform k poskytování strukturovaných analýz společností. Projekt je navržen s důrazem na nasaditelnost na LangGraph Platform a základní funkcionalitu bez zbytečně robustních implementací.

## Klíčové vlastnosti

- **Analýza společností**: Detekce typu analýzy z uživatelských dotazů
- **Hodnocení rizik**: Identifikace a analýza rizikových faktorů společností
- **Analýza dodavatelských řetězců**: Vizualizace a analýza dodavatelsko-odběratelských vztahů
- **Specializované prompty**: Optimalizované prompty pro různé typy analýz
- **LangGraph Platform kompatibilita**: Připraveno pro nasazení na LangGraph Platform

## Struktura projektu

```
AI-agent-Ntier/
├── src/
│   └── memory_agent/         # Hlavní kód projektu
│       ├── graph.py          # Definice LangGraph workflow
│       ├── analyzer.py       # Analýza uživatelských dotazů
│       ├── prompts.py        # Specializované prompty
│       └── tools.py          # Nástroje pro přístup k datům
├── mock_data/                # Testovací data
├── doc/                      # Dokumentace
├── langgraph.json            # Konfigurace pro LangGraph Platform
└── run_langgraph_dev.sh      # Skript pro spuštění vývojového serveru
```

## Začínáme

### Instalace

```bash
# Klonování repozitáře
git clone https://github.com/username/AI-agent-Ntier.git
cd AI-agent-Ntier

# Instalace závislostí
pip install -r requirements.txt

# Nastavení proměnných prostředí
cp .env.template .env
# Editujte soubor .env a doplňte vaše API klíče
```

### Spuštění lokálního vývojového serveru

```bash
# Spuštění lokálního serveru
./run_langgraph_dev.sh
```

LangGraph vývojový server bude spuštěn na adrese `http://127.0.0.1:2024`.

Pro přístup k LangGraph Studio UI otevřete v prohlížeči:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Použití API

```bash
# Příklad volání API
curl -X POST http://127.0.0.1:2024/agents/agent/invoke \
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

## Nasazení

Projekt je možné nasadit dvěma způsoby:

### Lokální nasazení

```bash
# Sestavit projekt
langgraph build

# Spustit lokálně
langgraph up
```

### Nasazení na LangGraph Platform

1. **Automatizované nasazení přes GitHub CI/CD**:
   - Nastavte v repozitáři GitHub Secrets: `OPENAI_API_KEY` a `LANGSMITH_API_KEY`
   - Push do větve `main` automaticky spustí workflow pro sestavení a vytvoření artefaktu
   - Stáhněte vygenerovaný artefakt a následujte instrukce v [Manuálu pro ruční nasazení](./doc/manual_langgraph_deployment.md)

2. **Ruční nasazení**:
   - Postupujte podle pokynů v [Návodu na nasazení](./doc/deployment_guide.md) a [Manuálu pro ruční nasazení](./doc/manual_langgraph_deployment.md)

## Dokumentace

Detailní dokumentace je dostupná v adresáři `/doc`:

- [Architektura systému](./doc/architecture.md)
- [API a struktura serveru](./doc/api_server_structure.md)
- [Příklady implementace](./doc/code_examples.md)
- [Návod na nasazení](./doc/deployment_guide.md)
- [Manuál pro ruční nasazení](./doc/manual_langgraph_deployment.md)
- [Struktura projektu a roadmapa](./doc/project_structure.md)
- [Popis workflow](./doc/workflow.md)

## Příklady použití

### Python klient

```python
import requests
import json

def query_agent(question, thread_id="default"):
    """Odešle dotaz na agenta prostřednictvím LangGraph Platform."""
    url = "http://127.0.0.1:2024/agents/agent/invoke"
    
    payload = {
        "input": {
            "messages": [{"type": "human", "content": question}],
            "original_query": question
        },
        "config": {
            "configurable": {
                "thread_id": thread_id
            }
        }
    }
    
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# Příklad použití
result = query_agent("Co je to MB TOOL?")
print(result["output"]["messages"][0]["content"])
```

## Licence

[MIT License](LICENSE)
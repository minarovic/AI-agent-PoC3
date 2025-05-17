# API a struktura serveru pro LangGraph Platform

## Přehled

AI-agent-Ntier využívá LangGraph Platform pro poskytování REST API rozhraní. Tato dokumentace popisuje strukturu serveru, dostupné endpointy a příklady použití.

## Struktura serveru

### Adresářová struktura

```
AI-agent-Ntier/
├── src/
│   └── memory_agent/
│       ├── graph.py         # Hlavní definice grafu pro LangGraph Platform
│       └── ...
├── langgraph.json           # Konfigurace pro LangGraph Platform
└── run_langgraph_dev.sh     # Spuštění vývojového serveru (lokálně)
```

### Konfigurace v langgraph.json

```json
{
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    }
}
```

Tato konfigurace říká, že graf `graph` z modulu `src/memory_agent/graph.py` bude dostupný pod identifikátorem `agent`.

## API rozhraní

### 1. Zpracování dotazu

**Endpoint:** `/agents/agent/invoke`

**Metoda:** `POST`

**Request:**
```json
{
    "input": {
        "messages": [
            {
                "type": "human",
                "content": "Jaké jsou rizika pro společnost MB TOOL?"
            }
        ],
        "original_query": "Jaké jsou rizika pro společnost MB TOOL?"
    },
    "config": {
        "configurable": {
            "thread_id": "user_123_conversation_456"
        }
    }
}
```

**Response:**
```json
{
    "output": {
        "messages": [
            {
                "type": "ai",
                "content": "Společnost MB TOOL má následující rizikové faktory..."
            }
        ],
        "error": null
    }
}
```

### 2. Získání stavu konverzace

**Endpoint:** `/threads/{thread_id}/state`

**Metoda:** `GET`

**Response:**
```json
{
    "state": {
        "messages": [...],
        "company_analysis": {...},
        "company_data": {...},
        "internal_data": {...},
        "relationships_data": {...},
        "original_query": "...",
        "current_step": "...",
        "error": null
    }
}
```

### 3. Vymazání stavu konverzace

**Endpoint:** `/threads/{thread_id}`

**Metoda:** `DELETE`

**Response:**
```json
{
    "status": "success",
    "message": "Thread deleted"
}
```

## Příklady použití API

### Curl příklad

```bash
curl -X POST http://127.0.0.1:2024/agents/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [{"type": "human", "content": "Jaké jsou rizika pro společnost MB TOOL?"}],
      "original_query": "Jaké jsou rizika pro společnost MB TOOL?"
    },
    "config": {
      "configurable": {
        "thread_id": "test_thread_1"
      }
    }
  }'
```

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

## Konfigurace serveru

### Vývojové prostředí

Pro spuštění vývojového serveru použijte:

```bash
./run_langgraph_dev.sh
```

Server bude dostupný na `http://127.0.0.1:2024`.

Pro přístup k LangGraph Studio UI použijte:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Produkční prostředí

Pro produkční nasazení se doporučuje využít LangGraph Platform pomocí GitHub integrace:

1. Vytvořte projekt v LangGraph Platform
2. Propojte s GitHub repozitářem
3. Nastavte potřebné environment variables
4. Nasaďte aplikaci
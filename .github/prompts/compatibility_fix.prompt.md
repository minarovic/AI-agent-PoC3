# AI-agent-Ntier: Řešení kompatibility

## 🎯 JEDINÝ CÍL
**Zajistit kompatibilitu kódu s LangGraph Platform**

## 🚨 KLÍČOVÉ POZNATKY Z DEPLOYMENTU
1. **LangGraph.json musí používat Python import syntax**
   - ✅ SPRÁVNĚ: `"src.memory_agent.graph:memory_agent"` (Python import s tečkami)
   - ❌ ŠPATNĚ: `"./src/memory_agent/graph.py:memory_agent"` (filesystem path s lomítky)

2. **String syntax a dependencies**
   - String syntax (`model = "openai:gpt-4"`) je preferovaná, ALE:
   - Stále vyžaduje `langchain-openai>=0.3.18` v requirements.txt
   - `init_chat_model()` interně stále potřebuje langchain_openai balíček

3. **Struktura projektu musí být standardní**
   - setup.py musí existovat pro `pip install -e .`
   - requirements-dev.txt musí existovat pokud je v workflow
   - src struktura musí odpovídat Python importům

## 📋 KOMPATIBILITA CHECKLIST
- [ ] langgraph.json používá Python import syntax?
- [ ] requirements.txt obsahuje všechny přímé i nepřímé závislosti?
- [ ] setup.py existuje a je minimální?
- [ ] String syntax pro modely je správně použita?
- [ ] Nejsou v kódu nepoužívané importy?
- [ ] GitHub Secrets obsahují správné API klíče?

## 🔧 ŘEŠENÍ TYPICKÝCH PROBLÉMŮ

### ImportError: Unable to import langchain_openai
- **Příčina:** String syntax není "dependency-free"
- **Řešení:** Přidat `langchain-openai>=0.3.18` do requirements.txt
- **Pattern Recognition:** Iterace 67

### Error: does not appear to be a Python project
- **Příčina:** Chybí setup.py pro `pip install -e .` 
- **Řešení:** Vytvořit minimální setup.py
- **Pattern Recognition:** Iterace 70

### ModuleNotFoundError pro vlastní moduly
- **Příčina:** Špatný PYTHONPATH nebo struktura importů
- **Řešení:** Opravit relativní/absolutní importy nebo nastavit PYTHONPATH
- **Pattern Recognition:** Iterace 66

### ValidationError: No configuration schema found
- **Příčina:** Chybí ConfigSchema v kódu
- **Řešení:** Přidat minimální ConfigSchema
- **Pattern Recognition:** Iterace 60

## 🧰 MINIMÁLNÍ SETUP.PY
```python
from setuptools import setup, find_packages

setup(
    name="ai-agent-ntier",
    version="0.1.0",
    description="AI agent for LangGraph Platform",
    author="AI-agent-Ntier Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Zkopírovat z requirements.txt
    ],
    python_requires=">=3.11",
)
```

## 🧪 OPTIMÁLNÍ MODEL DEFINICE
```python
# Preferovaná string syntax
model = "openai:gpt-4"

# NEBO explicitní definice pokud je potřeba více kontroly
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="gpt-4",
    temperature=0,
)
```

## 📄 SPRÁVNÝ FORMÁT LANGGRAPH.JSON
```json
{
  "graphs": {
    "memory_agent": "src.memory_agent.graph:memory_agent"
  }
}
```

## 🔑 API KLÍČE A FORMÁTY
```
OPENAI_API_KEY: Prefix "sk-" (např. sk-abc123...)
ANTHROPIC_API_KEY: Prefix "sk-ant-" (např. sk-ant-abc123...)
LANGSMITH_API_KEY: Prefix "ls-" (volitelné, např. ls-abc123...)
```

## ❌ ANTI-PATTERNS V ŘEŠENÍ KOMPATIBILITY
- **NETESTOVAT** lokálně a ignorovat GitHub Actions
- **NESIMULOVAT** řešení (string syntax bez závislostí)
- **NEPOUŽÍVAT** filesystem cesty v langgraph.json
- **NEPŘIDÁVAT** zbytečné závislosti "pro jistotu"
- **NEPŘEHLÍŽET** warning zprávy - často indikují budoucí chyby

## 🔄 ITERAČNÍ CYKLUS OPRAV
```
1. ANALYZUJ chybovou zprávu detailně (ne jen první řádek)
2. IDENTIFIKUJ přesnou příčinu (ne symptom)
3. POROVNEJ s předchozími iteracemi
4. NAVRHNI minimální opravu
5. OTESTUJ v GitHub Actions (ne lokálně)
6. ZHODNOŤ výsledek
```

## 🎯 DECISION FRAMEWORK
- **Chyba v importu modulu?** → Zkontroluj requirements.txt
- **Chyba v importu vlastního kódu?** → Zkontroluj langgraph.json formát
- **Chyba při instalaci projektu?** → Zkontroluj setup.py
- **Chyba při inicializaci modelu?** → Zkontroluj string syntax a dependencies
- **Chyba v API volání?** → Zkontroluj GitHub Secrets a formáty klíčů
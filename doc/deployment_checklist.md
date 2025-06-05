## 🚀 Deployment Checklist pro LangGraph Platform

### Před nahráním na LangGraph Platform:

#### 0. ✅ Python Version Requirements:
- **Python 3.11 nebo vyšší** - LangGraph Platform vyžaduje minimálně Python 3.11
- Zkontroluj `setup.py`: `python_requires=">=3.11"` ✅
- Zkontroluj `.github/workflows/deploy.yml`: `python-version: '3.11'` ✅

#### 1. ✅ Environment Variables nastavení:
```
V LangGraph Platform Dashboard → Environment Variables:

OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

LANGSMITH_API_KEY=lsv2_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_xxxxxxxxxxxxxxxx

LANGSMITH_PROJECT=AI-agent-Ntier

LOG_LEVEL=INFO
```

#### 2. ✅ Ověř, že aplikace funguje:
- Lokálně s těmito API klíči ✅ (už otestováno)
- Kód automaticky načítá z `os.environ.get("OPENAI_API_KEY")` ✅

#### 3. ✅ Repository je připravený:
- `langgraph.json` konfigurace ✅
- Dependencies v `requirements.txt` ✅
- `.env` v `.gitignore` (API klíče se neukládají do GitHubu) ✅

#### 4. 🎯 Deployment process:
1. Jdi na LangGraph Platform Dashboard
2. Create New Project → Import from GitHub
3. Vybor: `minarovic/AI-agent-PoC3` repository
4. Nastav Environment Variables (viz výše)
5. Deploy!

⚠️ **DŮLEŽITÉ**: Platforma použije Environment Variables z jejich admin rozhraní, ne z tvého lokálního `.env` souboru!

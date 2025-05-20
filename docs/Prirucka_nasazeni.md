# Průvodce nasazením AI-agent-Ntier na LangGraph Platform

Tento dokument obsahuje informace o správném procesu nasazení aplikace na LangGraph Platform.

## Produkční vs. testovací soubory

### Produkční soubory (nahrávané na GitHub)
Tyto soubory jsou nezbytné pro provoz aplikace a jsou nahrávány na GitHub pro nasazení na LangGraph Platform:

- **Zdrojové kódy:**
  - `src/memory_agent/analyzer.py` - Analytický modul s detekcí typů analýz
  - `src/memory_agent/tools.py` - Nástroje pro práci s MCP
  - `src/memory_agent/graph_nodes.py` - Uzly grafu workflow
  - `src/memory_agent/state.py` - Definice stavového objektu
  - `src/memory_agent/graph.py` - Hlavní graf workflow
  - `src/memory_agent/__init__.py` - Inicializační soubor balíčku
  - `src/memory_agent/utils.py` - Pomocné funkce
  - `src/memory_agent/prompts.py` - Šablony promptů
  - `src/memory_agent/configuration.py` - Konfigurační nastavení
  - `src/memory_agent/schema.py` - Definice schémat a modelů

- **Konfigurační soubory:**
  - `langgraph.json` - Hlavní konfigurační soubor pro LangGraph Platform
  - `requirements.txt` - Seznam závislostí pro standardní instalaci
  - `requirements-platform.txt` - Seznam závislostí pro LangGraph Platform
  - `setup.py` - Instalační skript balíčku

### Testovací soubory (pouze lokální)
Tyto soubory jsou určeny pouze pro lokální testování a vývoj a NEJSOU nahrávány na GitHub pro nasazení na LangGraph Platform:

- **Testovací skripty:**
  - `test_*.py` - Všechny testy začínající prefixem "test_"
  - `simple_test_analysis_types.py` - Jednoduchý testovací skript pro typy analýz
  - `src/memory_agent/mock_langgraph.py` - Pomocný modul pro testování

- **Lokální deployment soubory:**
  - `Dockerfile*` - Všechny Docker soubory
  - `docker-compose*.yml` - Všechny Docker Compose soubory
  - `.dockerignore` - Soubor s ignorovanými položkami pro Docker
  - `.github/workflows` - GitHub Actions definice

- **Dokumentační a logovací soubory:**
  - `deploy_logs/*` - Logy z nasazení
  - `doc/*` - Dokumentační soubory a diagramy

## Správný proces nasazení

1. **Lokální testování:**
   - Použijte `deploy_to_langgraph_platform.sh` pro LOKÁLNÍ testování funkčnosti
   - Použijte `simple_test_analysis_types.py` pro ověření podpory typů analýz
   - Použijte `verify_deployment.sh` pro kontrolu správnosti kódu

2. **Nasazení na GitHub:**
   - Pro nasazení používejte VÝHRADNĚ `deploy_analysis_types_to_github.sh`
   - Tento skript odešle ČISTÝ kód na GitHub bez testovacích skriptů a Docker souborů
   - LangGraph Platform si stáhne kód přímo z GitHubu a sestaví jej podle `langgraph.json`

3. **Kontrola nasazení:**
   - Po dokončení nasazení zkontrolujte stav na LangGraph Platform
   - Ověřte, že se všechny produkční soubory úspěšně nahrály a jsou funkční

## Co NEDĚLAT

- **NIKDY NEPOSÍLEJ** Docker soubory a konfiguraci na GitHub, způsobuje to konflikty při buildu na LangGraph Platform
- **NEVYUŽÍVEJ** příkazy jako `langgraph build` nebo `langgraph deploy` při práci s GitHub
- **NEPOSÍLEJ** testovací skripty na GitHub, mohly by způsobit problémy při nasazení

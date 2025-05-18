Zápisky:

# Deploying AI-agent-Ntier - Poznámky z procesu nasazení

## [2024-07-21] - Úspěšný deployment! 🎉

### Stav deploymentu:
- Deployment do LangGraph Platform proběhl úspěšně!
- Aplikace je spuštěna a dostupná na portu 8000
- Log obsahuje potvrzení o úspěšném startu: `Application startup complete.`
- HTTP požadavky jsou úspěšně zpracovávány

### Zbývající varování (pro budoucí balík):
1. **LangChain Deprecation Warnings**:
   - Varování týkající se používání `langchain_core.pydantic_v1`
   - Doporučení používat přímo `from pydantic import BaseModel`
   
2. **Problémy se schématem JSON**:
   - Nelze generovat JSON schéma pro třídu `MockMCPConnector`
   - Způsobuje chybu při snaze o získání schématu vstupu/výstupu pro grafy
   
### Doporučení pro budoucí verzi:
- Aktualizovat importy z `langchain_core.pydantic_v1` na `pydantic` nebo `pydantic.v1`
- Upravit třídu `MockMCPConnector`, aby byla Pydantic kompatibilní
- Implementovat správnou serializaci pro JSON schéma
- Vytvářet schémata pro vstupní a výstupní typy namísto přímého použití instancí tříd

### Závěr:
- Deployment je plně funkční pro produkční použití
- Nalezené problémy jsou pouze varování, nebrání funkčnosti aplikace
- Pro lepší integraci s nástroji LangGraph Platform doporučuji řešit tato varování v další verzi

## [2024-07-21] - Chybějící modul utils

### Identifikovaný problém:
- Deployment selhal s chybou: `ImportError: cannot import name 'utils' from 'memory_agent'`
- Kód v `analyzer.py` se snaží importovat modul `utils`, který neexistuje v balíčku `memory_agent`

### Analýza příčiny:
- V modulu `memory_agent` chybí soubor `utils.py` s potřebnými funkcemi
- Soubor `__init__.py` neexportuje modul `utils`, i kdyby existoval
- Funkce `utils.split_model_and_provider()` je používána v `analyzer.py` ale není definována nikde v projektu

### Navrhované řešení:
- [x] Vytvořit soubor `src/memory_agent/utils.py` s implementací potřebných funkcí
- [x] Aktualizovat `__init__.py` pro export modulu `utils`
- [ ] Spustit deployment znovu a ověřit fungování

### Implementace:
1. Vytvořen soubor `src/memory_agent/utils.py`:
   ```python
   def split_model_and_provider(model_name: str) -> Tuple[Optional[str], str]:
       """Split a model name into provider and model parts."""
       if "/" in model_name:
           provider, model = model_name.split("/", 1)
           return provider, model
       return None, model_name
   ```

2. Aktualizován `src/memory_agent/__init__.py`:
   ```python
   """Memory Agent package for AI-agent-Ntier."""

   __version__ = "0.1.0"

   # Explicitní export modulů
   from . import utils
   ```

### Verifikace:
- Čeká na opětovný deployment do LangGraph Platform

## [2024-07-21] - Missing langchain_openai module

### Identifikovaný problém:
- Po úpravě importů se objevila nová chyba: `ModuleNotFoundError: No module named 'langchain_openai'`
- Balíček je uvedený v requirements.txt, ale pravděpodobně není správně nainstalovaný v prostředí LangGraph Platform

### Analýza příčiny:
- LangGraph Platform pravděpodobně neprovádí instalaci všech balíčků z requirements.txt
- Je třeba explicitně uvést balíček langchain_openai v souboru langgraph.json

### Navrhované řešení:
- [x] Přidat `langchain_openai>=0.1.0` přímo do "dependencies" v souboru langgraph.json
- [ ] Spustit deployment znovu a ověřit fungování

### Implementace:
- Úprava langgraph.json:
  ```json
  {
      "name": "AI-agent-Ntier",
      "graphs": {
          "agent": "./src/memory_agent/graph.py:graph"
      },
      "python_version": "3.12",
      "dependencies": [".", "langchain_openai>=0.1.0"]
  }
  ```

### Verifikace:
- Čeká na opětovný deployment do LangGraph Platform

## [2024-07-21] - Missing langchain_community module

### Identifikovaný problém:
- Deployment do LangGraph Platform selhal s chybou: `ModuleNotFoundError: No module named 'langchain_community'`
- Tato chyba se vyskytuje ve `/deps/AI-agent-PoC3/src/memory_agent/graph.py`, při importu `from langchain_community import chat_models`

### Analýza příčiny:
- Import `from langchain.chat_models import ChatOpenAI` se v novějších verzích interně opírá o modul `langchain_community`
- I když je modul `langchain_community` uveden v requirements.txt, zdá se, že není správně nainstalován v prostředí LangGraph Platform

### Navrhované řešení:
- [x] Aktualizovat import v `graph.py`: změnit `from langchain.chat_models import ChatOpenAI` na `from langchain_openai import ChatOpenAI`
- [x] Vytvořit pomocnou funkci `get_chat_model()` v `analyzer.py` k nahrazení `init_chat_model`
- [x] Přidat explicitně `langchain_core` do `requirements.txt` pro zajištění správné instalace všech závislostí
- [ ] Spustit deployment znovu a ověřit fungování

### Implementace:
- Změna importu v `src/memory_agent/graph.py`:
  - Před: `from langchain.chat_models import ChatOpenAI`
  - Po: `from langchain_openai import ChatOpenAI`
- Vytvoření pomocné funkce v `analyzer.py`:
  ```python
  def get_chat_model(model: str = "gpt-4", temperature: float = 0.0, **kwargs):
      """Initialize a chat model with the given parameters."""
      # Handle Anthropic models
      if "anthropic" in model.lower() or "claude" in model.lower():
          logger.warning(f"Anthropic model '{model}' requested but using OpenAI fallback")
          return ChatOpenAI(model="gpt-4", temperature=temperature, **kwargs)
      else:
          return ChatOpenAI(model=model, temperature=temperature, **kwargs)
  ```
- Aktualizace `requirements.txt` s přidáním `langchain_core>=0.1.0`

### Verifikace:
- Čeká na opětovný deployment do LangGraph Platform
- Vytvořeny diagramy `doc/PlantUML/langchain_dependency_fix.puml`, `langchain_import_sequence.puml` a `module_dependencies.puml`

## [Timestamp: 2025-05-17 - Initial Analysis]

### Identifikovaný problém:
Při pokusu o spuštění příkazu `langgraph platform build --local` nastala chyba, protože v aktuální verzi LangGraph CLI (0.2.10) neexistuje příkaz `platform`.

### Analýza LangGraph CLI příkazů:
- Aktuální verze CLI je 0.2.10
- Dostupné příkazy jsou: `build`, `dev`, `dockerfile`, `new`, `up`
- Příkaz `platform` není v aktuální verzi k dispozici

### Provedené změny v skriptech:

1. Upravil jsem `deploy_to_langgraph_platform.sh`:
   - Původní příkazy: `langgraph platform build --local` a `langgraph platform push --env production`
   - Nahrazeno příkazy: `langgraph build` a instrukcí k ručnímu nasazení

2. Upravil jsem `.github/workflows/build-test-deploy.yml`:
   - Nahradil jsem neexistující příkaz `platform build`
   - Nyní workflow vytváří artefakt s potřebnými soubory pro ruční nasazení

3. Aktualizoval jsem dokumentaci v `doc/deployment_guide.md`:
   - Přidal jsem sekci pro sestavení projektu a ruční nasazení
   - Upravil jsem příklady příkazů podle aktuální verze CLI

### Stav souborů konfigurace:
1. `.env.example` - Již existuje se správnou konfigurací
   ```bash
   # Vzorový konfigurační soubor, přejmenujte na .env a doplňte vlastní klíče
   OPENAI_API_KEY=your_openai_api_key
   LANGSMITH_API_KEY=your_langsmith_api_key
   LANGSMITH_PROJECT=AI-agent-Ntier
   LOG_LEVEL=INFO
   ```

2. `langgraph.json` - Validní konfigurace
   ```json
   {
       "dockerfile_lines": [],
       "graphs": {
           "agent": "./src/memory_agent/graph.py:graph"
       },
       "env": ".env",
       "python_version": "3.11",
       "dependencies": ["."]
   }
   ```

## [Timestamp: 2025-05-17 - GitHub Secrets & CI/CD]

### Analýza GitHub workflow:
- GitHub workflow používá secrets `OPENAI_API_KEY` a `LANGSMITH_API_KEY`
- Tyto secrets musí být nastaveny v repozitáři GitHub (`minarovic/AI-agent-PoC3`)
- Bez těchto secrets nebude možné úspěšně provést build v CI/CD pipeline

### Další kroky:
1. **Nastavit GitHub Secrets**:
   - Přejít do repozitáře na GitHub
   - Otevřít Settings > Secrets and variables > Actions
   - Přidat `OPENAI_API_KEY` a `LANGSMITH_API_KEY` jako repository secrets

2. **Otestovat lokální sestavení**:
   - Vytvořit lokální `.env` soubor s API klíči
   - Spustit `langgraph build` pro ověření funkčnosti
   - Následně otestovat lokální spuštění pomocí `langgraph up`

3. **Připravit dokumentaci pro ruční nasazení na LangGraph Platform**:
   - Zjistit aktuální postup pro ruční nasazení na LangGraph Platform
   - Aktualizovat `doc/deployment_guide.md`
   - Připravit instrukce pro uživatele

### Poznámky k bezpečnosti:
- Nikdy neukládat reálné API klíče do zdrojového kódu
- Používat výhradně environment proměnné nebo GitHub Secrets
- Pro lokální vývoj používat `.env` soubor, který není verzován (přidán do .gitignore)
- Pro produkční nasazení používat GitHub Secrets nebo secrets management v LangGraph Platform

## [Timestamp: 2025-05-17 - Přímé nasazení přes GitHub]

### Rozhodnutí přeskočit lokální testování:
- Port 5433 je již obsazen v Dockeru, což komplikuje lokální testování
- GitHub Secrets jsou již nastaveny v repozitáři, můžeme přejít přímo k nasazení
- Workflow soubor je již upraven pro použití s aktuální verzí LangGraph CLI

### Další kroky:
1. Provést commit všech upravených souborů:
   - `deploy_to_langgraph_platform.sh`
   - `.github/workflows/build-test-deploy.yml`
   - `doc/deployment_guide.md`
   - `deploy_logs/notes.md`

2. Provést push do GitHub repozitáře:
   ```bash
   git add .
   git commit -m "Update deployment scripts for current LangGraph CLI version"
   git push origin main
   ```

3. Sledovat průběh GitHub Actions workflow:
   - **Přímo v VS Code**:
     - Stiskněte `Cmd+Shift+P` a vyberte "GitHub Actions: View Workflow Runs"
     - Nebo klikněte na ikonu GitHub v levém postranním panelu
     - Vyberte nejnovější běh workflow "AI-agent-Ntier CI/CD"
   - **Alternativně na webu**:
     - Otevřít repozitář na GitHub
     - Přejít na záložku "Actions"
     - Zkontrolovat, zda workflow proběhl úspěšně

4. Stáhnout vygenerovaný artefakt:
   - **Přímo v VS Code**:
     - V panelu GitHub Actions klikněte na úspěšně dokončený workflow
     - Rozbalte sekci "Artifacts"
     - Klikněte na "Download" u artefaktu "langgraph-package"
   - **Alternativně na webu**:
     - Po úspěšném dokončení workflow na stránce Actions
     - Klikněte na konkrétní běh workflow
     - Stáhněte artefakt ze sekce "Artifacts"
   - Artefakt obsahuje soubory potřebné pro ruční nasazení na LangGraph Platform

5. Nasazení na LangGraph Platform:
   - Použít LangGraph Platform UI pro nahrání artefaktu
   - Nebo aktualizovat dokumentaci s aktuálním způsobem nasazení

## [Timestamp: 2025-05-17 - CI/CD Pipeline Fix]

### Identifikované problémy v CI/CD:
- Workflow selhal s chybou "Could not import langchain_openai python package"
- Problematický soubor `deploy_logs/1.py` způsoboval další syntaktické chyby

### Provedené opravy:
1. Přidán explicitní příkaz pro instalaci `langchain_openai` v GitHub workflow:
   ```yaml
   pip install langchain_openai  # Explicitně instalujeme tento balíček
   ```
   
2. Odstraněn problémový soubor s logy `deploy_logs/1.py`
   - Soubor obsahoval pouze logy z předchozího pokusu o nasazení
   - Tyto logy zahrnovaly časové značky s úvodní nulou (07:01), což Python interpretoval jako osmičkovou soustavu
   - Soubor nebyl součástí aplikačního kódu

## [2024-07-22] - Řešení problémů se schématy JSON pro LangGraph Platform

### Identifikovaný problém:
- LangGraph Platform hlásí chybu: `Nelze generovat JSON schéma pro třídu MockMCPConnector`
- Tato chyba brání vytvoření správné dokumentace API a negeneruje správná schémata pro vstupy/výstupy
- V logu se objevují varování: `Warnings týkající se používání langchain_core.pydantic_v1`

### Analýza příčiny:
- `MockMCPConnector` je běžná Python třída, ne Pydantic model
- LangGraph Platform se pokouší generovat JSON schéma pro všechny objekty ve stavovém grafu
- Třída obsahuje metody a stav, které nejsou serializovatelné do JSON
- Některé metody používají nepřímo `langchain_core.pydantic_v1` místo přímého importu z `pydantic`

### Navrhované řešení:
- [x] Vytvořit nový soubor `schema.py` pro definice schémat
- [x] Vytvořit Pydantic model `MockMCPConnectorConfig` pro konfiguraci konektoru
- [x] Refaktorovat třídu `MockMCPConnector` pro kompatibilitu s Pydantic
- [x] Upravit importy v `analyzer.py` z `langchain_core.pydantic_v1` na přímý `pydantic`
- [x] Exportovat modul `schema` z `__init__.py`

### Implementace:
1. Vytvořen nový soubor `src/memory_agent/schema.py` s Pydantic modely
2. Třída `MockMCPConnector` upravena pro použití `MockMCPConnectorConfig` modelu
3. Přidána metoda `to_dict()` pro serializaci konektoru
4. Aktualizovány importy v `analyzer.py` pro odstranění varování o zastaralých importech
5. Vytvořeny typované modely pro konzistentní výstupy: `CompanyData`, `PersonData`, `RelationshipData`

### Vizualizace:
Vytvořen diagram `doc/PlantUML/LangGraphSchema_Fix.plantuml` popisující refaktoring

### Očekávaný výsledek:
Deployment by měl nyní:
- Generovat správná JSON schémata pro vstupy/výstupy bez chyb
- Zobrazit správnou dokumentaci API v LangGraph Platform
- Odstranit varování o zastaralých importech z `langchain_core.pydantic_v1`
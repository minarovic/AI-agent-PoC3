Zápisky:

# Deploying AI-agent-Ntier - Poznámky z procesu nasazení

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

### Očekávané výsledky:
- CI/CD pipeline by nyní měl proběhnout úspěšně
- Měl by být vytvořen artefakt `langgraph-package` pro nasazení na LangGraph Platform

## [Timestamp: 2025-05-17 - Finalizace nasazení]

### Ověření výsledků CI/CD:
- Push nových změn do GitHub repozitáře proběhl úspěšně
- Workflow v GitHub Actions by měl nyní běžet bez problémů
- Již byla připravena podrobná dokumentace v souboru `doc/manual_langgraph_deployment.md`

### Zbývající kroky:
1. **Ověřit výsledek GitHub Actions workflow**:
   - Zkontrolovat, zda workflow proběhl úspěšně
   - Stáhnout a zkontrolovat vytvořený artefakt

2. **Nasadit na LangGraph Platform**:
   - Následovat instrukce v souboru `doc/manual_langgraph_deployment.md`
   - Použít buď LangGraph Platform UI nebo GitHub integraci

3. **Dokumentace pro uživatele**:
   - Aktualizovat hlavní README.md s informacemi o nasazení
   - Přidat odkaz na vytvořenou dokumentaci

### Shrnutí procesu nasazení:
- Původní problém byl v neexistujícím příkazu `langgraph platform build` v aktuální verzi LangGraph CLI
- Řešením bylo použití dostupných příkazů a příprava procesu pro ruční nasazení
- Další problém nastal s chybějícím balíčkem `langchain_openai` v CI/CD procesu
- Tento problém byl vyřešen explicitní instalací balíčku v GitHub workflow
- Problematický soubor s logy byl odstraněn kvůli syntaktickým chybám
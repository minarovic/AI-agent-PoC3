# Instrukce pro nasazení AI-agent-Ntier s opravou JSON schématu

## Příprava prostředí

Před nasazením je potřeba nastavit potřebné proměnné prostředí:

```bash
# Nastavit OpenAI API klíč
export OPENAI_API_KEY=sk-...  # Nahraďte vaším OpenAI API klíčem

# Nastavit LangSmith API klíč pro sledování
export LANGSMITH_API_KEY=ls-...  # Nahraďte vaším LangSmith API klíčem

# Nastavit název projektu v LangSmith
export LANGSMITH_PROJECT=AI-agent-Ntier
```

## Kroky nasazení

### 1. Ujistěte se, že jste v branch s opravou JSON schématu

```bash
# Zkontrolujte aktuální branch
git branch

# Pokud nejste v branch langraph-schema-fix, přepněte se do ní
git checkout langraph-schema-fix
```

### 2. Spusťte skript pro nasazení

```bash
./deploy_to_langgraph_platform.sh
```

### 3. V menu zvolte možnost 2: "Sestavení a nasazení na LangGraph Platform"

```
Vyberte způsob nasazení:
1) Lokální vývojový server (langgraph dev)
2) Sestavení a nasazení na LangGraph Platform
3) Pouze sestavení bez nasazení

Vaše volba: 2
```

### 4. Sledujte proces sestavení

Skript spustí příkaz:

```bash
langgraph build --tag ai-agent-ntier:latest
```

Po úspěšném sestavení uvidíte zprávu podobnou této:

```
Sestavení dokončeno. Docker image: ai-agent-ntier:latest
Připraven k nasazení na LangGraph Platform...
Pro nasazení použijte oficiální LangGraph CLI nástroje nebo LangGraph Platform UI
```

### 5. Nasaďte projekt na LangGraph Platform

```bash
# Nasazení pomocí langgraph up
langgraph up
```

### 6. Ověření nasazení

Po úspěšném nasazení zkontrolujte logy v LangGraph Platform UI nebo pomocí příkazu:

```bash
langgraph logs
```

Ověřte, že se již **nevyskytuje chyba**:
```
Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'memory_agent.tools.MockMCPConnector'>)
```

### 7. Sloučení opravy do hlavní větve

Po ověření, že nasazení funguje správně:

```bash
# Přepnutí do hlavní větve
git checkout main

# Sloučení opravy
git merge langraph-schema-fix

# Push změn do repozitáře
git push origin main
```

## Řešení potíží

### Chyba s chybějícími API klíči

Pokud vidíte chybu o chybějících API klíčích:

```
OPENAI_API_KEY není nastaven, použijte příkaz:
export OPENAI_API_KEY=your_api_key
```

Ujistěte se, že jste nastavili všechny potřebné proměnné prostředí.

### Chyba při sestavení Docker image

Pokud nastane chyba při sestavení Docker image, zkontrolujte:

1. Zda máte nainstalovaný Docker a běží
2. Zda máte nejnovější verzi LangGraph CLI:
   ```bash
   pip install --upgrade "langgraph-cli[inmem]"
   ```

### Problémy s nasazením na LangGraph Platform

Pokud nasazení na LangGraph Platform selže:

1. Zkontrolujte, že máte správně nakonfigurovaný přístup k LangGraph Platform
2. Ověřte, že používáte aktuální verzi LangGraph CLI
3. Zkontrolujte logy nasazení pro identifikaci konkrétní chyby

## Dokumentace

Podrobné informace o provedených změnách najdete v:

- `deploy_logs/schema_fix_18_05_2025.md` - Detailní popis opravy JSON schématu
- `deploy_logs/deployment_plan_18_05_2025.md` - Plán nasazení
- `doc/PlantUML/LangGraph_Deployment_Flow.plantuml` - Vizuální diagram procesu nasazení

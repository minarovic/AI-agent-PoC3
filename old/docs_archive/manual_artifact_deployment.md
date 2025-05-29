# Manuální nasazení na LangGraph Platform pomocí artefaktu z GitHub Actions

Tento dokument obsahuje podrobné instrukce pro nasazení projektu AI-agent-Ntier na LangGraph Platform pomocí artefaktu vytvořeného v GitHub Actions workflow.

## Předpoklady

- Stažený artefakt `langgraph-package.tar.gz` z GitHub Actions workflow
- Účet na LangGraph Platform (https://smith.langchain.com/)
- Nastavené proměnné prostředí:
  - `OPENAI_API_KEY`
  - `LANGSMITH_API_KEY`

## Postup nasazení

### 1. Příprava artefaktu

```bash
# Vytvořte pracovní adresář
mkdir -p ~/langgraph-deploy && cd ~/langgraph-deploy

# Rozbalte stažený artefakt
tar -xzvf ~/Downloads/langgraph-package.tar.gz

# Ověřte obsah
ls -la artifacts/
```

Po rozbalení byste měli vidět adresářovou strukturu obsahující:
- `.langgraph/` - Adresář s build soubory
- `langgraph.json` - Konfigurační soubor

### 2. Nasazení přes LangGraph Platform UI

1. Přihlaste se na [LangGraph Platform](https://smith.langchain.com/)
2. Přejděte do sekce "Deployments"
3. Klikněte na tlačítko "Create new deployment"
4. Vyberte možnost "Upload files"
5. Nahrajte obsah adresáře `.langgraph` (všechny soubory z tohoto adresáře)
6. V sekci "Environment Variables" nastavte potřebné proměnné prostředí:
   - `OPENAI_API_KEY`: váš OpenAI API klíč
   - `LANGSMITH_API_KEY`: váš LangSmith API klíč
   - `LANGSMITH_PROJECT`: "AI-agent-Ntier"
   - `LOG_LEVEL`: "INFO"
7. Klikněte na "Deploy"

### 3. Alternativně: Nasazení přes GitHub integraci

Pokud preferujete automatické nasazení při každém push do repozitáře:

1. V LangGraph Platform přejděte do sekce "Settings"
2. Vyberte "Integrations"
3. Klikněte na "Connect" u GitHub
4. Autorizujte LangGraph Platform pro přístup k vašemu GitHub účtu
5. Vyberte repozitář `minarovic/AI-agent-PoC3`
6. Nastavte větev pro automatické nasazení (obvykle `main`)
7. Nastavte environment proměnné stejně jako v předchozím kroku
8. Dokončete konfiguraci

### 4. Ověření nasazení

Po úspěšném nasazení otestujte API endpoint:

```bash
# Nahraďte YOUR_DEPLOYMENT_URL a YOUR_API_KEY skutečnými hodnotami
curl -X POST https://YOUR_DEPLOYMENT_URL.langgraph.com/agents/agent/invoke \
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

### 5. Monitoring a debugging

1. V LangGraph Platform přejděte do detailu vašeho nasazení
2. Sekce "Logs" zobrazuje logy z běžící aplikace
3. Sekce "Traces" umožňuje prohlížet trace grafu (vyžaduje nastavení `LANGSMITH_API_KEY`)

### 6. Řešení problémů

Pokud nasazení selže nebo aplikace nefunguje správně:

1. Zkontrolujte logy nasazení v LangGraph Platform
2. Ověřte, že všechny environment proměnné jsou správně nastaveny
3. Ujistěte se, že struktura `.langgraph` adresáře odpovídá očekávané struktuře
4. Zkontrolujte, zda `langgraph.json` obsahuje správnou cestu ke grafu

## Závěr

Po úspěšném nasazení máte funkční instanci Memory Agent běžící na LangGraph Platform. Můžete k ní přistupovat přes API nebo prostřednictvím LangGraph Studio UI.

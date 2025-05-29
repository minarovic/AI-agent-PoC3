# Manuální nasazení artefaktu - Kontrolní seznam

## 1. Vytvořit pracovní adresář a připravit artefakt

```bash
# Vytvořit pracovní adresář
mkdir -p ~/langgraph-deploy && cd ~/langgraph-deploy

# Rozbalit stažený artefakt (podle formátu)
# Pro .zip:
unzip ~/Downloads/langgraph-package.zip -d ./
# Pro .tar.gz:
tar -xzvf ~/Downloads/langgraph-package.tar.gz

# Ověřit obsah
ls -la artifacts/
```

## 2. Postup nasazení přes LangGraph Platform UI

1. [ ] Přihlásit se na [LangGraph Platform](https://smith.langchain.com/)
2. [ ] Přejít do sekce "Deployments"
3. [ ] Kliknout na "Create new deployment"
4. [ ] Vybrat možnost "Upload files"
5. [ ] Nahrát obsah adresáře `.langgraph` (všechny soubory)
6. [ ] Nastavit environment proměnné:
   - [ ] `OPENAI_API_KEY`: váš OpenAI API klíč
   - [ ] `LANGSMITH_API_KEY`: váš LangSmith API klíč 
   - [ ] `LANGSMITH_PROJECT`: "AI-agent-Ntier"
   - [ ] `LOG_LEVEL`: "INFO"
7. [ ] Kliknout na "Deploy"
8. [ ] Počkat na dokončení deploymentu

## 3. Ověřit nasazení

```bash
# Nahradit YOUR_DEPLOYMENT_URL a YOUR_API_KEY skutečnými hodnotami
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

## 4. Monitoring a debugging

1. [ ] Zkontrolovat logy v sekci "Logs" v detailu nasazení
2. [ ] Ověřit, že aplikace běží správně a odpovídá na dotazy

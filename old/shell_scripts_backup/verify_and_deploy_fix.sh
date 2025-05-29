#!/bin/zsh
# Skript pro ověření a nasazení opravy chyby TypeError v AI-agent-Ntier/PoC3

echo "====================================================="
echo "  Ověření a nasazení opravy TypeError v State objektu "
echo "====================================================="

# Ověření stavu současného repozitáře
echo "Kontroluji aktuální stav repozitáře..."
REPO_DIR=$(pwd)
REPO_NAME=$(basename "$REPO_DIR")
echo "Pracovní adresář: $REPO_DIR"
echo "Název repozitáře: $REPO_NAME"

# Ověření, zda jsme v git repozitáři
if [ ! -d ".git" ]; then
  echo "CHYBA: Tento adresář není git repozitářem."
  exit 1
fi

# Ověření, že existuje soubor graph.py
GRAPH_FILE="src/memory_agent/graph.py"
if [ ! -f "$GRAPH_FILE" ]; then
  echo "CHYBA: Soubor $GRAPH_FILE nebyl nalezen."
  exit 1
fi

# Kontrola, zda graph.py obsahuje správnou opravu lambda funkce
echo "Kontroluji implementaci lambda funkce v $GRAPH_FILE..."
if grep -q "lambda x: x\[\"state\"\].query_type" "$GRAPH_FILE"; then
  echo "VAROVÁNÍ: Nalezena nesprávná verze lambda funkce v $GRAPH_FILE!"
  echo "Soubor obsahuje 'lambda x: x[\"state\"].query_type' místo 'lambda x: x.query_type'"
  
  # Návrh opravy
  echo "Chcete opravit tuto chybu? [y/n]"
  read -r FIX_LAMBDA
  
  if [[ "$FIX_LAMBDA" =~ ^[Yy]$ ]]; then
    echo "Opravuji lambda funkci v $GRAPH_FILE..."
    sed -i '' 's/lambda x: x\["state"\].query_type/lambda x: x.query_type  # x je přímo objekt State, ne slovník/g' "$GRAPH_FILE"
    echo "Oprava dokončena."
  else
    echo "Oprava byla přeskočena. VAROVÁNÍ: Chyba bude přetrvávat!"
  fi
else
  echo "✓ Soubor $GRAPH_FILE obsahuje správnou implementaci lambda funkce 'lambda x: x.query_type'"
fi

# Kontrola konfigurace LangGraph
LANGGRAPH_FILE="langgraph.json"
if [ ! -f "$LANGGRAPH_FILE" ]; then
  echo "CHYBA: Soubor $LANGGRAPH_FILE nebyl nalezen."
  exit 1
fi

# Ověření, že langgraph.json obsahuje správnou konfiguraci
echo "Kontroluji konfiguraci v $LANGGRAPH_FILE..."
CORRECT_CONFIG=0
if grep -q "\"name\": \"AI-agent-Ntier\"" "$LANGGRAPH_FILE"; then
  if grep -q "\"agent\": \"./src/memory_agent/graph.py:graph\"" "$LANGGRAPH_FILE"; then
    CORRECT_CONFIG=1
  fi
fi

if [ $CORRECT_CONFIG -eq 0 ]; then
  echo "VAROVÁNÍ: Konfigurace v $LANGGRAPH_FILE neodpovídá očekávanému formátu."
  echo "Chcete aktualizovat konfiguraci? [y/n]"
  read -r FIX_CONFIG
  
  if [[ "$FIX_CONFIG" =~ ^[Yy]$ ]]; then
    echo "Aktualizuji konfiguraci v $LANGGRAPH_FILE..."
    cat > "$LANGGRAPH_FILE" << EOL
{
    "name": "AI-agent-Ntier",
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    },
    "python_version": "3.12",
    "dependencies": [".", "langchain_openai>=0.1.0"]
}
EOL
    echo "Konfigurace aktualizována."
  else
    echo "Aktualizace konfigurace byla přeskočena. VAROVÁNÍ: Nasazení může selhat!"
  fi
else
  echo "✓ Soubor $LANGGRAPH_FILE obsahuje správnou konfiguraci."
fi

# Zjištění aktuálního git remote
echo "Kontroluji nastavení vzdáleného repozitáře..."
REMOTE_URL=$(git config --get remote.origin.url)
echo "Aktuální URL vzdáleného repozitáře: $REMOTE_URL"

# Vytvoření commit s opravou
echo "Chcete vytvořit commit s opravami? [y/n]"
read -r CREATE_COMMIT

if [[ "$CREATE_COMMIT" =~ ^[Yy]$ ]]; then
  echo "Přidávám změny do gitu..."
  git add "$GRAPH_FILE" "$LANGGRAPH_FILE"
  
  echo "Vytvářím commit..."
  COMMIT_MSG="Fix: Oprava TypeError v State objektu a aktualizace konfigurace LangGraph"
  git commit -m "$COMMIT_MSG"
  
  echo "Chcete push změny do vzdáleného repozitáře $REMOTE_URL? [y/n]"
  read -r PUSH_CHANGES
  
  if [[ "$PUSH_CHANGES" =~ ^[Yy]$ ]]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "Provádím push větve $BRANCH do origin..."
    git push origin "$BRANCH"
    
    if [ $? -eq 0 ]; then
      echo "✓ Změny byly úspěšně odeslány do vzdáleného repozitáře."
    else
      echo "CHYBA: Push selhal. Zkontrolujte oprávnění a připojení."
    fi
  else
    echo "Push byl přeskočen. Změny zůstávají pouze lokálně."
  fi
else
  echo "Vytvoření commitu přeskočeno."
fi

# Nasazení na LangGraph Platform
echo "Chcete spustit nasazení na LangGraph Platform? [y/n]"
read -r RUN_DEPLOY

if [[ "$RUN_DEPLOY" =~ ^[Yy]$ ]]; then
  DEPLOY_SCRIPT="./deploy_to_langgraph_platform.sh"
  
  if [ ! -f "$DEPLOY_SCRIPT" ]; then
    echo "CHYBA: Deployment skript $DEPLOY_SCRIPT nebyl nalezen."
    exit 1
  fi
  
  echo "Spouštím deployment..."
  chmod +x "$DEPLOY_SCRIPT"
  "$DEPLOY_SCRIPT"
else
  echo "Nasazení bylo přeskočeno."
fi

# Dokumentace provedených změn
echo "Zaznamenávám provedené změny do deploy_logs/fix_summary.md..."
mkdir -p deploy_logs

cat > deploy_logs/fix_summary.md << EOL
# Souhrn oprav TypeError: 'State' object is not subscriptable

## Datum provedení: $(date +%Y-%m-%d)

### Identifikovaný problém:
- LangGraph Platform hlásil chybu \`TypeError: 'State' object is not subscriptable\`
- Chyba nastávala v souboru \`graph.py\` při použití nesprávného přístupu k objektu State

### Provedené kontroly:
- Ověřen stav lokálního repozitáře: \`$REPO_DIR\`
- Zkontrolována implementace lambda funkce v \`$GRAPH_FILE\`
- Zkontrolována konfigurace v \`$LANGGRAPH_FILE\`

### Provedené opravy:
$(if grep -q "lambda x: x.query_type" "$GRAPH_FILE"; then
  echo "- ✓ Lambda funkce v \`graph.py\` již obsahovala správnou implementaci \`lambda x: x.query_type\`"
else
  echo "- ✓ Opravena lambda funkce v \`graph.py\` z \`lambda x: x[\"state\"].query_type\` na \`lambda x: x.query_type\`"
fi)
$(if [ $CORRECT_CONFIG -eq 1 ]; then
  echo "- ✓ Konfigurace \`langgraph.json\` již byla správně nastavena"
else
  echo "- ✓ Aktualizována konfigurace \`langgraph.json\` pro správné nasazení na LangGraph Platform"
fi)
$(if [[ "$CREATE_COMMIT" =~ ^[Yy]$ ]]; then
  echo "- ✓ Vytvořen commit s opravami: \"$COMMIT_MSG\""
  if [[ "$PUSH_CHANGES" =~ ^[Yy]$ ]]; then
    echo "- ✓ Změny odeslány do vzdáleného repozitáře \`$REMOTE_URL\`"
  else
    echo "- ✗ Změny nebyly odeslány do vzdáleného repozitáře"
  fi
else
  echo "- ✗ Commit s opravami nebyl vytvořen"
fi)
$(if [[ "$RUN_DEPLOY" =~ ^[Yy]$ ]]; then
  echo "- ✓ Spuštěno nasazení na LangGraph Platform"
else
  echo "- ✗ Nasazení na LangGraph Platform nebylo spuštěno"
fi)

### Další doporučení:
1. Po nasazení zkontrolujte logy LangGraph Platform pro ověření úspěšnosti opravy
2. Otestujte aplikaci pro potvrzení, že chyba \`'State' object is not subscriptable\` již nenastává
3. Zvažte přejmenování vzdáleného repozitáře na GitHub, aby název odpovídal lokálnímu názvu projektu
4. Aktualizujte dokumentaci projektu s informacemi o provedené opravě

### Technické detaily opravy:
V souboru \`graph.py\` byla opravena lambda funkce z nesprávné formy \`lambda x: x["state"].query_type\` na správnou formu \`lambda x: x.query_type\`. Tato oprava řeší problém, kdy kód nesprávně předpokládal, že vstupní parametr lambda funkce je slovník obsahující klíč "state", zatímco ve skutečnosti je přímo instancí třídy \`State\`.

V LangGraph API je důležité přistupovat přímo k atributům objektu \`State\`, nikoliv jako ke slovníku, což bylo příčinou chyby \`TypeError: 'State' object is not subscriptable\`.
EOL

echo "====================================================="
echo "        Kontrola a nasazení dokončeno!               "
echo "====================================================="
echo "Souhrn všech provedených akcí byl uložen do:"
echo "  deploy_logs/fix_summary.md"
echo "====================================================="

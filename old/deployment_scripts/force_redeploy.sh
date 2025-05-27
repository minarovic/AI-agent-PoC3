#!/bin/bash

# Force redeploy script pro LangGraph Platform
# Tento skript vytvoří drobnou změnu a provede nové nasazení
# Účelem je forcovat nový deploy na LangGraph Platform

echo "=== FORCE REDEPLOY PRO LANGGRAPH PLATFORM ==="
echo "Datum a čas: $(date)"

# Vytvoření force_redeploy.md souboru
echo "# Force redeploy - $(date)" > force_redeploy.md
echo "Vytvořil jsem force_redeploy.md s aktuálním datem a časem"

# Přidání do gitu
git add force_redeploy.md
git commit -m "Force redeploy pro opravu mcp_connector chyby"

# Spuštění deploy skriptu pro odeslání na GitHub
./deploy_to_github.sh

echo ""
echo "=== DOKONČENO ==="
echo "Zkontrolujte GitHub Actions workflow a LangGraph Platform pro status deploymentu"
echo "Po dokončení nasazení otestujte aplikaci znovu"

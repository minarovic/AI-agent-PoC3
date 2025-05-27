#!/bin/zsh
# Script pro commit a push opravy chyby indentace

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "src/memory_agent" ]; then
  echo "Error: Tento skript musí být spuštěn z kořenového adresáře projektu AI-agent-Ntier"
  exit 1
fi

# Příprava commit zprávy
COMMIT_MSG=$(cat ./deploy_logs/commit_message_indentation_fix.txt)

# Přidání změněných souborů do stage
git add src/memory_agent/analyzer.py
git add src/memory_agent/schema.py
git add deploy_logs/indentation_fix_18_05_2025.md
git add deploy_logs/indentation_error_notes.md
git add deploy_logs/deployment_check_18_05_2025.md
git add deploy_logs/deployment_completion_18_05_2025.md
git add deploy_logs/commit_message_indentation_fix.txt
git add doc/PlantUML/IndentationError_Fix_Flow.plantuml

# Vytvoření commitu
git commit -m "$COMMIT_MSG"

# Push změn do branch langraph-schema-fix
git push origin langraph-schema-fix

echo "Změny byly commitovány a odeslány do branch langraph-schema-fix"
echo "Nyní můžete sledovat výsledky GitHub Action v repozitáři."

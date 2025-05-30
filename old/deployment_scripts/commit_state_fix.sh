#!/bin/bash
# Script pro commit a push opravy State not subscriptable do GitHub

echo "Vytvářím commit s opravou TypeError: 'State' object is not subscriptable..."

# Přidání souborů s opravou a dokumentací do gitu
git add /Users/marekminarovic/AI-agent-Ntier/src/memory_agent/graph.py
git add /Users/marekminarovic/AI-agent-Ntier/deploy_logs/state_subscriptable_verification_18_05_2025.md
git add /Users/marekminarovic/AI-agent-Ntier/doc/PlantUML/State_Not_Subscriptable_Fix_Verification.plantuml
git add /Users/marekminarovic/AI-agent-Ntier/.github/copilot-instructions.md

# Commit změn
git commit -m "Oprava TypeError: 'State' object is not subscriptable v graph.py"

echo "Committing změn dokončen."
echo "Pro odeslání změn na GitHub použijte příkaz: git push origin langraph-schema-fix"
echo "Pro nasazení na LangGraph Platform postupujte podle instrukcí v deployment_completion_18_05_2025.md"

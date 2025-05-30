#!/bin/bash
# Skript pro verifikaci GitHub Actions workflow

echo "===== VERIFIKACE GITHUB ACTIONS WORKFLOW ====="

# Nastavení pracovního adresáře
cd "$(dirname "$0")"
BASEDIR="$(pwd)"
WORKFLOW_DIR="$BASEDIR/.github/workflows"
NEW_WORKFLOW="$WORKFLOW_DIR/langgraph-platform-deploy.yml"

# Kontrola existence workflow adresáře
if [ ! -d "$WORKFLOW_DIR" ]; then
  echo "❌ CHYBA: Adresář .github/workflows neexistuje!"
  echo "Vytvářím adresářovou strukturu..."
  mkdir -p "$WORKFLOW_DIR"
  echo "✅ Adresář .github/workflows vytvořen."
fi

# Kontrola existence workflow souboru
if [ ! -f "$NEW_WORKFLOW" ]; then
  echo "❌ CHYBA: Soubor langgraph-platform-deploy.yml neexistuje!"
  echo "Je třeba vytvořit workflow soubor podle dokumentace."
  exit 1
fi

echo "✅ Workflow soubor langgraph-platform-deploy.yml existuje."

# Kontrola obsahu workflow souboru
echo "Kontroluji obsah workflow souboru..."

# Kontrola základních částí workflow
if ! grep -q "name: AI-agent-Ntier LangGraph Platform Deploy" "$NEW_WORKFLOW"; then
  echo "⚠️ VAROVÁNÍ: Název workflow neodpovídá očekávanému formátu."
else
  echo "✅ Název workflow je správný."
fi

# Kontrola jobu test
if ! grep -q "test:" "$NEW_WORKFLOW"; then
  echo "⚠️ VAROVÁNÍ: Job 'test' nenalezen."
else
  echo "✅ Job 'test' nalezen."
fi

# Kontrola verify-deployment jobu
if ! grep -q "verify-deployment:" "$NEW_WORKFLOW"; then
  echo "⚠️ VAROVÁNÍ: Job 'verify-deployment' nenalezen."
else
  echo "✅ Job 'verify-deployment' nalezen."
fi

# Kontrola deploy jobu
if ! grep -q "deploy:" "$NEW_WORKFLOW"; then
  echo "⚠️ VAROVÁNÍ: Job 'deploy' nenalezen."
else
  echo "✅ Job 'deploy' nalezen."
fi

# Kontrola použití deploy_to_github.sh
if ! grep -q "deploy_to_github.sh" "$NEW_WORKFLOW"; then
  echo "❌ CHYBA: Skript deploy_to_github.sh není použit ve workflow!"
  echo "Workflow by měl používat deploy_to_github.sh pro správný deployment."
  exit 1
else
  echo "✅ Skript deploy_to_github.sh je správně použit."
fi

# Kontrola přítomnosti Docker build kroků (neměly by tam být)
if grep -q "langgraph build" "$NEW_WORKFLOW"; then
  echo "❌ CHYBA: Workflow obsahuje 'langgraph build' příkaz!"
  echo "Toto je v rozporu s doporučeným workflow - odstraňte tento krok."
  exit 1
else
  echo "✅ Žádné lokální Docker build příkazy nenalezeny."
fi

# Kontrola přítomnosti artefaktů (neměly by se vytvářet Docker/build artefakty)
if grep -q "langgraph-package.tar.gz" "$NEW_WORKFLOW"; then
  echo "⚠️ VAROVÁNÍ: Workflow vytváří balíček 'langgraph-package.tar.gz'."
  echo "LangGraph Platform stahuje kód přímo z GitHubu, není třeba vytvářet balíčky."
fi

echo "===== VERIFIKACE WORKFLOW DOKONČENA ====="
echo "Workflow je připraven k použití."
echo "Pro nasazení na LangGraph Platform proveďte:"
echo "1. Commit a push změn do GitHub repozitáře"
echo "2. Propojení GitHub repozitáře s LangGraph Platform v administraci"

#!/bin/zsh
# Script pro lokální testování AI-agent-Ntier před nasazením na GitHub
# DŮLEŽITÉ: Tento skript slouží pouze pro lokální testování! Pro nasazení použijte deploy_to_github.sh

echo "====================================================="
echo "   AI-agent-Ntier - Lokální testování    "
echo "====================================================="

# Kontrola potřebných API klíčů
if [ -z "$OPENAI_API_KEY" ]; then
  echo "OPENAI_API_KEY není nastaven, použijte příkaz:"
  echo "export OPENAI_API_KEY=your_api_key"
  exit 1
fi

if [ -z "$LANGSMITH_API_KEY" ]; then
  echo "LANGSMITH_API_KEY není nastaven, použijte příkaz:"
  echo "export LANGSMITH_API_KEY=your_api_key"
  exit 1
fi

echo "Nastavuji LANGSMITH_PROJECT..."
export LANGSMITH_PROJECT="AI-agent-Ntier"

# Ověření konfigurace
echo "Kontroluji konfiguraci..."

if [ ! -f "langgraph.json" ]; then
  echo "Error: langgraph.json nenalezen!"
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "Soubor .env nenalezen, vytvářím vzorový soubor .env.example..."
  cat > .env.example << EOL
# Vzorový konfigurační soubor, přejmenujte na .env a doplňte vlastní klíče
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=$LANGSMITH_PROJECT
LOG_LEVEL=INFO
EOL
  echo "Vzorový soubor .env.example vytvořen. Přejmenujte ho na .env a doplňte vlastní API klíče."
  exit 1
fi

# Spustíme verifikaci
echo "Spouštím verifikaci deploymentu..."
./verify_deployment.sh

if [ $? -ne 0 ]; then
  echo "Verifikace selhala. Opravte chyby a zkuste to znovu."
  exit 1
fi

echo "Verifikace úspěšná."

# Možnosti lokálního testování
echo "Vyberte způsob testování:"
echo "1) Lokální vývojový server (langgraph serve)"
echo "2) Spustit testy"

read -r choice

case $choice in
  1)
    echo "Spouštím lokální LangGraph Platform server pro testování..."
    langgraph serve
    ;;
  2)
    echo "Spouštím testy..."
    pytest
    
    if [ $? -eq 0 ]; then
      echo "====================================================="
      echo "  Testování úspěšně dokončeno!  "
      echo "====================================================="
      echo "Pro nasazení na GitHub použijte:"
      echo "./deploy_to_github.sh"
    else
      echo "Testy selhaly. Opravte chyby a zkuste to znovu."
      exit 1
    fi
    ;;
  *)
    echo "Neplatná volba"
    exit 1
    ;;
esac

#!/bin/bash
set -e

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Zahajuji lokální deployment do LangGraph Platform...${NC}"

# Nastavení proměnných prostředí pokud nejsou již nastaveny
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}OPENAI_API_KEY není nastaven, načítám z .env souboru...${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Ověření python prostředí
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Vytvářím virtuální prostředí...${NC}"
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Build s požadovaným tag parametrem
echo -e "${YELLOW}Sestavuji LangGraph balíček...${NC}"
TAG_VERSION="v1.0.0"
langgraph build --local --tag "$TAG_VERSION"

# Spuštění lokálního deploymentu
echo -e "${YELLOW}Spouštím lokální deployment...${NC}"
langgraph up

echo -e "${GREEN}Lokální deployment úspěšně dokončen!${NC}"

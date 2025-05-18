#!/bin/zsh
# Script pro nasazení AI-agent-Ntier na LangGraph Platform

echo "====================================================="
echo "   AI-agent-Ntier - LangGraph Platform Deploy    "
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

# Kontrola, zda je nainstalovaný LangGraph CLI
if ! command -v langgraph &> /dev/null; then
  echo "Instaluji LangGraph CLI..."
  pip install --upgrade "langgraph-cli[inmem]"
fi

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

# Možnosti nasazení
echo "Vyberte způsob nasazení:"
echo "1) Lokální vývojový server (langgraph dev)"
echo "2) Sestavení a nasazení na LangGraph Platform"
echo "3) Pouze sestavení bez nasazení"

read -r choice

case $choice in
  1)
    echo "Spouštím lokální LangGraph Platform server pro testování..."
    langgraph dev
    ;;
  2)
    echo "Sestavuji projekt..."
    langgraph build --tag ai-agent-ntier:latest
    
    echo "Připraven k nasazení na LangGraph Platform..."
    echo "Pro nasazení použijte oficiální LangGraph CLI nástroje nebo LangGraph Platform UI"
    ;;
  3)
    echo "Sestavuji projekt..."
    langgraph build --tag ai-agent-ntier:latest
    echo "Hotovo. Pro lokální spuštění použijte: langgraph up"
    ;;
  *)
    echo "Neplatná volba"
    exit 1
    ;;
esac

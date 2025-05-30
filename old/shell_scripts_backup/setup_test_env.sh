#!/bin/bash
# Setup script pro testovací prostředí AI-agent-Ntier
set -e

echo "===== Nastavuji testovací prostředí pro AI-agent-Ntier ====="

# Kontrola, zda je Python nainstalován
if ! command -v python3 &> /dev/null; then
    echo "Python není nainstalován! Nainstalujte Python 3.11+"
    exit 1
fi

# Kontrola verze Pythonu
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Detekována verze Pythonu: $PYTHON_VERSION"
if [[ "$PYTHON_VERSION" < "3.11" ]]; then
    echo "Varování: Doporučená verze Pythonu je 3.11 nebo vyšší"
fi

# Vytvoření virtuálního prostředí, pokud neexistuje
if [ ! -d "venv" ]; then
    echo "Vytvářím virtuální prostředí..."
    python3 -m venv venv
fi

# Aktivace virtuálního prostředí
source venv/bin/activate
echo "Virtuální prostředí aktivováno"

# Instalace závislostí
echo "Instaluji závislosti..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Vytvoření .env souboru, pokud neexistuje
if [ ! -f ".env" ]; then
    echo "Vytvářím .env soubor z šablony..."
    cp .env.example .env
    echo "Upravte soubor .env a doplňte vlastní API klíče"
fi

# Kontrola přítomnosti potřebných API klíčů v .env
source .env
if [ -z "$OPENAI_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "VAROVÁNÍ: V .env souboru nejsou nastavené API klíče pro OpenAI nebo Anthropic"
    echo "Pro testování analyzéru je nutné tyto klíče doplnit"
fi

echo "===== Testovací prostředí připraveno ====="
echo "Pro spuštění testů použijte: pytest"
echo "Pro lokální spuštění LangGraph: ./run_langgraph_dev.sh"

#!/bin/bash
# Skript pro ověření čistého stavu kódu před nasazením
# Rozšířeno o validaci pro GitHub Actions workflow

set -e  # Ukončit při chybě

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Kontrola čistého stavu produkčního kódu ===${NC}"

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo -e "${RED}Error: Skript musí být spuštěn z kořenového adresáře projektu${NC}"
    exit 1
fi

# Kontrola, zda není v repozitáři sandbox
if [ -d "./sandbox" ]; then
    echo -e "${RED}Error: Detekován adresář sandbox/ v repozitáři!${NC}"
    echo -e "${YELLOW}Sandbox adresář nesmí být součástí produkčního kódu.${NC}"
    echo -e "${YELLOW}Přesuňte testovací kód do oficiálních testů nebo přidejte do .gitignore.${NC}"
    exit 1
fi

# Kontrola, zda nejsou přítomny testovací soubory mimo tests/
find . -type f -name "test_*.py" -not -path "./tests/*" | while read -r file; do
    echo -e "${RED}Error: Detekován testovací soubor mimo adresář tests/: $file${NC}"
    exit 1
done

# Kontrola, zda soubory v src/ neobsahují testovací kód
grep -r "test_" ./src/ --include="*.py" | grep -v "def test_" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${RED}Error: Detekován potenciální testovací kód v src/ adresáři${NC}"
    echo -e "${YELLOW}Výsledky hledání:${NC}"
    grep -r "test_" ./src/ --include="*.py" | grep -v "def test_"
    exit 1
fi

# Kontrola konfigurace LangGraph
if [ ! -f "langgraph.json" ]; then
    echo -e "${RED}Error: Chybí soubor langgraph.json${NC}"
    exit 1
fi

# Kontrola requirements
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Chybí soubor requirements.txt${NC}"
    exit 1
fi

# Ověření analyzátoru pomocí Pythonu
echo -e "${YELLOW}Ověření funkčnosti analyzátoru...${NC}"
python -c "from memory_agent.analyzer import analyze_company_query; analyze_company_query('Test query')" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Nefunkční analyzátor. Opravte chyby před nasazením.${NC}"
    exit 1
fi

# Kontrola GitHub Actions workflow
if [ ! -d "./.github/workflows" ]; then
    echo -e "${YELLOW}Varování: Není nastaven GitHub Actions workflow pro automatické testování${NC}"
    echo -e "${YELLOW}Zvažte přidání GitHub Actions workflow pro CI/CD${NC}"
else
    echo -e "${GREEN}OK: GitHub Actions workflow je nastaven${NC}"
    
    # Kontrola existence workflow souborů
    if [ ! -f "./.github/workflows/test_memory_agent.yml" ]; then
        echo -e "${YELLOW}Varování: Chybí soubor test_memory_agent.yml pro testování${NC}"
    fi
    
    if [ ! -f "./.github/workflows/validate_production_code.yml" ]; then
        echo -e "${YELLOW}Varování: Chybí soubor validate_production_code.yml pro validaci kódu${NC}"
    fi
fi

# Kontrola, že zdrojový kód lze importovat
echo "Kontrola importu kódu..."
if python -c "import memory_agent; print('Import successful')" && \
   python -c "from memory_agent import analyzer, graph, state, tools; print('Imports successful')"; then
    echo -e "${GREEN}OK: Import kódu funguje${NC}"
else
    echo -e "${RED}Error: Import kódu selhal${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kód je připraven k nasazení${NC}"
echo ""
exit 0

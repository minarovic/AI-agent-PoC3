#!/bin/bash
# Skript pro spuštění testů Memory Agent
#
# DŮLEŽITÉ: Tento skript by měl být používán pouze v těchto případech:
# 1. Pro ověření oprav po selhání GitHub Actions testů
# 2. Pro ověření funkčnosti před nasazením na LangGraph Platform
# 3. Pro experimentální účely v sandbox adresáři
#
# Pro běžný vývoj preferujte testování přes GitHub Actions!
#
# Použití:
#   ./run_tests.sh           - Spustí pouze oficiální testy
#   ./run_tests.sh --all     - Spustí oficiální testy i sandbox testy
#   ./run_tests.sh --sandbox - Spustí pouze sandbox testy
#   ./run_tests.sh --help    - Zobrazí nápovědu

set -e  # Ukončit při chybě

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Zobrazení nápovědy
if [ "$1" == "--help" ]; then
    echo -e "${YELLOW}Použití:${NC}"
    echo -e "  ./run_tests.sh           - Spustí pouze oficiální testy"
    echo -e "  ./run_tests.sh --all     - Spustí oficiální testy i sandbox testy"
    echo -e "  ./run_tests.sh --sandbox - Spustí pouze sandbox testy"
    echo -e "  ./run_tests.sh --help    - Zobrazí tuto nápovědu"
    echo
    echo -e "${YELLOW}DŮLEŽITÉ:${NC}"
    echo -e "Tento skript by měl být používán pouze v těchto případech:"
    echo -e "1. Pro ověření oprav po selhání GitHub Actions testů"
    echo -e "2. Pro ověření funkčnosti před nasazením na LangGraph Platform"
    echo -e "3. Pro experimentální účely v sandbox adresáři"
    echo
    echo -e "Pro běžný vývoj preferujte testování přes GitHub Actions!"
    exit 0
fi

echo -e "${YELLOW}=== Spouštění testů Memory Agent ===${NC}"
echo -e "${YELLOW}POZNÁMKA: Pro běžný vývoj preferujte testování přes GitHub Actions!${NC}"

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo -e "${RED}Error: Skript musí být spuštěn z kořenového adresáře projektu${NC}"
    exit 1
fi

# Kontrola existence pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}Instaluji pytest...${NC}"
    pip install pytest pytest-cov
fi

# Spuštění testů
echo -e "${YELLOW}Spouštím jednotkové testy...${NC}"

# Kontrola parametrů
if [ "$1" == "--all" ]; then
    echo -e "${YELLOW}Spouštím všechny testy včetně sandbox testů...${NC}"
    pytest tests/ -v
    
    if [ -d "./sandbox/testing_playground" ]; then
        echo -e "${YELLOW}Spouštím testy z sandbox/testing_playground...${NC}"
        for test_file in $(find ./sandbox/testing_playground -name "test_*.py"); do
            echo -e "${YELLOW}Spouštím $test_file...${NC}"
            python "$test_file"
        done
    fi
elif [ "$1" == "--sandbox" ]; then
    echo -e "${YELLOW}Spouštím pouze sandbox testy...${NC}"
    if [ -d "./sandbox/testing_playground" ]; then
        for test_file in $(find ./sandbox/testing_playground -name "test_*.py"); do
            echo -e "${YELLOW}Spouštím $test_file...${NC}"
            python "$test_file"
        done
    else
        echo -e "${RED}Adresář sandbox/testing_playground neexistuje${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Spouštím pouze oficiální testy...${NC}"
    pytest tests/ -v
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Všechny testy úspěšně prošly${NC}"
else
    echo -e "${RED}✗ Některé testy selhaly${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}=== Spouštění testů analyzátoru ===${NC}"
pytest tests/test_analyzer_llm.py -v

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Testy analyzátoru úspěšně prošly${NC}"
else
    echo -e "${RED}✗ Testy analyzátoru selhaly${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Všechny testy úspěšně dokončeny ===${NC}"

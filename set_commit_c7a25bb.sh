#!/bin/bash
# Skript pro nastavení commitu c7a25bb jako posledního commitu 
# a jeho přípravu na nahrání na LangGraph Platform

set -e  # Ukončit při chybě

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TARGET_COMMIT="c7a25bb"
TARGET_BRANCH="production-c7a25bb"

echo -e "${YELLOW}=== Nastavení commitu $TARGET_COMMIT jako poslední commit ===${NC}"

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo -e "${RED}Error: Skript musí být spuštěn z kořenového adresáře projektu${NC}"
    exit 1
fi

# Kontrola, zda máme správně inicializovaný git repozitář
if [ ! -d ".git" ]; then
    echo -e "${RED}Git repozitář není inicializován. Nelze provést manipulaci s commity.${NC}"
    exit 1
fi

# Kontrola, zda existuje cílový commit
echo -e "${YELLOW}Kontroluji existenci commitu $TARGET_COMMIT...${NC}"
if ! git cat-file -e $TARGET_COMMIT^{commit} 2>/dev/null; then
    echo -e "${RED}Commit $TARGET_COMMIT neexistuje v historii repozitáře!${NC}"
    exit 1
fi

# 1. Vytvoří novou větev z cílového commitu
echo -e "${YELLOW}Vytvářím novou větev '$TARGET_BRANCH' z commitu $TARGET_COMMIT...${NC}"
git checkout $TARGET_COMMIT
git checkout -b $TARGET_BRANCH

if [ $? -ne 0 ]; then
    echo -e "${RED}Vytvoření nové větve $TARGET_BRANCH selhalo!${NC}"
    exit 1
fi

# 2. Ověří, že jsme na správném commitu
CURRENT_COMMIT=$(git rev-parse --short HEAD)
if [ "$CURRENT_COMMIT" != "$TARGET_COMMIT" ]; then
    echo -e "${RED}Aktuální commit není $TARGET_COMMIT, ale $CURRENT_COMMIT!${NC}"
    exit 1
fi

echo -e "${GREEN}Nyní jste na větvi '$TARGET_BRANCH' s commitem $TARGET_COMMIT jako jediným commitem.${NC}"

# 3. Seznam produkčních souborů, které budou nahrány na GitHub
echo -e "${YELLOW}Seznam produkčních souborů, které budou nahrány na LangGraph Platform:${NC}"
git ls-tree -r --name-only HEAD src/memory_agent/ | grep -v "mock_" | sort
echo -e "langgraph.json\nrequirements.txt\nrequirements-platform.txt\nsetup.py"

# 4. Zobrazí instrukce pro nahrání na GitHub
echo -e "\n${YELLOW}Pro nahrání tohoto commitu na GitHub proveďte následující:${NC}"
echo -e "${BLUE}git push -f origin $TARGET_BRANCH:main${NC}"

echo -e "${GREEN}=== Proces nastavení commitu $TARGET_COMMIT jako posledního byl úspěšně dokončen ===${NC}"

# Zeptáme se, zda chceme rovnou provést force push
echo -e "${YELLOW}Chcete rovnou provést force push na GitHub? [y/N]${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Provádím force push na GitHub...${NC}"
    git push -f origin $TARGET_BRANCH:main
    echo -e "${GREEN}Force push byl dokončen. Změny jsou nyní na GitHubu.${NC}"
    echo -e "${GREEN}LangGraph Platform by nyní měl stáhnout a nasadit tuto verzi kódu.${NC}"
else
    echo -e "${BLUE}Force push nebyl proveden. Až budete připraveni, použijte příkaz:${NC}"
    echo -e "${BLUE}git push -f origin $TARGET_BRANCH:main${NC}"
fi

exit 0

#!/bin/bash
set -e

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Zahajuji nasazení kódu na GitHub...${NC}"

# Kontrola, zda máme správně inicializovaný git repozitář
if [ ! -d ".git" ]; then
    echo -e "${RED}Git repozitář není inicializován. Spusťte 'git init' a nastavte vzdálený repozitář.${NC}"
    exit 1
fi

# Kontrola existence klíčových souborů
if [ ! -f "langgraph.json" ]; then
    echo -e "${RED}Soubor langgraph.json neexistuje! Tento soubor je nutný pro deployment na LangGraph Platform.${NC}"
    exit 1
fi

# Očištění od Docker souborů a dalších konfiguračních souborů
echo -e "${YELLOW}Odstraňuji soubory, které by mohly způsobit konflikt při buildu...${NC}"
files_to_ignore=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    ".github/workflows"
)

for file in "${files_to_ignore[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Ignoruji soubor/složku: $file${NC}"
        git update-index --skip-worktree "$file" 2>/dev/null || true
    fi
done

# Přidání všech souborů ke commitu (kromě ignorovaných)
echo -e "${YELLOW}Přidávám soubory ke commitu...${NC}"
git add .

# Vrácení ignorovaných souborů do sledování
for file in "${files_to_ignore[@]}"; do
    if [ -e "$file" ]; then
        git update-index --no-skip-worktree "$file" 2>/dev/null || true
    fi
done

# Vytvoření commitu
echo -e "${YELLOW}Vytvářím commit...${NC}"
git commit -m "Deployment update $(date '+%Y-%m-%d %H:%M:%S')"

# Push na GitHub
echo -e "${YELLOW}Odesílám změny na GitHub...${NC}"
git push

echo -e "${GREEN}Deployment na GitHub dokončen!${NC}"
echo -e "${YELLOW}Nyní přejděte do administrace LangGraph Platform a propojte tento GitHub repozitář.${NC}"
echo -e "${YELLOW}URL: https://platform.langgraph.com${NC}"

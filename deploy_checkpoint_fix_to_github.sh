#!/bin/bash
set -e

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Zahajuji nasazení opravy checkpointů na GitHub...${NC}"

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

# Vytvoření nové větve pro opravu checkpointů
BRANCH_NAME="fix/checkpoint-serialization"
echo -e "${YELLOW}Vytvářím novou větev: $BRANCH_NAME...${NC}"
git checkout -b $BRANCH_NAME

# Spuštění testů ověřujících opravu
echo -e "${YELLOW}Spouštím testy pro ověření opravy...${NC}"
python test_checkpoint_fix.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Testy selhaly! Oprava není připravena k nasazení.${NC}"
    exit 1
fi

echo -e "${GREEN}Testy úspěšně prošly.${NC}"

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

# Přidání pouze souborů souvisejících s opravou checkpointů
echo -e "${YELLOW}Přidávám soubory s opravou ke commitu...${NC}"
git add src/memory_agent/state.py
git add src/memory_agent/graph_nodes.py
git add test_checkpoint_fix.py
git add deploy_logs/checkpoint_mcp_connector_fix.md

# Vrácení ignorovaných souborů do sledování
for file in "${files_to_ignore[@]}"; do
    if [ -e "$file" ]; then
        git update-index --no-skip-worktree "$file" 2>/dev/null || true
    fi
done

# Vytvoření commitu s detailním popisem opravy
echo -e "${YELLOW}Vytvářím commit...${NC}"
git commit -m "Fix: Oprava serializace checkpointů v Memory Agent

Tento commit řeší problém s checkpointy v LangGraph workflow, který byl způsoben 
neserializovatelnou instancí MockMCPConnector ve stavu. Implementované řešení zahrnuje:

1. Úpravu reducer funkce merge_dict_values v state.py pro robustní zpracování objektů bez metody copy()
2. Odstranění ukládání instance MockMCPConnector do stavu v uzlech grafu
3. Vytváření nové instance MockMCPConnector při každém volání místo spoléhání se na stav
4. Přidání testovacího skriptu pro ověření funkčnosti opravy

Tato oprava zajišťuje správné fungování checkpointů v Memory Agent workflow."

# Push na GitHub
echo -e "${YELLOW}Odesílám změny na GitHub...${NC}"
git push -u origin $BRANCH_NAME

echo -e "${GREEN}Deployment opravy checkpointů na GitHub dokončen!${NC}"
echo -e "${YELLOW}URL větve: https://github.com/username/AI-agent-Ntier/tree/$BRANCH_NAME${NC}"
echo -e "${YELLOW}Pro vytvoření Pull Requestu navštivte: https://github.com/username/AI-agent-Ntier/pull/new/$BRANCH_NAME${NC}"
echo -e "${YELLOW}Po schválení PR je možné propojit tento repozitář s LangGraph Platform.${NC}"

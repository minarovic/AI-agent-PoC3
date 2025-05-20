#!/bin/bash
# Deploy updatovaného kódu s podporou typů analýz na GitHub
# POZOR: Tento skript zajišťuje, že na GitHub se odešle pouze produkční kód,
# bez testovacích skriptů a dočasných souborů

set -e  # Ukončit při chybě

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Optimalizace workflow a nasazení typů analýz na GitHub ===${NC}"
echo -e "${YELLOW}POZNÁMKA: Na GitHub budou odeslány pouze produkční soubory${NC}"

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo -e "${RED}Error: Skript musí být spuštěn z kořenového adresáře projektu${NC}"
    exit 1
fi

# Kontrola existence klíčových souborů
if [ ! -f "langgraph.json" ]; then
    echo -e "${RED}Error: langgraph.json nenalezen! Tento soubor je nutný pro deployment na LangGraph Platform.${NC}"
    exit 1
fi

# Aktuální datum a čas pro commit zprávu
DATE=$(date "+%d.%m.%Y %H:%M")

# Kontrola změněných souborů
echo -e "${YELLOW}=== Kontrola změněných souborů ===${NC}"
git status -s

# Ověření funkčnosti
echo -e "${YELLOW}=== Ověření funkčnosti typů analýz ===${NC}"
python simple_test_analysis_types.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Testy selhaly. Deploy byl zrušen.${NC}"
    exit 1
fi

# Commit a push změn - pouze zdrojové kódy, ne Docker nebo build soubory
echo -e "${YELLOW}=== Příprava commitu a push na GitHub ===${NC}"

# Očištění od Docker souborů a dalších konfiguračních souborů
echo -e "${YELLOW}Odstraňuji soubory, které by mohly způsobit konflikt při buildu...${NC}"
files_to_ignore=(
    "Dockerfile"
    "Dockerfile.dev"
    "Dockerfile.local"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose.override.yml"
    ".dockerignore"
    ".github/workflows"
)

for file in "${files_to_ignore[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Ignoruji soubor/složku: $file${NC}"
        git update-index --skip-worktree "$file" 2>/dev/null || true
    fi
done

# Vytvoření souboru se seznamem souborů pro přidání do Gitu
echo -e "${YELLOW}=== Příprava pouze produkčních souborů pro GitHub ===${NC}"

# Seznam souborů, které budou odeslány na GitHub
production_files=(
    "src/memory_agent/analyzer.py"
    "src/memory_agent/tools.py"
    "src/memory_agent/graph_nodes.py"
    "src/memory_agent/state.py"
    "src/memory_agent/graph.py"
    "src/memory_agent/__init__.py"
    "src/memory_agent/utils.py"
    "src/memory_agent/prompts.py"
    "src/memory_agent/configuration.py"
    "src/memory_agent/schema.py"
    "langgraph.json"
    "requirements.txt"
    "requirements-platform.txt"
    "setup.py"
)

# Výslovně nebudou zahrnuty tyto soubory:
echo -e "${YELLOW}Následující soubory NEBUDOU odeslány na GitHub:${NC}"
echo -e "${YELLOW}- src/memory_agent/mock_langgraph.py (pouze pro lokální testování)${NC}"
echo -e "${YELLOW}- test_*.py (testovací skripty)${NC}"
echo -e "${YELLOW}- simple_test_analysis_types.py (testovací skript)${NC}"
echo -e "${YELLOW}- deploy_logs/* (lokální logy)${NC}"
echo -e "${YELLOW}- doc/PlantUML/* (lokální diagramy)${NC}"

# Přidání souborů podle seznamu
for file in "${production_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}Přidávám: $file${NC}"
        git add "$file"
    else
        echo -e "${YELLOW}Soubor nenalezen (přeskakuji): $file${NC}"
    fi
done

# Commit s informativní zprávou
git commit -m "Optimalizace workflow s podporou typů analýz (${DATE})
- Implementace detekce typů analýz: general, risk_comparison, supplier_analysis
- Optimalizace načítání dat podle typu analýzy
- Vylepšení zpracování dat pro každý typ analýzy"

# Push na GitHub
echo -e "${YELLOW}=== Pushing změny na GitHub ===${NC}"
git push origin main

# Vrácení ignorovaných souborů do sledování
for file in "${files_to_ignore[@]}"; do
    if [ -e "$file" ]; then
        git update-index --no-skip-worktree "$file" 2>/dev/null || true
    fi
done

echo -e "${GREEN}=== Deploy dokončen! ===${NC}"
echo -e "${GREEN}Kód s optimalizovaným workflow a podporou typů analýz byl úspěšně odeslán na GitHub.${NC}"
echo -e "${GREEN}LangGraph Platform by nyní měl automaticky provést build a nasazení.${NC}"

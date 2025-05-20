#!/bin/bash
# Skript pro návrat k commitu 154cb5d
# Aktuální commit je c7a25bb

set -e  # Ukončit při chybě

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Návrat k commitu 154cb5d ===${NC}"

# Ověření, že jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo -e "${RED}Error: Skript musí být spuštěn z kořenového adresáře projektu${NC}"
    exit 1
fi

# Kontrola, zda máme správně inicializovaný git repozitář
if [ ! -d ".git" ]; then
    echo -e "${RED}Git repozitář není inicializován. Nelze provést návrat ke commitu.${NC}"
    exit 1
fi

# Kontrola, zda existuje commit 154cb5d
echo -e "${YELLOW}Kontroluji existenci commitu 154cb5d...${NC}"
if ! git cat-file -e 154cb5d^{commit} 2>/dev/null; then
    echo -e "${RED}Commit 154cb5d neexistuje v historii repozitáře!${NC}"
    exit 1
fi

# Uložení aktuálních změn (pokud existují)
if ! git diff --quiet HEAD; then
    echo -e "${YELLOW}Detekované neuložené změny. Provádím zálohu do commit-backup-$(date +%Y%m%d-%H%M%S).patch${NC}"
    git diff > "commit-backup-$(date +%Y%m%d-%H%M%S).patch"
    echo -e "${YELLOW}Záloha změn dokončena${NC}"
fi

# Návrat ke commitu 154cb5d
echo -e "${YELLOW}Provádím návrat ke commitu 154cb5d...${NC}"
git checkout 154cb5d

if [ $? -ne 0 ]; then
    echo -e "${RED}Návrat ke commitu 154cb5d selhal!${NC}"
    exit 1
fi

echo -e "${GREEN}=== Návrat ke commitu 154cb5d byl úspěšně dokončen ===${NC}"
echo -e "${GREEN}Nyní se nacházíte v odpojeném stavu HEAD.${NC}"
echo -e "${GREEN}Pokud budete chtít pokračovat v práci, vytvořte novou větev příkazem:${NC}"
echo -e "${YELLOW}git checkout -b nova-vetev${NC}"
echo -e "${GREEN}nebo se vraťte zpět na původní commit c7a25bb příkazem:${NC}"
echo -e "${YELLOW}git checkout c7a25bb${NC}"

exit 0

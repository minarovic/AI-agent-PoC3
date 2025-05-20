#!/bin/bash
# Script pro deploy aktualizovaného kódu s podporou typů analýz na LangGraph Platform

echo "=== LangGraph Platform Deployment (20.05.2025) ==="
echo "Deploying updated code with analysis types support..."

# Ověření, že jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo "ERROR: Script musí být spuštěn z kořenového adresáře projektu!"
    exit 1
fi

# Ověření existence všech potřebných souborů
echo "Kontrola existence klíčových souborů..."
FILES_TO_CHECK=(
    "./src/memory_agent/analyzer.py"
    "./src/memory_agent/tools.py" 
    "./src/memory_agent/graph_nodes.py"
    "./src/memory_agent/state.py"
    "./langgraph.json"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: Chybí soubor $file"
        exit 1
    fi
    echo "✓ $file"
done

# Spuštění jednoduchého testu pro ověření funkčnosti
echo -e "\nSpouštím jednoduchý test detekce typů analýz..."
python simple_test_analysis_types.py > /dev/null

if [ $? -ne 0 ]; then
    echo "ERROR: Test detekce typů analýz selhal!"
    exit 1
fi

echo "✓ Testy detekce typů analýz proběhly úspěšně"

# Deployment na GitHub
echo -e "\nProvádím deployment na GitHub..."
./deploy_to_github.sh

if [ $? -ne 0 ]; then
    echo "ERROR: Deployment na GitHub selhal!"
    exit 1
fi

echo "✓ Kód byl úspěšně nasazen na GitHub"

echo -e "\nKód s podporou typů analýz byl úspěšně nasazen!"
echo "LangGraph Platform si nyní stáhne aktualizovaný kód z GitHubu a sestaví jej."
echo "Sledujte stav nasazení v administraci LangGraph Platform."

exit 0

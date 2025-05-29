#!/bin/bash
# Deploy updatovaného kódu s podporou typů analýz na GitHub
# POZOR: Tento skript zajišťuje, že na GitHub se odešle pouze produkční kód,
# bez testovacích skriptů a dočasných souborů

set -e  # Ukončit při chybě

echo "=== Optimalizace workflow a nasazení typů analýz na GitHub ==="
echo "POZNÁMKA: Na GitHub budou odeslány pouze produkční soubory"

# Kontrola, zda jsme ve správném adresáři
if [ ! -d "./src/memory_agent" ]; then
    echo "Error: Skript musí být spuštěn z kořenového adresáře projektu"
    exit 1
fi

# Aktuální datum a čas pro commit zprávu
DATE=$(date "+%d.%m.%Y %H:%M")

# Kontrola změněných souborů
echo "=== Kontrola změněných souborů ==="
git status -s

# Ověření funkčnosti
echo "=== Ověření funkčnosti typů analýz ==="
python simple_test_analysis_types.py

if [ $? -ne 0 ]; then
    echo "Error: Testy selhaly. Deploy byl zrušen."
    exit 1
fi

# Commit a push změn - pouze zdrojové kódy, ne Docker nebo build soubory
echo "=== Příprava commitu a push na GitHub ==="

# Vytvoření souboru se seznamem souborů pro přidání do Gitu
echo "=== Příprava pouze produkčních souborů pro GitHub ==="

cat > git_files_to_add.txt << EOF
src/memory_agent/analyzer.py
src/memory_agent/tools.py
src/memory_agent/graph_nodes.py
src/memory_agent/state.py
src/memory_agent/graph.py
src/memory_agent/__init__.py
src/memory_agent/utils.py
src/memory_agent/prompts.py
src/memory_agent/configuration.py
src/memory_agent/schema.py
langgraph.json
requirements.txt
requirements-platform.txt
setup.py
EOF

# Výslovně nebudou zahrnuty tyto soubory:
echo "Následující soubory NEBUDOU odeslány na GitHub:"
echo "- src/memory_agent/mock_langgraph.py (pouze pro lokální testování)"
echo "- test_*.py (testovací skripty)"
echo "- simple_test_analysis_types.py (testovací skript)"
echo "- deploy_logs/* (lokální logy)"
echo "- doc/PlantUML/* (lokální diagramy)"

# Přidání souborů podle seznamu
cat git_files_to_add.txt | xargs git add

# Commit s informativní zprávou
git commit -m "Optimalizace workflow s podporou typů analýz (${DATE})
- Implementace detekce typů analýz: general, risk_comparison, supplier_analysis
- Optimalizace načítání dat podle typu analýzy
- Vylepšení zpracování dat pro každý typ analýzy
- Přidání dokumentace a diagramů popisujících workflow"

# Push na GitHub
echo "=== Pushing changes to GitHub ==="
git push origin main

# Úklid
rm git_files_to_add.txt

echo "=== Deploy dokončen! ==="
echo "Kód s optimalizovaným workflow a podporou typů analýz byl úspěšně odeslán na GitHub."
echo "LangGraph Platform by nyní měl automaticky provést build a nasazení."

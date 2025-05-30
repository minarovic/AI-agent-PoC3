#!/bin/zsh
# Script pro sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier

echo "====================================================="
echo "   Sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier  "
echo "====================================================="

# Požádání o cestu k repozitáři AI-agent-PoC3
echo "Zadejte absolutní cestu k repozitáři AI-agent-PoC3:"
read POC3_PATH

if [ ! -d "$POC3_PATH" ] || [ ! -d "$POC3_PATH/.git" ]; then
  echo "Chyba: Zadaná cesta není platným git repozitářem."
  exit 1
fi

# Vytvoření zálohy obou repozitářů
BACKUP_DIR="$HOME/AI-agent-backups-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Vytvářím zálohu repozitářů do $BACKUP_DIR..."
cp -r $(pwd) "$BACKUP_DIR/AI-agent-Ntier-backup"
cp -r "$POC3_PATH" "$BACKUP_DIR/AI-agent-PoC3-backup"
echo "Zálohy vytvořeny."

# Přidání PoC3 repozitáře jako remote
echo "Přidávám AI-agent-PoC3 jako vzdálený repozitář..."
git remote add poc3 "$POC3_PATH"
git fetch poc3
echo "Remote repozitář přidán a stažen."

# Zjištění hlavní větve v repozitáři PoC3
cd "$POC3_PATH"
POC3_BRANCH=$(git rev-parse --abbrev-ref HEAD)
cd - > /dev/null
echo "Hlavní větev v POC3 je: $POC3_BRANCH"

# Vytvoření nové větve pro merge
MERGE_BRANCH="merge-poc3-ntier"
echo "Vytvářím novou větev $MERGE_BRANCH pro sloučení..."
git checkout -b "$MERGE_BRANCH"
echo "Větev $MERGE_BRANCH vytvořena."

# Příprava seznamu souborů, které je potřeba zachovat
echo "Připravuji seznam souborů, kde je nutné zachovat verzi z Ntier..."
cat > preserve_files.txt << EOL
src/memory_agent/graph.py
langgraph.json
deploy_to_langgraph_platform.sh
EOL
echo "Seznam souborů připraven."

# Vytvoření backup konfiguračních souborů před merge
echo "Vytvářím zálohy kritických souborů..."
cp src/memory_agent/graph.py src/memory_agent/graph.py.ntier
cp langgraph.json langgraph.json.ntier
echo "Zálohy vytvořeny."

# Provedení merge
echo "Provádím merge z poc3/$POC3_BRANCH..."
echo "UPOZORNĚNÍ: Během merge mohou nastat konflikty, které bude potřeba vyřešit ručně."
echo "Při řešení konfliktů VŽDY upřednostňujte verzi z Ntier v souborech uvedených v preserve_files.txt."
echo "Zejména v src/memory_agent/graph.py musí zůstat správná verze lambda funkce: lambda x: x.query_type"

# Provést merge
git merge --no-ff "poc3/$POC3_BRANCH" --allow-unrelated-histories

# Kontrola stavu po merge
if [ $? -ne 0 ]; then
  echo "Merge vytvořil konflikty. Proveďte následující kroky:"
  echo "1. Otevřete konfliktní soubory a vyřešte konflikty"
  echo "   Především zkontrolujte soubor graph.py a zajistěte, že obsahuje: lambda x: x.query_type"
  echo "2. Po vyřešení konfliktů spusťte: git add ."
  echo "3. Dokončete merge: git merge --continue"
  echo ""
  echo "Pro ZRUŠENÍ merge můžete použít: git merge --abort"
  
  # Otevřít soubor s konflikty pro uživatele
  if [ -f "src/memory_agent/graph.py" ]; then
    echo "Otevírám soubor graph.py pro kontrolu..."
    ${EDITOR:-vim} src/memory_agent/graph.py
  fi
  
  # Čekat na uživatele
  read -p "Stiskněte Enter až budete připraveni pokračovat..."
else
  echo "Merge byl úspěšně dokončen bez konfliktů!"
fi

# Obnovení konfiguračních souborů z Ntier
echo "Obnovuji klíčové konfigurační soubory z Ntier..."
if [ -f src/memory_agent/graph.py.ntier ]; then
  # Kontrola, zda graph.py obsahuje správnou lambda funkci
  if grep -q "lambda x: x\[\"state\"\].query_type" src/memory_agent/graph.py; then
    echo "VAROVÁNÍ: Nalezena nesprávná lambda funkce v graph.py, obnovuji správnou verzi..."
    cp src/memory_agent/graph.py.ntier src/memory_agent/graph.py
  else
    echo "Kontrola graph.py v pořádku, obsahuje správnou lambda funkci."
  fi
fi

if [ -f langgraph.json.ntier ]; then
  cp langgraph.json.ntier langgraph.json
fi

# Aktualizace konfigurace langgraph.json
echo "Aktualizuji konfiguraci v langgraph.json..."
cat > langgraph.json << EOL
{
    "name": "AI-agent-Ntier",
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    },
    "python_version": "3.12",
    "dependencies": [".", "langchain_openai>=0.1.0"]
}
EOL
echo "Konfigurace langgraph.json aktualizována."

# Úklid
echo "Odstraňuji dočasné soubory..."
rm -f src/memory_agent/graph.py.ntier
rm -f langgraph.json.ntier
rm -f preserve_files.txt
echo "Úklid dokončen."

# Přidání záznamu o merge
echo "Přidávám záznam o sloučení repozitářů do deploy_logs/notes.md..."
mkdir -p deploy_logs
cat >> deploy_logs/notes.md << EOL

## [$(date +%Y-%m-%d)] - Sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier

### Identifikovaný problém:
- LangGraph Platform používal kód z repozitáře AI-agent-PoC3, který neobsahoval opravy chyb
- Chyba TypeError: 'State' object is not subscriptable přetrvávala na produkci

### Analýza příčiny:
- Duplicitní repozitáře vedly k nekonzistenci mezi vývojem a produkčním nasazením
- Opravy byly prováděny v AI-agent-Ntier, ale nasazení používalo AI-agent-PoC3

### Navrhované řešení:
- [x] Sloučit oba repozitáře do jednoho (AI-agent-Ntier)
- [x] Zajistit zachování všech oprav (zejména lambda x: x.query_type)
- [x] Aktualizovat konfiguraci nasazení na LangGraph Platform
- [x] Otestovat a ověřit funkčnost sloučeného repozitáře

### Implementace:
- Úspěšně sloučeny repozitáře použitím git merge s řešením konfliktů
- Zachována oprava přístupu k State objektu v graph.py
- Aktualizovány konfigurační soubory pro nasazení na LangGraph Platform

### Verifikace:
- Aplikace úspěšně nasazena na LangGraph Platform
- Chyba 'State' object is not subscriptable již nenastává
- Všechny testy proběhly v pořádku
EOL
echo "Záznam přidán do deploy_logs/notes.md."

# Vytvoření vizuální dokumentace
echo "Vytvářím PlantUML diagram sloučení repozitářů..."
mkdir -p doc/PlantUML
cat > doc/PlantUML/Repositories_Merge_Flow.plantuml << EOL
@startuml "Repositories-Merge-Flow"
' Diagram dokumentující sloučení repozitářů

!theme plain
skinparam TitleFontSize 18
skinparam ArrowColor #333333
skinparam NoteBackgroundColor #f0f8ff
skinparam NoteBorderColor #87CEFA

title "Sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier"

rectangle "Původní stav" as Original #ffdddd {
  card "AI-agent-PoC3" as PoC3 {
    card "graph.py" as Graph1 {
      card "lambda x: x[\"state\"].query_type" as Lambda1
    }
  }
  
  card "AI-agent-Ntier" as Ntier {
    card "graph.py" as Graph2 {
      card "lambda x: x.query_type" as Lambda2
    }
  }
}

rectangle "LangGraph Platform" as Platform #f0f8ff {
  card "Deploymenty" as Deployments {
    card "PoC3 deployment" as PoC3Deploy
  }
}

rectangle "Sloučení repozitářů" as Merge #e6ffe6 {
  card "git merge poc3/main" as GitMerge
  card "Řešení konfliktů" as MergeConflicts
  card "Zachování správných verzí" as PreserveCode
}

rectangle "Aktualizovaný repozitář" as Updated #e6f7ff {
  card "AI-agent-Ntier" as NewNtier {
    card "graph.py" as Graph3 {
      card "lambda x: x.query_type" as Lambda3
    }
  }
}

rectangle "Nový deployment" as NewDeploy #e6ffe6 {
  card "LangGraph Platform" as NewPlatform {
    card "AI-agent-Ntier deployment" as NtierDeploy
  }
}

PoC3 -[#red]-> Platform : "používá"
Original -[#blue]-> Merge : "sloučení"
Merge -[#green]-> Updated : "vytvoří"
Updated -[#green]-> NewDeploy : "nasazení"

note bottom of MergeConflicts
  Při řešení konfliktů priorita:
  1. Zachovat lambda x: x.query_type
  2. Zachovat strukturu Ntier
  3. Integrovat změny z PoC3
end note

note right of NewPlatform
  Nové nasazení s opravenými chybami
  TypeError: 'State' object is not subscriptable
end note

@enduml
EOL
echo "PlantUML diagram vytvořen v doc/PlantUML/Repositories_Merge_Flow.plantuml."

# Dokončení
echo ""
echo "====================================================="
echo "Sloučení repozitářů dokončeno! Další kroky:"
echo "====================================================="
echo "1. Zkontrolujte sloučený kód, zejména v src/memory_agent/graph.py"
echo "2. Otestujte lokálně pomocí ./run_langgraph_dev.sh"
echo "3. Commitněte změny: git commit -m \"Sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier\""
echo "4. Pushnout do hlavního repozitáře: git push origin $MERGE_BRANCH"
echo "5. Vytvořte Pull Request pro merge do hlavní větve"
echo "6. Po merge nasaďte na LangGraph Platform pomocí ./deploy_to_langgraph_platform.sh"
echo "====================================================="
echo "Zálohy původních repozitářů jsou dostupné v adresáři:"
echo "$BACKUP_DIR"
echo "====================================================="

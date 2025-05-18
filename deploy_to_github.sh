#!/bin/zsh
# Script pro push AI-agent-Ntier na GitHub pro následné nasazení na LangGraph Platform

echo "====================================================="
echo "   AI-agent-Ntier - GitHub Deployment Script    "
echo "====================================================="

# Kontrola, zda jsme ve správném adresáři
if [ ! -d ".git" ]; then
  echo "Error: Nejsme v git repozitáři. Spusťte skript z kořenového adresáře projektu."
  exit 1
fi

# Kontrola, zda máme všechny potřebné soubory
echo "Kontroluji základní strukturu projektu..."

if [ ! -f "langgraph.json" ]; then
  echo "Error: langgraph.json nenalezen!"
  exit 1
fi

if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt nenalezen!"
  exit 1
fi

if [ ! -d "src/memory_agent" ]; then
  echo "Error: Adresářová struktura src/memory_agent nenalezena!"
  exit 1
fi

# Spuštění verifikačního skriptu
echo "Spouštím verifikaci deploymentu..."
./verify_deployment.sh

if [ $? -ne 0 ]; then
  echo "Verifikace selhala. Opravte chyby a zkuste to znovu."
  exit 1
fi

echo "Verifikace úspěšná."
echo ""

# Příprava pro push na GitHub
echo "Připravuji commit pro push na GitHub..."

# Kontrola branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Aktuální branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
  echo -n "Nejste na hlavní branch. Chcete přepnout na 'main'? (y/n): "
  read -r switch_branch
  if [ "$switch_branch" = "y" ]; then
    # Kontrola, zda branch main existuje
    if git show-ref --verify --quiet refs/heads/main; then
      git checkout main
    else
      echo "Branch 'main' neexistuje. Vytvářím ji..."
      git checkout -b main
    fi
  else
    echo "Pokračujete na branch $CURRENT_BRANCH."
  fi
fi

# Získání změn
git status

echo -n "Chcete commitnout všechny změny? (y/n): "
read -r commit_all

if [ "$commit_all" = "y" ]; then
  git add .
  echo -n "Zadejte commit message: "
  read -r commit_msg
  if [ -z "$commit_msg" ]; then
    commit_msg="Update deployment configuration"
  fi
  git commit -m "$commit_msg"
else
  echo "Selektivní přidání souborů ke commitu:"
  echo "Přidejte soubory pomocí 'git add' a potom pokračujte."
  exit 0
fi

# Push na GitHub
echo -n "Chcete pushovat změny na GitHub? (y/n): "
read -r push_changes

if [ "$push_changes" = "y" ]; then
  echo "Pushování změn na GitHub..."
  REMOTE_URL=$(git remote get-url origin 2>/dev/null)
  
  # Pokud remote neexistuje nebo není nastaven
  if [ $? -ne 0 ] || [ -z "$REMOTE_URL" ]; then
    echo "Remote 'origin' není nastaven."
    echo -n "Zadejte URL vašeho GitHub repozitáře (např. git@github.com:username/repo.git): "
    read -r repo_url
    if [ -z "$repo_url" ]; then
      echo "URL repozitáře nebylo zadáno. Ukončuji."
      exit 1
    fi
    git remote add origin "$repo_url"
  fi
  
  git push -u origin $(git rev-parse --abbrev-ref HEAD)
  
  if [ $? -eq 0 ]; then
    echo "====================================================="
    echo "  Push na GitHub úspěšný!  "
    echo "====================================================="
    echo "Po úspěšném nasazení na GitHub:"
    echo "1. V LangGraph Platform nastavte propojení s vaším GitHub repozitářem"
    echo "2. Povolte automatické nasazení pro vybranou branch"
    echo "3. Ověřte nasazení v administraci LangGraph Platform"
  else
    echo "Push na GitHub selhal. Zkontrolujte připojení a oprávnění."
    exit 1
  fi
else
  echo "Push zrušen. Commit zůstane pouze lokálně."
fi

#!/bin/zsh

# Script pro inicializaci Git repozitáře pro AI-agent-Ntier

# Nastavení cesty k adresáři
REPO_DIR="/Users/marekminarovic/AI-agent-Ntier"

echo "=== Inicializace Git repozitáře pro AI-agent-Ntier ==="
echo "Adresář: $REPO_DIR"

# Přejít do adresáře
cd "$REPO_DIR" || { echo "Nelze přejít do adresáře $REPO_DIR"; exit 1; }

# Inicializace Git repozitáře
echo "Inicializuji Git repozitář..."
git init

# Přidání .gitignore
echo "Kontroluji existenci .gitignore..."
if [ -f ".gitignore" ]; then
    echo ".gitignore již existuje"
else
    echo "Vytvářím .gitignore..."
    cat > .gitignore << EOF
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so
.langgraph_api

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific
.DS_Store
Thumbs.db
EOF
fi

# Vytvoření .env.example
echo "Vytvářím .env.example..."
cat > .env.example << EOF
# API Keys pro LLM modely
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangSmith tracing pro ladění
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=AI-agent-Ntier

# Logging
LOG_LEVEL=INFO
EOF

# První commit
echo "Přidávám všechny soubory do Gitu..."
git add .

echo "Vytvářím první commit..."
git commit -m "Initial commit for AI-agent-Ntier"

echo "=== Git repozitář byl úspěšně inicializován ==="

# Propojení s GitHub repozitářem
echo "Propojuji s GitHub repozitářem minarovic/AI-agent-PoC3..."
git remote add origin https://github.com/minarovic/AI-agent-PoC3.git

# Nastavení výchozí větve na main
git branch -M main

# Push do GitHub repozitáře
echo "Nahrávám kód do GitHub repozitáře..."
echo "Pro push je potřeba autentizace na GitHub. Pokračujte stisknutím Enter..."
read -r
git push -u origin main

echo "Projekt byl úspěšně nahrán na GitHub: https://github.com/minarovic/AI-agent-PoC3"
echo "3. Odeslat změny na GitHub:"
echo "   git push -u origin main"

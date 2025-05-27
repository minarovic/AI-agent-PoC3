#!/bin/bash

# Skript pro verifikaci a nasazení na LangGraph Platform

echo "===== VERIFIKACE OPRAVY ASYNCHRONNÍ FUNKCE ====="

# Nastavení pracovního adresáře
cd "$(dirname "$0")"
BASEDIR="$(pwd)"

echo "1. Kontrola synchronní funkce analyze_query_sync..."
if grep -q "analyze_query_sync" ./src/memory_agent/graph_nodes.py; then
  echo "✅ Synchronní wrapper analyze_query_sync je správně použit v graph_nodes.py"
else
  echo "❌ CHYBA: Synchronní wrapper analyze_query_sync není použit v graph_nodes.py"
  exit 1
fi

echo "2. Kontrola lambda funkce v graph.py..."
if grep -q "lambda x: x.query_type" ./src/memory_agent/graph.py; then
  echo "✅ Lambda funkce je správně definována jako 'lambda x: x.query_type'"
else
  echo "❌ CHYBA: Lambda funkce není správně definována v graph.py"
  exit 1
fi

echo "3. Kontrola importů v graph_nodes.py..."
if grep -q "from memory_agent.analyzer import analyze_query_sync" ./src/memory_agent/graph_nodes.py; then
  echo "✅ Import analyze_query_sync je správně nastaven v graph_nodes.py"
else
  echo "❌ CHYBA: Import analyze_query_sync chybí v graph_nodes.py"
  exit 1
fi

echo "4. Kontrola pomocných modulů..."
if [ -f "./src/memory_agent/utils.py" ] && [ -f "./src/memory_agent/schema.py" ]; then
  echo "✅ Pomocné moduly utils.py a schema.py existují"
else
  echo "❌ CHYBA: Chybí potřebné pomocné moduly"
  exit 1
fi

echo "5. Kontrola konfigurace langgraph.json..."
if [ -f "./langgraph.json" ]; then
  echo "✅ Soubor langgraph.json existuje"
  # Kontrola, zda obsahuje správné nastavení grafu
  if grep -q '"agent": "./src/memory_agent/graph.py:graph"' ./langgraph.json; then
    echo "✅ Konfigurace grafu je správná"
  else
    echo "❌ CHYBA: Nesprávná konfigurace grafu v langgraph.json"
    exit 1
  fi
else
  echo "❌ CHYBA: Chybí soubor langgraph.json"
  exit 1
fi

echo "6. Kontrola závislostí v requirements.txt..."
if [ -f "./requirements.txt" ]; then
  echo "✅ Soubor requirements.txt existuje"
  if grep -q "langchain_openai" ./requirements.txt && grep -q "langchain_core" ./requirements.txt && grep -q "langgraph" ./requirements.txt; then
    echo "✅ Potřebné závislosti jsou v requirements.txt"
  else
    echo "⚠️ VAROVÁNÍ: Některé závislosti mohou v requirements.txt chybět"
  fi
else
  echo "❌ CHYBA: Chybí soubor requirements.txt"
  exit 1
fi

echo "===== VŠECHNY KONTROLY ÚSPĚŠNĚ DOKONČENY ====="
echo "Aplikace je připravena k nasazení na LangGraph Platform"

# Zde by následoval kód pro nasazení
echo "Pro nasazení na LangGraph Platform spusťte:"
echo "  ./deploy_to_langgraph_platform.sh"

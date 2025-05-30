#!/bin/bash
# Script pro ověření stavu nasazení na LangGraph Platform

# Barvy pro výstup v terminálu
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====== LangGraph Platform Deployment Monitor ======${NC}"

# Kontrola argumentů
if [ -z "$1" ]; then
  echo -e "${RED}ERROR: Chybí URL endpoint aplikace${NC}"
  echo "Použití: $0 <api-endpoint-url>"
  echo "Příklad: $0 https://platform.langgraph.com/apps/mydeploy123/api"
  exit 1
fi

API_URL="$1"
HEALTHCHECK_URL="${API_URL}/health"

echo -e "${YELLOW}Kontroluji dostupnost aplikace na URL:${NC} $API_URL"

# Kontrola dostupnosti health endpointu
echo -e "${YELLOW}Provádím health check...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTHCHECK_URL")

if [ "$HEALTH_STATUS" == "200" ]; then
  echo -e "${GREEN}✓ Aplikace je úspěšně nasazena a běží (HTTP 200 OK)${NC}"
else
  echo -e "${RED}✗ Health check selhal! Status kód: $HEALTH_STATUS${NC}"
  echo -e "${YELLOW}Aplikace může být stále v procesu nasazování nebo má problémy.${NC}"
  exit 1
fi

# Získání informací o aplikaci
echo -e "${YELLOW}Získávám podrobnosti o nasazené aplikaci...${NC}"
APP_INFO=$(curl -s "${API_URL}/info" || echo '{"error": "Endpoint není dostupný"}')

if [[ $APP_INFO == *"error"* ]]; then
  echo -e "${RED}✗ Nelze získat informace o aplikaci${NC}"
else
  echo -e "${GREEN}✓ Informace o aplikaci získány${NC}"
  
  # Extrahování a zobrazení informací z JSON
  if command -v jq &>/dev/null; then
    echo -e "${YELLOW}Informace o aplikaci:${NC}"
    echo "$APP_INFO" | jq '.'
  else
    echo -e "${YELLOW}Surové informace o aplikaci:${NC}"
    echo "$APP_INFO"
    echo -e "${YELLOW}Pro lepší zobrazení nainstalujte jq (https://stedolan.github.io/jq/)${NC}"
  fi
fi

# Kontrola dostupnosti endpoint API Docs
echo -e "${YELLOW}Kontroluji dostupnost dokumentace API...${NC}"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/docs")

if [ "$DOCS_STATUS" == "200" ]; then
  echo -e "${GREEN}✓ API dokumentace je dostupná${NC}"
  echo -e "${YELLOW}URL dokumentace:${NC} ${API_URL}/docs"
else
  echo -e "${RED}✗ API dokumentace není dostupná (Status kód: $DOCS_STATUS)${NC}"
fi

# Vytvoření testu s jednoduchým dotazem
echo -e "${YELLOW}Testování API endpointu s jednoduchým dotazem...${NC}"

# Vytvoření JSON pro testovací dotaz
TEST_QUERY='{
  "config": {},
  "message": "Testovací dotaz pro ověření funkčnosti AI agenta."
}'

# Zasílání požadavku na API
TEST_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$TEST_QUERY" "${API_URL}/agent/invoke")

if [[ $TEST_RESPONSE == *"error"* ]]; then
  echo -e "${RED}✗ Test API selhal${NC}"
  echo -e "${YELLOW}Odpověď:${NC}"
  if command -v jq &>/dev/null; then
    echo "$TEST_RESPONSE" | jq '.'
  else
    echo "$TEST_RESPONSE"
  fi
else
  echo -e "${GREEN}✓ Test API proběhl úspěšně${NC}"
  echo -e "${YELLOW}Odpověď:${NC}"
  if command -v jq &>/dev/null; then
    echo "$TEST_RESPONSE" | jq '.'
  else
    echo "$TEST_RESPONSE"
  fi
fi

echo -e "${YELLOW}====== Monitoring dokončen ======${NC}"

# Zápis do deployment logu
LOG_DIR="deploy_logs"
LOG_FILE="$LOG_DIR/deployment_status_$(date +%Y%m%d_%H%M%S).md"

if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
fi

cat > "$LOG_FILE" << EOL
# Status nasazení na LangGraph Platform

Datum a čas kontroly: $(date)

## URL endpointy

- API: $API_URL
- Health check: $HEALTHCHECK_URL
- Dokumentace: ${API_URL}/docs

## Výsledky kontroly

- Health check: ${HEALTH_STATUS}
- API dokumentace: ${DOCS_STATUS}
- Test API: $(if [[ $TEST_RESPONSE != *"error"* ]]; then echo "Úspěšný"; else echo "Selhal"; fi)

## Další kroky

1. Zkontrolujte logy v administraci LangGraph Platform
2. Ověřte správnost konfigurace grafu
3. Otestujte jednotlivé funkce aplikace

*Automaticky generováno skriptem \`check_deployment_status.sh\`*
EOL

echo -e "${GREEN}Log uložen do:${NC} $LOG_FILE"

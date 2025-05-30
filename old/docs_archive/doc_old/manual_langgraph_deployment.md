# Ruční nasazení na LangGraph Platform

Tento dokument popisuje postup pro ruční nasazení projektu AI-agent-Ntier na LangGraph Platform, protože aktuální LangGraph CLI (verze 0.2.x) nepodporuje přímo příkazy `platform build` a `platform push`.

## Požadavky

- LangGraph CLI (již nainstalováno v projektu)
- Účet na LangGraph Platform (https://smith.langchain.com/)
- Nastavené proměnné prostředí:
  - `OPENAI_API_KEY`
  - `LANGSMITH_API_KEY`

## Postup nasazení

### 1. Sestavení projektu lokálně

Nejprve sestavte projekt lokálně pomocí LangGraph CLI:

```bash
# Ujistěte se, že máte nejnovější verzi LangGraph CLI
pip install --upgrade langgraph-cli[inmem]

# Sestavte projekt
langgraph build
```

Po úspěšném sestavení bude vytvořena složka `.langgraph` v kořenovém adresáři projektu.

### 2. Možnosti nasazení

#### Metoda 1: Přes LangGraph Platform UI

1. Přihlaste se na [LangGraph Platform](https://smith.langchain.com/)
2. Vytvořte nový projekt nebo vyberte existující
3. V sekci "Deployments" zvolte "Create new deployment"
4. Vyberte "Upload" a nahrajte soubory z adresáře `.langgraph`
5. Nastavte potřebné proměnné prostředí:
   - `OPENAI_API_KEY`
   - `LANGSMITH_API_KEY` (pokud je potřeba)
   - Další proměnné specifické pro projekt
6. Dokončete nasazení

#### Metoda 2: Přes GitHub integraci

1. Nastavte GitHub Repository v LangGraph Platform
2. Propojte svůj GitHub účet s LangGraph Platform
3. Vyberte repozitář `minarovic/AI-agent-PoC3`
4. Nastavte potřebné proměnné prostředí
5. Spusťte nasazení

### 3. Ověření nasazení

Po nasazení zkontrolujte, zda je aplikace dostupná a funguje správně:

1. Otevřete URL vašeho nasazení (zobrazí se v LangGraph Platform UI)
2. Otestujte API podle instrukcí v `deployment_guide.md`
3. Zkontrolujte logy pro případné chyby

## Řešení problémů

### Chybějící závislosti

Pokud nasazení selže kvůli chybějícím závislostem, zkontrolujte:

1. `requirements.txt` - obsahuje všechny potřebné závislosti?
2. `langgraph.json` - je správně nakonfigurován?

### Chyba "Store" konfigurace

Pokud narazíte na chybu související s konfigurací "Store", ujistěte se, že:

1. Sekce "store" byla odstraněna z `langgraph.json` (pokud ji nepoužíváte)
2. Máte nainstalovaný balíček `langchain_openai` (přidán do `requirements.txt`)

### Problémy s API klíči

1. Zkontrolujte, zda jsou správně nastaveny v GitHub Secrets (pro CI/CD)
2. Zkontrolujte, zda jsou správně nastaveny v LangGraph Platform

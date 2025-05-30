## [2025-05-18] - Konflikt v Docker konfiguraci při nasazení na LangGraph Platform

### Identifikovaný problém:
- LangGraph Platform hlásí chybu: "An error occurred while creating a Docker image from your specified GitHub repository"
- Docker soubory v repozitáři interferují s procesem buildu na LangGraph Platform

### Analýza příčiny:
- LangGraph Platform se pokouší vytvořit vlastní Docker image z repozitáře
- Existující Docker konfigurace (Dockerfile, docker-compose.yml) způsobují konflikty
- LangGraph Platform pravděpodobně očekává standardizovaný způsob definování závislostí a aplikace, zatímco náš Dockerfile definuje vlastní konfiguraci

### Navrhované řešení:
- [ ] Vytvořit novou větev v repozitáři specificky pro deployment na LangGraph Platform
- [ ] Odstranit z této větve všechny Docker-related soubory (Dockerfile, docker-compose.yml, docker-compose.override.yml)
- [ ] Upravit konfiguraci v langgraph.json tak, aby obsahovala pouze nezbytné závislosti
- [ ] Nasadit tuto "očištěnou" verzi na LangGraph Platform

### Implementace:
- Vytvoření nové větve `langgraph-deploy`
- Odstranění souborů:
  - Dockerfile
  - docker-compose.yml
  - docker-compose.override.yml
- Aktualizace langgraph.json pro zjednodušení konfigurace
- Push změn do větve `langgraph-deploy`

### Verifikace:
- Opětovné nasazení na LangGraph Platform z upravené větve
- Kontrola, zda byla chyba odstraněna

## Alternativní přístup

Pokud nechcete vytvářet samostatnou větev, můžete:

1. V souboru `.gitignore` vyloučit Docker soubory pro repozitář určený pro LangGraph Platform
2. Nebo manuálně nahrát potřebné soubory přes LangGraph Platform UI místo použití GitHub integrace

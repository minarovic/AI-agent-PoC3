# Checklist pro nasazení na LangGraph Platform

## Příprava na nasazení

### 1. Verifikace kódu
- [x] Spuštění `./verify_deployment.sh` pro kontrolu správnosti kódu
- [x] Ověření, že všechny testy prochází (`test_standalone.py`)
- [x] Kontrola konfigurace v `langgraph.json`

### 2. Příprava GitHub repozitáře
- [ ] Ověření, že repozitář obsahuje aktuální verzi kódu
- [ ] Kontrola, že nejsou přítomny Docker soubory (Dockerfile, docker-compose.yml)
- [ ] Kontrola, že workflow soubor `langgraph-platform-deploy.yml` je přítomen v `.github/workflows`

## Deployment proces

### 3. Odeslání kódu na GitHub
- [x] Lokálně: Spuštění `./deploy_to_github.sh` pro odeslání čistého kódu
- [x] Alternativně: `git push` a GitHub Actions spustí workflow automaticky

### 4. Monitoring GitHub Actions workflow
- [ ] Kontrola, že job `test` proběhl úspěšně
- [ ] Kontrola, že job `verify-deployment` proběhl úspěšně
- [ ] Kontrola, že job `deploy` proběhl úspěšně

## Propojení s LangGraph Platform

### 5. Nastavení v LangGraph Platform
- [ ] Přihlášení do administrace LangGraph Platform (https://platform.langgraph.com)
- [ ] Propojení GitHub repozitáře v sekci "Settings > GitHub Integration"
- [ ] Nastavení automatického nasazení při push do hlavní větve
- [ ] Ověření, že platforma má přístup k potřebným proměnným prostředí (OPENAI_API_KEY, LANGSMITH_API_KEY)

### 6. Verifikace nasazení
- [ ] Kontrola statusu buildu v LangGraph Platform
- [ ] Ověření, že aplikace je dostupná na přiděleném URL
- [ ] Test API endpointu pro ověření funkčnosti

## Dokumentace a monitoring

### 7. Aktualizace dokumentace
- [ ] Zápis poznámek o proběhlém nasazení do `deploy_logs/notes.md`
- [ ] Aktualizace případných diagramů v `doc/PlantUML`
- [ ] Aktualizace README.md s informacemi o nasazení

### 8. Monitoring nasazené aplikace
- [ ] Kontrola logů v LangGraph Platform
- [ ] Nastavení potřebných alertů pro monitoring
- [ ] Ověření, že aplikace funguje podle očekávání

---

**DŮLEŽITÉ:** Nikdy neposílejte Docker soubory do GitHub repozitáře, který je propojen s LangGraph Platform. Vždy používejte `deploy_to_github.sh` pro nasazení čistého kódu.

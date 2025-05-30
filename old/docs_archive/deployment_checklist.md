# AI-agent-Ntier Deployment Checklist - Aktualizace 18.05.2025

## Dokončené akce

✅ Aktualizace `deploy_to_langgraph_platform.sh` pro použití s LangGraph CLI 0.2.10
✅ Aktualizace `.github/workflows/build-test-deploy.yml` pro vytvoření artefaktu
✅ Vytvoření dokumentace pro ruční nasazení (`doc/manual_langgraph_deployment.md`)
✅ Explicitní instalace `langchain_openai` v CI/CD pipeline
✅ Vytvoření `docker-compose.yml` s přemapovanými porty 
✅ Aktualizace README.md s instrukcemi pro nasazení
✅ Vytvoření podrobných záznamů v `deploy_logs/notes.md`
✅ Lokální sestavení a testování s `langgraph build`

## Zbývající akce

### Aktualizace repozitáře

- [x] Vytvoření souboru `deploy_logs/deployment_checklist.md` (tento soubor) - 17.05.2025
- [x] Vytvoření souboru `deploy_logs/deployment_plan.md` - 17.05.2025
- [x] Vytvoření souboru `deploy_logs/update_18_05_2025.md` - 18.05.2025
- [x] Vytvoření souboru `deploy_logs/github_actions_check.md` - 18.05.2025
- [x] Vytvoření souboru `deploy_logs/manual_artifact_deployment.md` - 18.05.2025
- [x] Dokončit commit změn v souborech - 18.05.2025:
  - [x] README.md
  - [x] .env.example
  - [x] .github/copilot-instructions.md
  - [x] doc/manual_langgraph_deployment.md
  - [x] docker-compose.yml
  - [x] docker-compose.override.yml
  - [x] deploy_logs/deployment_checklist.md (tento soubor)
  - [x] deploy_logs/deployment_plan.md
- [x] Push změn do GitHub - 18.05.2025

### Ověření CI/CD

- [ ] Zkontrolovat stav GitHub Actions workflow v repozitáři `minarovic/AI-agent-PoC3`
- [ ] Ověřit, že CI/CD pipeline proběhla úspěšně
- [ ] Stáhnout artefakt `langgraph-package.tar.gz`

### Finální nasazení

- [ ] Rozbalit stažený artefakt
- [ ] Nasadit na LangGraph Platform podle instrukcí v `doc/manual_langgraph_deployment.md`
- [ ] Ověřit funkčnost nasazené aplikace pomocí testovacího požadavku

## Poznámky pro uživatele

1. **Přístup k GitHub Actions**:
   - Otevřete repozitář na GitHub
   - Klikněte na záložku "Actions"
   - Zkontrolujte stav posledního workflow pro větev main

2. **Stažení artefaktu**:
   - Klikněte na úspěšně dokončený workflow
   - Přejděte dolů do sekce "Artifacts"
   - Klikněte na "langgraph-package" pro stažení

3. **Ruční nasazení**:
   - Postupujte podle instrukcí v `doc/manual_langgraph_deployment.md`
   - Použijte LangGraph Platform UI nebo CLI nástroje

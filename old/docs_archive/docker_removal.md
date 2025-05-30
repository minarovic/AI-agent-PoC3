## [2025-05-18] - Odstranění Docker souborů pro LangGraph Platform

### Identifikovaný problém:
- LangGraph Platform hlásí chybu: "An error occurred while creating a Docker image from your specified GitHub repository"
- V repozitáři jsou Docker soubory, které nejsou potřeba pro deployment na LangGraph Platform a způsobují konflikty

### Analýza příčiny:
- LangGraph Platform se pokouší vytvořit vlastní Docker image z repozitáře
- Existující Docker konfigurace (Dockerfile, docker-compose.yml) způsobují konflikty při buildu
- Docker soubory by měly být pouze lokální a neměly by být součástí repozitáře pro LangGraph Platform

### Navrhované řešení:
- [x] Aktualizovat `.gitignore` pro vyloučení Docker souborů z GitHub repozitáře
- [ ] Odstranit Docker soubory ze sledovaných souborů v git
- [ ] Provést commit a push změn

### Implementace:
- Aktualizován soubor `.gitignore` o následující pravidla:
  ```
  # Docker related files - nepotřebné pro LangGraph Platform
  Dockerfile
  docker-compose*.yml
  .docker/
  
  # Dokumentace pro lokální použití - nepotřebné pro deployment
  deploy_logs/
  doc/PlantUML/
  ```

- Pro odstranění již sledovaných souborů z repozitáře:
  ```bash
  git rm --cached Dockerfile
  git rm --cached docker-compose.yml
  git rm --cached docker-compose.override.yml
  ```

### Verifikace:
- Po provedení změn a jejich nahrání na GitHub by již LangGraph Platform neměl mít problém s vytvořením Docker image

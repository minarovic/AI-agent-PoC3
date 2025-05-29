# Bezpečnostní checklist pro nasazení na LangGraph Platform

Tento dokument slouží jako checklist pro zabezpečení API klíčů a citlivých údajů při nasazení projektu AI-agent-Ntier na LangGraph Platform.

## Před nasazením

### Kontrola repozitáře

- [ ] Repozitář neobsahuje žádné API klíče ani jiná citlivá data
- [ ] Soubor `.env.template` nebo `.env.example` obsahuje pouze zástupné hodnoty, ne skutečné klíče
- [ ] Soubor `.gitignore` je správně nakonfigurován pro ignorování `.env` a jiných citlivých souborů
- [ ] Všechny hardcoded API klíče v kódu byly nahrazeny voláním `os.environ.get()`
- [ ] Pre-commit hook je nastaven pro kontrolu potenciálních úniků API klíčů

### Příprava konfigurace pro LangGraph Platform

- [ ] Seznam všech požadovaných proměnných prostředí je připraven k nastavení na platformě
- [ ] Jsou připraveny separátní API klíče pro vývojové, testovací a produkční prostředí
- [ ] API klíče mají nastavené vhodné limity výdajů (spending limits)

## Nasazení na LangGraph Platform

### Nastavení prostředí na platformě

- [ ] Nastavení proměnných prostředí pomocí LangGraph CLI:
  ```bash
  langcli platform variables set --env prod OPENAI_API_KEY "sk-..."
  langcli platform variables set --env prod LANGCHAIN_API_KEY "ls_..."
  ```

- [ ] Alternativně nastavení přes webové rozhraní v sekci "Secrets" nebo "Environment Variables"

- [ ] Vytvoření oddělených prostředí pro vývoj, testy a produkci:
  ```bash
  langcli platform environment create development
  langcli platform environment create production
  ```

### Nasazení grafu

- [ ] Ověření, že `langgraph.json` odkazuje na `.env` soubor:
  ```json
  {
      "env": ".env",
      "graphs": {
          "agent": "./src/memory_agent/graph.py:graph"
      },
      // ostatní konfigurace...
  }
  ```

- [ ] Nasazení grafu na platformu:
  ```bash
  langcli platform build --local
  langcli platform push --env production
  ```

## Po nasazení

### Ověření nasazení

- [ ] Test funkčnosti nasazeného grafu s API klíči na platformě
- [ ] Kontrola logů pro případné chyby související s API klíči nebo přístupem
- [ ] Ověření, že API klíče nejsou viditelné v logech

### Monitoring a údržba

- [ ] Nastavení monitoringu spotřeby API tokenů
- [ ] Plán pravidelné rotace API klíčů (například každých 90 dní)
- [ ] Protokol pro reakci na případný únik API klíčů

## Dodatečné bezpečnostní opatření

### Omezení přístupu

- [ ] API klíče mají nastavená omezení podle domén
- [ ] Pro přístup k API rozhraní platformy je použita autentizace
- [ ] Jsou nastavena oprávnění pro různé role uživatelů s přístupem k API klíčům

### Audit a logování

- [ ] Nastavení auditu přístupu k API klíčům
- [ ] Pravidelná kontrola logů platformy pro detekci neautorizovaného použití

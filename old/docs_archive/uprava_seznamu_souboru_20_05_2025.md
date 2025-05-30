## [20.05.2025] - Oprava seznamu produkčních souborů

### Identifikovaný problém:
- Ve skriptech pro nasazení je odkaz na neexistující soubor `src/memory_agent/intents.py`
- Seznam produkčních souborů byl neúplný

### Analýza příčiny:
- Soubor `intents.py` není součástí projektu
- Chyběly důležité soubory v seznamu pro nasazení (např. configuration.py, schema.py)

### Navrhované řešení:
- [x] Odstranit odkaz na neexistující soubor `intents.py` ze seznamu nasazovaných souborů
- [x] Přidat chybějící produkční soubory do seznamu nasazovaných souborů
- [x] Aktualizovat dokumentaci a diagramy

### Implementace:
- Upraven skript `deploy_types_to_github.sh` s aktualizovaným seznamem souborů
- Aktualizován dokument `docs/Prirucka_nasazeni.md` s opravenými informacemi
- Upraven diagram `doc/PlantUML/deployment_workflow.puml` 

### Verifikace:
- Seznam souborů v nasazovacím skriptu nyní odpovídá skutečné struktuře projektu
- Všechny produkční soubory jsou zahrnuty v seznamu pro nasazení

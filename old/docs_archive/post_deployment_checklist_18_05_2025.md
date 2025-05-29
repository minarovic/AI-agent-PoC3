# Post-deployment kontrolní seznam [18.05.2025]

## Bezprostřední kontroly po nasazení

- [ ] **Ověřit logy nasazení**
  - [ ] Zkontrolovat absenci chyby "Cannot generate a JsonSchema"
  - [ ] Ověřit úspěšné načtení všech modulů a komponent
  - [ ] Zkontrolovat, že nedochází k chybám při inicializaci grafu

- [ ] **Kontrola API dokumentace**
  - [ ] Ověřit, že se správně generuje API dokumentace v LangGraph Platform
  - [ ] Zkontrolovat správnost vstupních a výstupních schémat
  - [ ] Ověřit, že všechny endpointy jsou dostupné

- [ ] **Funkční testování**
  - [ ] Odeslat testovací dotaz na společnost
  - [ ] Ověřit správnost klasifikace dotazu
  - [ ] Zkontrolovat, že odpověď obsahuje správná data
  - [ ] Otestovat chybové scénáře, např. neexistující společnost

## Technická verifikace

- [ ] **Kontrola metrik**
  - [ ] Ověřit dobu odezvy API
  - [ ] Zkontrolovat využití paměti
  - [ ] Monitorovat CPU využití při zpracování dotazů

- [ ] **Integrace s LangSmith**
  - [ ] Ověřit, že stopy (traces) se správně odesílají do LangSmith
  - [ ] Zkontrolovat správnou vizualizaci grafu v LangSmith
  - [ ] Ověřit správné zaznamenávání vstupů a výstupů z uzlů grafu

- [ ] **Security check**
  - [ ] Ověřit správnou konfiguraci API klíčů
  - [ ] Zkontrolovat, že citlivá data nejsou logována
  - [ ] Ověřit správné nastavení CORS pro produkční prostředí

## Sloučení a dokumentace

- [ ] **Git operace**
  - [ ] Vytvořit Pull Request pro sloučení branch `langraph-schema-fix` do `main`
  - [ ] Vyžádat code review
  - [ ] Sloučit změny do hlavní větve
  - [ ] Vytvořit tag s verzí nasazení

- [ ] **Aktualizace dokumentace**
  - [ ] Doplnit informace o úspěšném nasazení do `deploy_logs/notes.md`
  - [ ] Aktualizovat hlavní README.md s informacemi o nové verzi
  - [ ] Doplnit technické detaily řešení do dokumentace API

- [ ] **Archivace**
  - [ ] Uložit logy z nasazení do `deploy_logs/logs/`
  - [ ] Archivovat výsledky testů po nasazení
  - [ ] Vytvořit snapshot konfigurace před případnými dalšími změnami

## Další kroky po verifikaci

- [ ] **Plánování dalších vylepšení**
  - [ ] Aktualizace všech importů z `langchain_core.pydantic_v1` na přímé importy z `pydantic`
  - [ ] Refaktorování dalších částí kódu pro lepší serializaci
  - [ ] Implementace lepšího systému logování

- [ ] **Školení a předání**
  - [ ] Aktualizace dokumentace pro vývojáře
  - [ ] Informování týmu o provedených změnách
  - [ ] Školení pro práci s novou verzí LangGraph Platform

## Poznámky

Tento kontrolní seznam by měl být vyplněn po úspěšném nasazení na LangGraph Platform. Jednotlivé položky označte jako dokončené (✅) nebo nedokončené (❌) podle výsledku kontroly. V případě zjištění problémů zaznamenejte jejich popis a návrh řešení do sekce "Poznámky" pod příslušným bodem.

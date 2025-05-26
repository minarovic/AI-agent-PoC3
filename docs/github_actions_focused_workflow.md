# Workflow zaměřený na GitHub Actions

## Problém s lokálním testováním

Při vývoji s využitím lokálního testování docházelo k následujícím problémům:

1. **Nekontrolované úpravy kódu** - během testování byly prováděny změny v produkčním kódu, které nebyly součástí původního zadání
2. **"Pokus-omyl" přístup** - opakované spouštění testů a úpravy kódu vedly k složitějšímu kódu, než bylo potřeba
3. **Implementace podle testů** - místo implementace podle zadání se kód přizpůsoboval testům
4. **Neplánované změny** - tyto změny se dostávaly do produkce

## Nový workflow zaměřený na GitHub Actions

Aby se tyto problémy eliminovaly, přecházíme na workflow zaměřený na GitHub Actions:

### 1. Vývoj (lokálně)
- Implementace kódu do `src/` - **striktně podle zadání**
- Žádné testování během vývoje
- Žádné úpravy kódu podle výsledků lokálních testů

### 2. Commit a push
- Commit pouze implementovaného kódu:
  ```bash
  git add src/ docs/
  git commit -m "Implementace funkce X"
  git push
  ```

### 3. Automatické testování na GitHubu
- GitHub Actions automaticky spustí testy po každém push
- Testy běží v izolovaném prostředí na GitHub serverech
- Výsledky testů jsou viditelné v GitHub rozhraní

### 4. Analýza výsledků
- Pokud testy selžou, prozkoumáte výsledky v GitHub rozhraní
- Identifikujete přesné problémy bez nutnosti lokálního testování

### 5. Opravy na základě GitHub Actions (ne na základě lokálních testů)
- Implementujete opravy podle výsledků GitHub Actions testů
- Opravy commitujete a pushujete
- GitHub Actions opět automaticky otestuje změny

### 6. Nasazení
- Po úspěšném průběhu GitHub Actions testů nasadíte manuálně na LangGraph Platform

## Výhody tohoto přístupu

1. **Oddělení vývoje a testování**
   - Vývoj se zaměřuje pouze na implementaci zadání
   - Testování probíhá automaticky a odděleně od vývoje

2. **Žádné lokální testování během vývoje**
   - Eliminuje pokušení upravovat kód na základě lokálních testů
   - Kód je vyvinut striktně podle zadání

3. **Objektivní hodnocení kódu**
   - GitHub Actions poskytují konzistentní prostředí pro testování
   - Výsledky jsou jasně viditelné a reprodukovatelné

4. **Kontrolované opravy**
   - Opravy jsou založeny na konkrétních výsledcích testů
   - Každá oprava prochází stejným procesem testování

5. **Dokumentované změny**
   - Každá změna má jasný commit a důvod
   - Všechny změny jsou verzovány a sledovatelné

## Lokální sandbox pro experimenty

Pro případné experimentování a prototypování stále používáme:

- Adresář `sandbox/` (není verzován)
- Experimenty nikdy nejdou do produkčního kódu
- Pokud experiment prokáže hodnotu, je reimplementován čistě podle zadání do produkčního kódu

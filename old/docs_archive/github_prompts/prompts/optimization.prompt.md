# Optimalizace výkonu

## Instrukce pro Copilot

Když je aplikace funkční a kód je čistý, je čas zaměřit se na optimalizaci výkonu. Optimalizace by měla být založena na měření a zaměřena na skutečná úzká místa. Postupuj podle následujících kroků:

1. **Profilování aplikace:**
   - Vytvoř profilovací skripty:
     ```bash
     mkdir -p sandbox/profiling
     touch sandbox/profiling/profile_workflow.py
     ```
   - Implementuj měření výkonu klíčových částí:
     - Čas zpracování dotazu
     - Latence jednotlivých komponent
     - Využití paměti
     - Počet volání API

2. **Identifikace úzkých míst:**
   - Spusť profilovací skripty:
     ```bash
     python sandbox/profiling/profile_workflow.py
     ```
   - Analyzuj výsledky a identifikuj:
     - Nejpomalejší komponenty
     - Nejčastěji volané funkce
     - Redundantní operace
     - Neefektivní algoritmy

3. **Implementace optimalizací:**
   - Vytvoř branch pro optimalizace:
     ```bash
     git checkout -b optimize/<název_komponenty>
     ```
   - Implementuj cílené optimalizace:
     - Cachování výsledků
     - Redukce volání API
     - Optimalizace algoritmů
     - Paralelizace operací
     - Snížení režie

4. **Měření zlepšení:**
   - Po každé optimalizaci změř dopad:
     ```bash
     python sandbox/profiling/benchmark.py
     ```
   - Dokumentuj zlepšení:
     ```
     Původní: X ms/operaci
     Po optimalizaci: Y ms/operaci
     Zlepšení: Z%
     ```

5. **Testování optimalizací:**
   - Ujisti se, že optimalizace nezmění funkcionalitu:
     ```bash
     pytest tests/
     ```
   - Push branch na GitHub pro automatické testy:
     ```bash
     git add src/memory_agent/<optimalizovaný_soubor>
     git commit -m "Optimize: <popis_optimalizace> (zlepšení o X%)"
     git push -u origin optimize/<název_komponenty>
     ```

6. **Dokumentace optimalizací:**
   - Vytvoř záznam o optimalizacích:
     ```
     docs/performance/optimizations_<datum>.md
     ```
   - Zahrň:
     - Identifikovaná úzká místa
     - Implementované optimalizace
     - Naměřená zlepšení
     - Případné kompromisy (trade-offs)

## Důležité principy

- **Měř, pak optimalizuj** - vždy založ optimalizace na měření
- **Zaměř se na největší úzká místa** - 20% kódu obvykle způsobuje 80% problémů
- **Zachovej čitelnost** - neobětuj čitelnost kódu pro malé zlepšení výkonu
- **Testuj výsledky** - ujisti se, že optimalizace nezmění funkcionalitu
- **Dokumentuj kompromisy** - každá optimalizace má svá pro a proti

## Další kroky

Po úspěšné optimalizaci je vhodné:
- Aktualizovat dokumentaci výkonu
- Nasadit optimalizovanou verzi (použij prompt `deploy.prompt.md`)
- Nastavit monitoring výkonu v produkci

# Master Prompt: Přehled vývojového procesu

## Instrukce pro Copilot

Tento master prompt poskytuje přehled celého vývojového procesu a odkazuje na specializované prompty pro jednotlivé fáze. Použij tento prompt jako vstupní bod pro navigaci vývojovým procesem.

## Fáze vývojového procesu

### 1. Vývoj a implementace
- Implementace podle jasného zadání
- Striktní dodržování specifikace
- Kód jde přímo do `src/`

**Následující krok:** Po implementaci použij prompt `testing.prompt.md`

### 2. Testování
- Automatické testování pomocí GitHub Actions
- Žádné úpravy kódu během testování
- Analýza výsledků testů

**Následující krok:** Po úspěšných testech použij prompt `deploy.prompt.md`

### 3. Nasazení
- Manuální nasazení na LangGraph Platform
- Validace kódu před nasazením
- Ověření nasazení

**Následující krok:** Po úspěšném nasazení použij prompt `evaluation.prompt.md`

### 4. Hodnocení
- Testování reálných scénářů
- Hodnocení přesnosti a relevance
- Identifikace problémů

**Následující krok:** Po hodnocení použij prompt `improvement.prompt.md`

### 5. Vylepšení
- Implementace cílených oprav
- Prioritizace podle kritičnosti
- Testování každé změny

**Následující krok:** Po implementaci vylepšení se vrať k `testing.prompt.md`

## Specializované workflowy

### Nové funkce
- Návrh a implementace nových funkcí
- Izolované testování
- Integrace do hlavní větve

**Prompt:** `new_feature.prompt.md`

### Kompatibilita
- Řešení problémů s kompatibilitou na LangGraph Platform
- Minimální úpravy pro zajištění funkčnosti
- Dokumentace workaroundů

**Prompt:** `compatibility_fix.prompt.md`

### Refaktorování
- Systematické zlepšování kvality kódu
- Postupné změny s průběžným testováním
- Zachování funkcionality

**Prompt:** `refactoring.prompt.md`

### Optimalizace
- Měření výkonu
- Cílené optimalizace úzkých míst
- Ověření zlepšení

**Prompt:** `optimization.prompt.md`

## Jak používat tyto prompty

1. Začni s tímto master promptem pro pochopení celého procesu
2. V každé fázi vývoje použij odpovídající specializovaný prompt
3. Sleduj "Následující krok" pro navigaci procesem
4. Pro specifické situace použij specializované workflowy

## Nejdůležitější principy

- **Testování pomocí GitHub Actions** - minimalizace lokálního testování
- **Jeden problém = jeden commit** - přehlednost a sledovatelnost změn
- **Manuální nasazení** - prevence nechtěných změn v produkci
- **Dokumentace všech změn** - jasná historie vývoje
- **Postupné iterace** - malé, kontrolovatelné změny

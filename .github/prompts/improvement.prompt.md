# Implementace vylepšení a oprav

## Instrukce pro Copilot

Na základě předchozího hodnocení funkčnosti aplikace je čas implementovat cílená vylepšení a opravy. Zaměř se na nejkritičtější problémy identifikované v hodnocení a postupuj podle následujících kroků:

1. **Prioritizace problémů:**
   - Seřaď identifikované problémy podle priority:
     - **KRITICKÉ:** Problémy blokující základní funkčnost (např. nerozpoznání klíčových společností)
     - **DŮLEŽITÉ:** Problémy ovlivňující kvalitu odpovědí (např. nesprávný typ analýzy)
     - **NICE-TO-HAVE:** Vylepšení pro lepší uživatelský zážitek

2. **Implementace oprav kritických problémů:**
   - Zaměř se na jeden problém v jednom commitu
   - Implementuj minimální změny potřebné k řešení problému
   - Neměň jiné části kódu, které nesouvisí s problémem
   - Pro každou změnu:
     ```bash
     git add src/memory_agent/<upravený_soubor>
     git commit -m "Oprava: <popis_problému>"
     git push
     ```
     - Vyčkej na výsledky GitHub Actions testů
     - Pokračuj až po úspěšných testech

3. **Implementace důležitých vylepšení:**
   - Po vyřešení kritických problémů přejdi k důležitým vylepšením
   - Postupuj stejně - jeden problém, jeden commit
   - Zaměř se na:
     - Zlepšení detekce typů analýz
     - Rozšíření podpory pro další společnosti
     - Optimalizaci zpracování dat

4. **Dokumentace změn:**
   - Pro každé významné vylepšení aktualizuj dokumentaci:
     ```
     docs/improvements_<datum>.md
     ```
   - Zahrň:
     - Popis řešeného problému
     - Implementované řešení
     - Očekávaný dopad
     - Případná omezení nebo rizika

5. **Aktualizace testů:**
   - Přidej nebo aktualizuj testy pokrývající opravené problémy:
     ```bash
     git add tests/<nový_nebo_upravený_test>
     git commit -m "Test: <popis_testu>"
     git push
     ```

## Důležité principy

- **Řeš jeden problém v jednom commitu** - usnadňuje sledování změn
- **Minimální změny** - měň pouze to, co je potřeba k vyřešení problému
- **Testuj každou změnu** - používej GitHub Actions pro ověření
- **Dokumentuj důvody změn** - nejen co jsi změnil, ale proč
- **Postupuj od kritických k méně důležitým** - zajisti nejprve základní funkčnost

## Další kroky

Po implementaci všech potřebných oprav a vylepšení bude aplikace připravena na nové nasazení. Použij prompt `deploy.prompt.md` pro nasazení aktualizované verze.

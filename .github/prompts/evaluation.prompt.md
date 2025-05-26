# Hodnocení funkčnosti aplikace

## Instrukce pro Copilot

Nyní, když je aplikace nasazena na LangGraph Platform, je čas vyhodnotit její funkčnost v reálném prostředí. Zaměř se na ověření, že aplikace správně rozpoznává a zpracovává různé typy analýz. Proveď následující kroky:

1. **Příprava testovacích dotazů:**
   - Připrav sadu testovacích dotazů pokrývajících všechny typy analýz:
     - **General:** "Co je to společnost MB TOOL?"
     - **Risk Comparison:** "Porovnej rizika spojená s firmou BOS AUTOMOTIVE"
     - **Supplier Analysis:** "Udělej analýzu dodavatelů společnosti ADIS TACHOV"
   - Zahrň i dotazy na různé společnosti:
     - MB TOOL
     - BOS / BOS AUTOMOTIVE
     - ADIS TACHOV
     - Flídr plast
     - ŠKODA AUTO

2. **Testování aplikace:**
   - Spusť testovací skript pro vyhodnocení:
     ```bash
     python test_workflow_analysis_types.py
     ```
   - Analyzuj výsledky - zaměř se na:
     - Správné rozpoznání společnosti
     - Správné určení typu analýzy
     - Relevantnost odpovědi
     - Chybové stavy

3. **Vytvoř hodnotící zprávu:**
   - Vytvoř strukturovanou zprávu obsahující:
     - Přehled úspěšnosti rozpoznání společností
     - Přehled úspěšnosti určení typů analýz
     - Identifikované problémy
     - Návrhy na zlepšení

4. **Porovnání s předchozí verzí:**
   - Porovnej výsledky s předchozí verzí aplikace
   - Zaměř se na zlepšení nebo zhoršení v:
     - Přesnosti rozpoznávání
     - Rychlosti odpovědí
     - Relevanci obsahu

5. **Dokumentace výsledků:**
   - Zaznamenej výsledky do dokumentačního souboru:
     ```
     docs/evaluation_results_<datum>.md
     ```

## Důležité principy

- **Objektivní hodnocení** - hodnoť pouze na základě faktů a měřitelných výsledků
- **Zaměř se na problémy z reálného provozu** - ne na teoretické edge cases
- **Identifikuj konkrétní problémy** - ne obecná prohlášení
- **Navrhuj specifická zlepšení** - která lze implementovat v další iteraci

## Další kroky

Na základě výsledků hodnocení budeš moci:
- Navrhnout cílené vylepšení pro další iteraci
- Opravit případné problémy
- Rozšířit podporu pro další typy analýz

Použij prompt `improvement.prompt.md` pro další instrukce k implementaci vylepšení.

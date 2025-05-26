# Testování kódu pomocí GitHub Actions

## Instrukce pro Copilot

Nyní, když jsi dokončil vývoj funkcionality podle zadání, je čas otestovat kód pomocí GitHub Actions. Proveď následující kroky:

1. **Připrav kód pro commit:**
   - Zkontroluj, že jsi upravil pouze soubory v `src/` adresáři
   - Neposílej žádné testovací soubory mimo adresář `tests/`
   - Zkontroluj, že v kódu nejsou žádné debug výpisy nebo zakomentované bloky kódu

2. **Připrav commit:**
   ```bash
   git add src/memory_agent/<upravené_soubory>
   git add tests/<případné_nové_testy>
   git add requirements.txt  # pokud byly přidány nové závislosti
   ```

3. **Vytvoř commit s popisným komentářem:**
   ```bash
   git commit -m "Implementace <název_funkcionality> podle zadání"
   ```

4. **Push na GitHub pro automatické testování:**
   ```bash
   git push
   ```

5. **Sleduj výsledky testů:**
   - Otevři GitHub repozitář v prohlížeči
   - Přejdi na záložku "Actions"
   - Sleduj průběh automatických testů
   - Vyčkej na dokončení testů (může trvat několik minut)

6. **Analýza výsledků:**
   - Pokud testy **prošly** (zelená fajfka ✅):
     - Funkcionalita je připravena pro nasazení
     - Můžeš pokračovat na další krok

   - Pokud testy **selhaly** (červený křížek ❌):
     - Přečti si chybové zprávy v logu testů
     - Identifikuj přesný problém
     - Oprav kód **pouze** v místech, kde je chyba
     - Nepřidávej nové funkce nebo komplexitu
     - Opakuj proces commitu a pushe

## Důležité principy

- **Nikdy neupravuj kód jen proto, aby prošel testy** - testy mají ověřit správnou implementaci zadání
- **Drž se zadání** - nepřidávej funkce navíc
- **Opravuj pouze identifikované problémy** - nezasahuj do částí, které fungují
- **Každá úprava = jeden commit** - pro snadné sledování změn
- **Commit message musí jasně popisovat účel změny** - například "Oprava rozpoznávání společnosti MB TOOL v analyzer.py"

## Další kroky

Po úspěšném dokončení testů budeš připraven na nasazení. Použij prompt `deploy.prompt.md` pro další instrukce.

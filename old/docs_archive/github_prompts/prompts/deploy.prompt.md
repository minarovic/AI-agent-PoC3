# Nasazení kódu na LangGraph Platform

## Instrukce pro Copilot

Nyní, když prošly všechny testy na GitHub Actions, je čas nasadit kód na LangGraph Platform. Tento proces je **záměrně manuální**, aby nedošlo k nechtěnému přepsání fungujícího kódu. Proveď následující kroky:

1. **Ověř stav testů na GitHub Actions:**
   - Zkontroluj, že poslední build v GitHub Actions byl úspěšný (zelená fajfka ✅)
   - Přečti si výsledky testů a ujisti se, že všechny testy prošly

2. **Ověř produkční kód:**
   ```bash
   ./validate_production_code.sh
   ```
   - Zkontroluj, že skript proběhl bez chyb
   - Ujisti se, že kód neobsahuje testovací funkce nebo debugovací výpisy

3. **Příprava na nasazení:**
   - Zkontroluj, že máš správně nastavené proměnné prostředí:
     ```bash
     export OPENAI_API_KEY="your_key_here"
     export ANTHROPIC_API_KEY="your_key_here"  # pokud používáme Anthropic
     export LANGSMITH_API_KEY="your_key_here"  # pro sledování workflow
     ```

4. **Nasazení na LangGraph Platform:**
   - **DŮLEŽITÉ:** Tento krok provede uživatel manuálně
   - Uživatel spustí skript pro nasazení:
     ```bash
     ./deploy_to_langgraph_platform.sh
     ```
   - **NIKDY** nespouštěj tento skript automaticky!

5. **Ověření nasazení:**
   - Po nasazení ověř, že aplikace běží:
     ```bash
     ./verify_deployment.sh
     ```
   - Zkontroluj výstup a ujisti se, že neobsahuje chyby

6. **Dokumentace nasazení:**
   - Vytvoř záznam o nasazení v `deploy_logs/`:
     ```
     Datum: <aktuální_datum>
     Verze: <hash_commitu>
     Změny: <seznam_hlavních_změn>
     Výsledek: <úspěch/neúspěch>
     Poznámky: <případné_poznámky>
     ```

## Důležité principy

- **Nasazení je vždy manuální** - nikdy nespouštěj automaticky deploy skripty
- **Vždy validuj kód před nasazením** - používej validation skripty
- **Dokumentuj každé nasazení** - pro sledování historie změn
- **Při problémech s nasazením** - řeš jen konkrétní problém, ne celou aplikaci
- **Upřednostni minimální změny** - méně změn = méně problémů

## V případě problémů s nasazením

Pokud se nasazení nezdaří:

1. **Zanalyzuj chybové zprávy** v logu nasazení
2. **Identifikuj konkrétní problém** (konfigurace, závislosti, kód)
3. **Vytvoř minimální opravu** zaměřenou pouze na problém
4. **Otestuj opravu** pomocí GitHub Actions
5. **Zkus nasazení znovu** po úspěšných testech

## Další kroky

Po úspěšném nasazení se můžeš vrátit k dalšímu vývoji nebo vyhodnocení funkčnosti. Použij prompt `evaluation.prompt.md` pro další instrukce.

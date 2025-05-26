# Řešení problémů s kompatibilitou na LangGraph Platform

## Instrukce pro Copilot

Pokud se vyskytly specifické problémy s kompatibilitou při nasazení na LangGraph Platform, je třeba je řešit systematicky. Tento prompt tě provede procesem identifikace a řešení problémů s kompatibilitou. Postupuj podle následujících kroků:

1. **Analýza chybových zpráv:**
   - Projdi logy z nasazení na LangGraph Platform
   - Identifikuj konkrétní chybové zprávy
   - Zaměř se na:
     - ImportError - chybějící nebo nekompatibilní závislosti
     - AttributeError - změny v API
     - TypeError - nekompatibilní typy
     - KeyError - chybějící konfigurace

2. **Izolace problému:**
   - Vytvoř minimální reprodukci problému:
     ```bash
     mkdir -p sandbox/compatibility_test
     touch sandbox/compatibility_test/test_issue.py
     ```
   - Implementuj minimální test reprodukující problém
   - Ověř, že problém se vyskytuje i v izolovaném prostředí

3. **Ověření kompatibility závislostí:**
   - Zkontroluj verze závislostí v `requirements.txt`
   - Porovnej s verzemi podporovanými na LangGraph Platform
   - Zaměř se zejména na:
     - langgraph
     - langchain
     - openai (pokud používáme)
     - anthropic (pokud používáme)

4. **Použití Context7 pro API dokumentaci:**
   - Nejprve zjisti přesné ID knihovny:
     ```
     # Použij nástroj resolve-library-id pro zjištění ID knihovny
     resolve-library-id "langgraph"
     ```
   - Získej aktuální dokumentaci k problematické části API:
     ```
     # Použij nástroj get-library-docs pro získání dokumentace
     get-library-docs "context7CompatibleLibraryID" --topic "workflow API"
     ```
   - Prozkoumej dokumentaci pro správný způsob použití API
   - Porovnej s aktuální implementací v kódu

5. **Systematické promýšlení problému:**
   - Použij nástroj `think` pro strukturované promýšlení problému:
     ```
     # Použij nástroj think pro analýzu problému
     think "Analýza kompatibility s LangGraph Platform:
     1. Jaký je přesný problém? ImportError na langgraph.graph.Graph.
     2. Co způsobuje problém? Pravděpodobně změna API v nové verzi.
     3. Jaké jsou možnosti řešení?
       a) Downgrade na kompatibilní verzi
       b) Úprava kódu podle nového API
       c) Implementace adaptéru
     4. Který přístup je nejbezpečnější? Závisí na rozsahu změn..."
     ```
   - Na základě strukturované analýzy zvol nejlepší přístup k řešení

6. **Implementace oprav:**
   - Vytvoř branch pro opravu:
     ```bash
     git checkout -b fix/platform-compatibility
     ```
   - Implementuj minimální změny:
     - Aktualizace verzí závislostí
     - Úprava importů
     - Úprava volání API
     - Zjednodušení komplexních funkcí

5. **Testování oprav:**
   - Nejprve lokálně:
     ```bash
     python sandbox/compatibility_test/test_issue.py
     ```
   - Poté pomocí GitHub Actions:
     ```bash
     git add src/ requirements.txt
     git commit -m "Fix: Kompatibilita s LangGraph Platform"
     git push -u origin fix/platform-compatibility
     ```

6. **Ověření kompatibility s dokumentací:**
   - Pro složitější API problémy použij znovu Context7:
     ```
     # Ověř, že nová implementace odpovídá aktuální dokumentaci
     get-library-docs "context7CompatibleLibraryID" --topic "graph implementation" --tokens 5000
     ```
   - Porovnej implementaci s příklady z dokumentace
   - Ověř, že všechny požadované parametry a typy jsou správně

7. **Dokumentace řešení:**
   - Vytvoř záznam o řešení problému:
     ```
     docs/platform_compatibility/<datum>_<název_problému>.md
     ```
   - Zahrň:
     - Popis problému
     - Příčina problému
     - Implementované řešení
     - Doporučení pro budoucí vývoj

## Důležité principy

- **Minimální změny** - měň pouze to, co je potřeba k vyřešení problému
- **Zachovej funkcionalitu** - řešení kompatibility nesmí změnit funkcionalitu
- **Preferuj zjednodušení** - v případě pochybností odstraň komplexní funkce
- **Dokumentuj workaroundy** - pokud používáš dočasné řešení, jasně to zdokumentuj
- **Testuj v prostředí podobném produkci** - ne jen lokálně
- **Využívej oficiální dokumentaci** - používej Context7 pro přístup k aktuální dokumentaci
- **Systematicky analyzuj problém** - používej nástroj think pro strukturované promýšlení

## Další kroky

Po vyřešení problémů s kompatibilitou je čas na nasazení opravené verze. Použij prompt `deploy.prompt.md` pro nasazení kompatibilní verze aplikace.

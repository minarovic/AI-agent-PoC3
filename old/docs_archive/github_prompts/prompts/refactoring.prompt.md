# Refaktorování kódu

## Instrukce pro Copilot

Když je aplikace stabilní a funkční, je vhodný čas na refaktorování kódu pro zlepšení jeho kvality, čitelnosti a udržitelnosti. Refaktorování by mělo být prováděno postupně a systematicky, aby se minimalizovalo riziko zanesení nových chyb. Postupuj podle následujících kroků:

1. **Identifikace kandidátů na refaktorování:**
   - Zaměř se na:
     - Duplicitní kód
     - Příliš dlouhé funkce (> 50 řádků)
     - Komplexní podmínky
     - Nedostatečně modulární kód
     - Nízké pokrytí testy
   - Vytvoř seznam priorit refaktorování:
     ```
     docs/refactoring/priorities.md
     ```

2. **Příprava testů:**
   - Před refaktorováním zajisti dostatečné pokrytí testy:
     ```bash
     pytest tests/ --cov=src/memory_agent --cov-report=term
     ```
   - Pokud pokrytí není dostatečné, nejprve doplň testy:
     ```bash
     git add tests/test_<modul>.py
     git commit -m "Tests: Zvýšení pokrytí pro <modul>"
     git push
     ```

3. **Postupné refaktorování:**
   - Vytvoř branch pro refaktorování:
     ```bash
     git checkout -b refactor/<název_modulu>
     ```
   - Refaktoruj postupně jednu část kódu:
     - Extrakce opakujícího se kódu do funkcí
     - Rozdělení dlouhých funkcí
     - Zjednodušení komplexních podmínek
     - Zlepšení názvů proměnných a funkcí
     - Přidání dokumentace a typových anotací

4. **Testování po každé změně:**
   - Spusť testy po každé významné změně:
     ```bash
     pytest tests/test_<modul>.py -v
     ```
   - Commituj pouze pokud testy prochází:
     ```bash
     git add src/memory_agent/<modul>.py
     git commit -m "Refactor: <popis_změny>"
     ```

5. **Code review a merge:**
   - Push branch na GitHub:
     ```bash
     git push -u origin refactor/<název_modulu>
     ```
   - Sleduj výsledky GitHub Actions testů
   - Po úspěšných testech merge do main:
     ```bash
     git checkout main
     git merge refactor/<název_modulu>
     git push
     ```

6. **Dokumentace změn:**
   - Aktualizuj technickou dokumentaci:
     ```
     docs/architecture/<modul>.md
     ```
   - Zahrň:
     - Popis nové struktury
     - Důvody pro refaktorování
     - Výhody nové implementace

## Důležité principy

- **Refaktoruj postupně** - malé změny jsou bezpečnější
- **Zachovej funkcionalitu** - refaktorování nesmí změnit chování
- **Testuj po každé změně** - ujisti se, že jsi nic nerozbil
- **Zlepšuj čitelnost** - kód má být čitelnější po refaktorování
- **Dokumentuj záměr** - komentáře by měly vysvětlovat proč, ne jak

## Další kroky

Po úspěšném refaktorování je vhodné:
- Provést code review s týmem
- Aktualizovat technickou dokumentaci
- Nasadit novou verzi (použij prompt `deploy.prompt.md`)

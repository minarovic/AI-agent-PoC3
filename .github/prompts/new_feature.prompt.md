# Implementace nových funkcí

## Instrukce pro Copilot

Nyní, když je základní aplikace stabilní a funkční, je možné implementovat nové funkce pro rozšíření možností Memory Agenta. Při implementaci nových funkcí postupuj podle následujících kroků:

1. **Návrh nové funkce:**
   - Vytvoř detailní návrh nové funkce obsahující:
     - Jasný popis funkcionality
     - Očekávané vstupy a výstupy
     - Interakce s existujícími komponentami
     - Potřebné změny v kódu
   - Ulož návrh do `docs/feature_proposals/`:
     ```
     docs/feature_proposals/<název_funkce>.md
     ```

2. **Izolovaná implementace:**
   - Implementuj novou funkci v izolované větvi:
     ```bash
     git checkout -b feature/<název_funkce>
     ```
   - Implementuj funkci postupně:
     - Základní struktura
     - Unit testy
     - Integrace s existujícím kódem
     - Dokumentace

3. **Testování v izolaci:**
   - Vytvoř testy specifické pro novou funkci:
     ```bash
     git add tests/test_<název_funkce>.py
     ```
   - Spusť testy na GitHub Actions:
     ```bash
     git push -u origin feature/<název_funkce>
     ```
   - Oprav případné problémy odhalené testy

4. **Integrace do hlavní větve:**
   - Po úspěšném testování v izolaci:
     ```bash
     git checkout main
     git merge feature/<název_funkce>
     git push
     ```
   - Sleduj výsledky GitHub Actions testů po merge

5. **Dokumentace nové funkce:**
   - Aktualizuj dokumentaci:
     ```
     docs/features/<název_funkce>.md
     ```
   - Zahrň:
     - Detailní popis funkce
     - Příklady použití
     - Omezení a známé problémy
     - Případné konfigurace

## Důležité principy

- **Nové funkce vždy v izolované větvi** - minimalizuje riziko narušení existující funkčnosti
- **Testy před integrací** - nová funkce musí být řádně otestována
- **Zpětná kompatibilita** - nová funkce nesmí narušit existující funkčnost
- **Postupná implementace** - rozděl komplexní funkce do menších částí
- **Dokumentace součástí implementace** - ne až po dokončení

## Další kroky

Po úspěšné implementaci a integraci nové funkce je čas na nasazení. Použij prompt `deploy.prompt.md` pro nasazení rozšířené verze aplikace.

# Aktualizovaný testovací workflow s GitHub Actions

## Přehled

Tento dokument popisuje aktualizovaný workflow pro testování a nasazování Memory Agenta s využitím GitHub Actions pro automatizaci testů, se zaměřením na oddělení testovacího a produkčního kódu.

## Nová struktura projektu

```
/Users/marekminarovic/AI-agent-Ntier/
├── src/                          # POUZE produkční kód
├── tests/                        # Oficiální testy
├── sandbox/                      # Experimentální kód (není na GitHubu)
│   ├── experimental/             # Experimenty a prototypy
│   ├── testing_playground/       # Ad-hoc testování
│   └── temp_fixes/               # Dočasné opravy pro testování
├── .github/                      # GitHub konfigurace
│   └── workflows/                # GitHub Actions workflow
└── docs/                         # Dokumentace
```

## Aktualizovaný workflow

### 1. Vývoj
- Produkční kód jde do `src/`
- Oficiální testy jdou do `tests/`
- Experimentální kód jde do `sandbox/` (nikdy se nepřenáší na GitHub)

### 2. Testování
- **Oficiální testy**:
  ```bash
  ./run_tests.sh
  ```
- **Sandbox testy** (pouze lokálně):
  ```bash
  ./run_tests.sh --sandbox
  ```

### 3. Validace a commit
- Kontrola produkčního kódu před commitem:
  ```bash
  ./validate_production_code.sh
  ```
- Commit pouze produkčního kódu:
  ```bash
  git add src/ tests/ docs/ .github/
  git commit -m "Popis změn"
  git push
  ```

### 4. Automatické testy na GitHubu
- GitHub Actions spustí testy po každém pushu
- Kontroluje kvalitu kódu (formátování, importy)
- Generuje reporty o pokrytí kódu testy

### 5. Nasazení
- Nasazení na LangGraph Platform **probíhá ručně** pro zabránění nechtěných změn
- Používáme existující skripty pro nasazení, ale pouze po validaci

## Nové GitHub Actions workflow

### `test_memory_agent.yml`
- Testuje kód na různých verzích Pythonu (3.10, 3.11)
- Instaluje závislosti a spouští pytest
- Generuje coverage report pro sledování pokrytí kódu testy

### `validate_production_code.yml`
- Kontroluje formátování kódu (black, isort)
- Spouští linting (flake8)
- Kontroluje, že produkční kód neobsahuje testovací funkce/importy
- Ověřuje, že kód je správně importovatelný

## Přínosy aktualizovaného workflow

1. **Striktní oddělení kódu**
   - Produkční kód je vždy čistý
   - Experimenty zůstávají lokální
   - Sandbox nikdy nejde na GitHub

2. **Automatizované testování**
   - Každý push spouští automatické testy
   - Různé verze Pythonu pro zajištění kompatibility
   - Linting pro konzistentní styl kódu

3. **Kontrolované nasazení**
   - Ruční nasazení na LangGraph Platform
   - Vždy předchází validace
   - Minimalizuje riziko nasazení nechtěných změn

4. **Flexibilní lokální testování**
   - Oddělené spouštění oficiálních a sandbox testů
   - Možnost experimentovat bez ovlivnění produkčního kódu

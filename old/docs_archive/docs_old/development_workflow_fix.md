# Řešení problému s nekontrolovanými změnami kódu

## Identifikovaný problém
- Během testování přidávám funkcionality do produkčního kódu
- Tyto změny nejsou součástí původního zadání
- Kód se stává složitější než bylo potřeba
- Neplánované změny odcházejí na GitHub/LangGraph Platform

## Navrhované řešení: Oddělení prostředí

### 1. Struktura adresářů
```
/Users/marekminarovic/AI-agent-Ntier/
├── src/                          # POUZE produkční kód
├── tests/                        # Oficiální testy
├── sandbox/                      # NOVÝ: Experimentální kód
│   ├── experimental/             # Experimenty a prototypy
│   ├── testing_playground/       # Ad-hoc testování
│   └── temp_fixes/              # Dočasné opravy pro testování
└── docs/
```

### 2. Workflow pravidla

#### FÁZE 1: Implementace (STRICT)
- Implementuji POUZE to, co je v zadání
- ŽÁDNÉ "vylepšení" během implementace
- Kód jde přímo do `src/`

#### FÁZE 2: Testování (IZOLOVANÉ)
- Testovací kód jde do `sandbox/testing_playground/`
- Experimenty jdou do `sandbox/experimental/`
- NIKDY neměním produkční kód během testování

#### FÁZE 3: Schválení změn (KONTROLOVANÉ)
- Pokud test odhalí nutnost změny produkčního kódu:
  1. STOP testování
  2. Vytvořím návrh změny v `sandbox/experimental/`
  3. Získám schválení od uživatele
  4. Teprve pak měním `src/`

### 3. Git workflow
```bash
# Pouze tyto adresáře jdou na GitHub:
git add src/
git add tests/
git add docs/

# NIKDY:
git add sandbox/
```

### 4. Deployment skripty
- Upravím všechny deployment skripty
- Budou ignorovat `sandbox/` adresář
- Přidám kontrolu, že se nasazuje pouze schválený kód

## Implementační kroky

### Krok 1: Vytvoření sandbox struktury
- [ ] Vytvořit `sandbox/` adresář
- [ ] Přesunout všechny experimentální skripty do `sandbox/`
- [ ] Aktualizovat `.gitignore`

### Krok 2: Úprava deployment skriptů
- [ ] Upravit `deploy_to_github.sh` - ignorovat sandbox
- [ ] Přidat kontrolu "clean state" před deploymentem
- [ ] Vytvořit `validate_production_code.sh`

### Krok 3: Rollback současného stavu
- [ ] Identifikovat neschválené změny v `src/`
- [ ] Vrátit pouze na schválený stav
- [ ] Přesunout experimenty do `sandbox/`

### Krok 4: Nový workflow
- [ ] Dokumentovat přesný postup pro budoucí vývoj
- [ ] Vytvořit checklist pro každý deployment

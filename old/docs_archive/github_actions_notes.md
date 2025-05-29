# Poznámky k GitHub Actions workflow

## Preferovaný postup vývoje

1. **Implementace kódu** - Implementujte kód podle zadání do `src/`
2. **Commit a push** - Odešlete kód na GitHub
3. **Automatické testy** - GitHub Actions automaticky spustí testy
4. **Analýza výsledků** - Zkontrolujte výsledky testů v GitHub rozhraní
5. **Opravy** - Implementujte opravy na základě výsledků testů
6. **Nasazení** - Po úspěšných testech nasaďte manuálně na LangGraph Platform

## Důležité poznámky

- **Lokální testování by mělo být minimální** - Používejte jej pouze pro ověření oprav po selhání GitHub Actions testů
- **Vyhněte se úpravám kódu na základě lokálních testů** - To vede k nekontrolovaným změnám
- **Každá změna musí projít GitHub Actions testy** - To zajistí kvalitu kódu
- **Změny musí být založeny na zadání, ne na testech** - Implementujte podle specifikace, ne podle testů

## Instalace GitHub Actions (již provedeno)

1. Vytvořené workflow soubory:
   - `.github/workflows/test_memory_agent.yml` - testování kódu
   - `.github/workflows/validate_production_code.yml` - validace produkčního kódu

2. Nastavení secrets v GitHub repozitáři:
   - `OPENAI_API_KEY` - Pro testy využívající OpenAI API
   - `ANTHROPIC_API_KEY` - Pro testy využívající Anthropic API

## Jak číst výsledky testů

1. Po každém push navštivte GitHub repozitář
2. Klikněte na záložku "Actions"
3. Zkontrolujte nejnovější workflow run
4. Prohlédněte si výsledky testů a chybové zprávy
5. Implementujte opravy na základě těchto výsledků

## Jak nastavit sandbox pro experimenty

Sandbox adresář je pro experimenty a není součástí verzování:

```
sandbox/
├── experimental/       # Pro experimentální implementace
├── testing_playground/ # Pro ad-hoc testování
└── temp_fixes/         # Pro dočasné opravy
```

Veškerý kód v sandbox adresáři je **pouze lokální** a nikdy se neposílá na GitHub.

## Připomenutí

Tento workflow byl zaveden, aby se vyřešil problém s nekontrolovanými změnami během lokálního testování. Dodržujte jej pro zajištění čistého a funkčního kódu.

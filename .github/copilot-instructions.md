````instructions
# AI## ❌ NIKDY
- **Nepřidávaj funkce během oprav**
- **Netestuj a neměň kód podle testů**
- **Nedeployuj automaticky**
- **Nepřidávej složité error handling**
- **Neoslavuj předčasně** - URL ještě neznamená funkční aplikaci
- **Nepřeháněj s pozitivitou** - čekáme na výsledky testůt-Ntier: Minimální instrukce pro nasazení

## 🎯 JEDINÝ CÍL
**Zprovoznit nejjednodušší možnou verzi na LangGraph Platform**

## ✅ Aktuální checklist
- [x] Zjednodušit analyzer.py na minimum
- [x] Opravit Python verze v GitHub Actions
- [x] Opravit langgraph.json konfigurace ✅
- [x] Přidat ANTHROPIC_API_KEY do GitHub Secrets
- [ ] Úspěšné testy v GitHub Actions
- [ ] Nasazení na LangGraph Platform

## 🚨 KRITICKÉ - Dělej pouze toto
1. **Minimální kód** - Žádné extra funkce, pouze základní flow
2. **Oprav chyby z logů** - Přesně podle chybových zpráv
3. **Commit pouze nutné soubory** - src/, requirements.txt, langgraph.json
4. **NETESTUJ LOKÁLNĚ** - Push a čekej na GitHub Actions
5. **ZEPTEJ SE PŘED ZMĚNAMI** - Před opravou kódu nebo přidáním features se vždy zeptat uživatele na potvrzení
6. **UČIT SE Z HISTORIE** - Vždy přečti posledních 5 iterací před akcí

## ❌ NIKDY
- **Nepřidávej funkce během oprav**
- **Netestuj a neměň kód podle testů**
- **Nedeployuj automaticky**
- **Nepřidávej složité error handling**

## 📁 Struktura pro nasazení
```
Produkční soubory:
src/memory_agent/
├── analyzer.py      # HOTOVO - 40 řádků
├── graph.py         # TODO - zjednodušit
├── graph_nodes.py   # TODO - zjednodušit
├── tools.py         # TODO - zjednodušit
├── state.py         # TODO - minimalizovat
└── __init__.py

Konfigurace:
├── langgraph.json   # OPRAVIT - změnit "agent" na "memory_agent"
├── requirements.txt # HOTOVO
└── .env            # Lokální API klíče
```

## 🔧 Aktuální problémy k řešení
1. **langgraph.json** - Špatná reference grafu
2. ~~**GitHub Secrets** - Chybí ANTHROPIC_API_KEY~~ ✅ HOTOVO
3. **Záložní soubory** - Přesunout do ./old

## 🚦 Prioritizace chyb z GitHub Actions
1. **Blokující chyby** (workflow se zastaví) → Opravit ihned
   - Syntax errors, import errors, missing dependencies
2. **Test failures** → IGNOROVAT pro nasazení
   - Podle instrukcí: "Netestuj a neměň kód podle testů"
3. **Warnings** → Ignorovat

## 📝 Dokumentace iterací
Při každé opravě zapiš do `deploy_logs/testing_iteration_log.md`:
- Co bylo opraveno
- Proč (ne "aby to fungovalo", ale konkrétní důvod)
- Co očekáváš (ne "bude fungovat", ale "projde validation fáze")

## 🧠 SAMOUČÍCÍ PROCES
### Před každou akcí:
1. **Přečti posledních 5 iterací** z testing_iteration_log.md
2. **Identifikuj podobné situace** - stejné chyby, podobné problémy
3. **Aplikuj naučené vzory** - co fungovalo, co ne
4. **Formuluj konkrétní očekávání** - ne obecné "bude fungovat"

### Po každé akci:
1. **Zhodnoť přesnost odhadu** - byl očekávaný výsledek správný?
2. **Zapiš lesson learned** - co se potvrdilo, co bylo špatně
3. **Aktualizuj decision tree** - nové if/then pravidlo
4. **Trackuj confidence level** - jak moc si byl jistý

### Pattern Recognition:
- **ModuleNotFoundError + grep nepoužívaný** → Odstranit import (Iterace 21,30)
- **"No configuration schema"** → Přidat ConfigSchema (Iterace 60)
- **Prázdné objekty {}** → Naplnit return hodnoty (Iterace 60)
- **sed selhává** → Python skript (Iterace 39)
- **URL existuje ≠ aplikace funguje** → Čekat na skutečné testy

### Anti-patterns (NEDĚLAT):
- **Předčasné oslavování** - URL není funkčnost
- **Optimistické odhady** - raději pesimisticky
- **Ignorování instrukcí** - NETESTUJ LOKÁLNĚ znamená NETESTUJ LOKÁLNĚ

## ⚙️ Řešení chyb v GitHub Actions
graph TD
    A[Chyba z Actions] --> B{Blokuje deploy?}
    B -->|Ano| C[Opravit ihned]
    B -->|Ne| D{Blokuje další vývoj?}
    D -->|Ano| E[Opravit teď]
    D -->|Ne| F[Zalogovat a pokračovat]
    
    F --> G[Dokončit větší celek]
    G --> H[Vrátit se k opravám]

## 🎯 DECISION FRAMEWORK pro samoučení
### Před opravou:
```
1. Čti testing_iteration_log.md (posledních 5 iterací)
2. Hledej pattern: "Stejná chyba byla v iteraci X"
3. Zkontroluj: "Co tehdy fungovalo/nefungovalo?"
4. Odhad confidence: Jistý 90% / Nejistý 50% / Nevím 10%
5. Konkrétní očekávání: "Projde X fáze" místo "bude fungovat"
```

### Po opravě:
```
1. Skutečný výsledek vs. odhad
2. Confidence level se potvrdil? (90% → skutečně prošlo?)
3. Lesson learned pro další iterace
4. Aktualizuj pattern recognition
````
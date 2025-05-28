
````instructions
# AI-agent-Ntier: Minimální instrukce pro nasazení

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

## ⚙️ Řešení chyb v GitHub Actions
graph TD
    A[Chyba z Actions] --> B{Blokuje deploy?}
    B -->|Ano| C[Opravit ihned]
    B -->|Ne| D{Blokuje další vývoj?}
    D -->|Ano| E[Opravit teď]
    D -->|Ne| F[Zalogovat a pokračovat]
    
    F --> G[Dokončit větší celek]
    G --> H[Vrátit se k opravám]
````
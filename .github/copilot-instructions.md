# AI-agent-Ntier: Minimální instrukce pro nasazení

## 🎯 JEDINÝ CÍL
**Zprovoznit nejjednodušší možnou verzi na LangGraph Platform**

## ✅ Aktuální checklist
- [x] Zjednodušit analyzer.py na minimum
- [x] Opravit Python verze v GitHub Actions
- [ ] Opravit langgraph.json konfigurace
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

## 📝 Pro další kroky viz
- Detailní workflow: `.github/prompts/testing.prompt.md`
- Deploy instrukce: `.github/prompts/deploy.prompt.md`
- Aktuální stav: `deploy_logs/current_status.md`
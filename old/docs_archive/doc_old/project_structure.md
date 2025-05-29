# Struktura projektu a roadmapa implementace

## Struktura projektu AI-agent-Ntier

Následující struktura adresářů a souborů je navržena pro optimální kompatibilitu s LangGraph Platform:

```
AI-agent-Ntier/
├── src/
│   └── memory_agent/
│       ├── __init__.py
│       ├── analyzer.py          # Analýza dotazů a detekce typu analýzy
│       ├── graph.py             # Hlavní StateGraph workflow
│       ├── prompts.py           # Správa specializovaných promptů  
│       └── tools.py             # MockMCPConnector pro přístup k datům
├── mock_data/                   # Testovací data
│   ├── companies/               # Data o společnostech
│   ├── internal_data/           # Interní data
│   ├── people/                  # Data o osobách
│   └── relationships/           # Data o vztazích
├── tests/                       # Testy
│   ├── unit/                    # Unit testy
│   └── integration/             # Integrační testy
├── doc/                         # Dokumentace
│   ├── architecture.md          # Popis architektury
│   ├── api_server_structure.md  # Struktura API a serveru
│   ├── code_examples.md         # Příklady implementace
│   ├── deployment_guide.md      # Návod na nasazení
│   ├── project_structure.md     # Tento soubor
│   └── workflow.md              # Popis workflow
├── .env.template                # Šablona pro konfiguraci prostředí
├── langgraph.json               # Konfigurace pro LangGraph Platform
├── pyproject.toml               # Python projekt konfigurace
├── README.md                    # Hlavní dokumentace projektu
├── requirements.txt             # Seznam závislostí
└── run_langgraph_dev.sh         # Skript pro spuštění vývojového serveru
```

## Roadmapa implementace

### Fáze 1: Základní struktura a konfigurace

1. **Vytvoření základní struktury projektu**
   - Setup adresářové struktury
   - Inicializace Git repozitáře
   - Vytvoření README.md

2. **Konfigurace pro LangGraph Platform**
   - Vytvoření langgraph.json
   - Konfigurace prostředí (.env.template)
   - Nastavení závislostí (requirements.txt)

3. **Setup lokálního vývoje**
   - Skript pro spuštění vývojového serveru
   - Základní testovací prostředí

### Fáze 2: Core komponenty

4. **Implementace analyzátoru**
   - Few-shot prompting s reasoning procesem
   - Detekce typu analýzy
   - Zpracování chyb

5. **Implementace MockMCPConnector**
   - Načítání dat z JSON souborů
   - Normalizace názvů společností
   - Hierarchie výjimek

6. **Implementace PromptRegistry**
   - Centralizovaná správa promptů
   - Specializované prompty pro každý typ analýzy
   - Formátovače dat pro prompty

### Fáze 3: StateGraph workflow

7. **Implementace základního grafu**
   - Definice State pomocí Pydantic BaseModel
   - Uzly pro analýzu a získávání dat
   - Uzel pro generování odpovědi

8. **Implementace podmíněného větvení**
   - Funkce pro rozhodování o toku
   - Podmíněné hrany pro větvení workflow
   - Zpracování chybových stavů

9. **Konfigurace API**
   - Export grafu pro LangGraph Platform
   - Definice vstupních/výstupních typů
   - Konfigurace thread_id pro persistenci

### Fáze 4: Testování a ladění

10. **Implementace unit testů**
    - Testy pro analyzátor
    - Testy pro MockMCPConnector
    - Testy pro PromptRegistry

11. **Implementace integračních testů**
    - End-to-end testy workflow
    - Testy pro různé typy analýz
    - Testy chybových scénářů

12. **Ladění a optimalizace**
    - Ladění promptů
    - Optimalizace workflow
    - Ladění zpracování chyb

### Fáze 5: Nasazení a dokumentace

13. **Finalizace dokumentace**
    - Kompletace všech dokumentů
    - Vytvoření příkladů použití
    - Aktualizace README.md

14. **Příprava nasazení**
    - Nastavení GitHub repozitáře
    - Konfigurace pro LangGraph Platform
    - Testování nasazení

15. **Nasazení a monitorování**
    - Nasazení na LangGraph Platform
    - Testování produkčního nasazení
    - Nastavení monitoringu
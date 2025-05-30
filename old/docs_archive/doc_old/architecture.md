# AI-agent-Ntier Architektura (PoC-3)

## Přehled architektury

AI-agent-Ntier je implementace analytického agenta založeného na LangGraph Platform, který umožňuje analýzu společností, hodnocení rizik a analýzu dodavatelských řetězců. Hlavní důraz je kladen na nasaditelnost na LangGraph Platform s minimálním množstvím specializovaného kódu.

## Klíčové komponenty

### 1. StateGraph Workflow

Jádrem projektu je `StateGraph` workflow, které zajišťuje:
- Zpracování uživatelských dotazů
- Detekci typu analýzy
- Získávání relevantních dat
- Generování odpovědí

Workflow je navržené pro kompatibilitu s LangGraph Platform, což znamená:
- Přímé aktualizace stavu místo Command pattern
- Standardní podmíněné hrany pro řízení toku
- Jasně definované vstupní a výstupní typy

### 2. Analyzer

Analyzátor zajišťuje zpracování uživatelských dotazů a jejich klasifikaci do tří typů analýz:
- `risk_comparison` - Analýza rizikových faktorů společnosti
- `supplier_analysis` - Analýza dodavatelského řetězce
- `general` - Obecná analýza společnosti

Implementace používá few-shot prompting s reasoning procesem pro komplexní dotazy.

### 3. MockMCPConnector

Komponenta pro simulaci přístupu k datům o společnostech:
- Dynamické načítání dat z JSON souborů
- Normalizace názvů společností
- Mapování na ID entit
- Hierarchické zpracování chyb

### 4. PromptRegistry

Centralizovaný registr promptů pro různé typy analýz:
- Specializované prompty pro každý typ analýzy
- Formátování dat pro prompty
- Integrace s LCEL řetězci

## Workflow

Základní workflow agenta:

1. **Analýza dotazu**
   - Uživatel zadá dotaz
   - `analyze_company_input` uzel analyzuje dotaz, identifikuje společnosti a typ analýzy

2. **Podmíněné větvení**
   - Pokud se jedná o analýzu společnosti: pokračuje k získávání dat
   - Pokud nejde o společnost: přeskočí na generování odpovědi
   - Pokud nastane chyba: přesměruje na zpracování chyby

3. **Získávání dat**
   - `fetch_company_data`: Získává základní data o společnosti
   - `fetch_internal_data`: Získává interní data o společnosti
   - `fetch_relationships`: Získává data o vztazích
   - Pro typ `supplier_analysis`: Získává data o dodavatelském řetězci

4. **Generování odpovědi**
   - Výběr specializovaného promptu podle typu analýzy
   - Formátování dat pro prompt
   - Generování odpovědi pomocí LLM

5. **Vrácení výsledku**
   - Vrácení odpovědi a metadat uživateli

## Diagram komponent

```
                          ┌─────────────────┐
                          │                 │
                          │    Uživatel     │
                          │                 │
                          └────────┬────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────┐
│                                                      │
│                  LangGraph Server                    │
│                                                      │
│  ┌──────────────┐      ┌──────────────────────────┐  │
│  │              │      │                          │  │
│  │   Analyzer   │◄────►│     StateGraph           │  │
│  │              │      │                          │  │
│  └──────────────┘      └──────────────┬───────────┘  │
│                                       │              │
│  ┌──────────────┐                     │              │
│  │              │                     │              │
│  │PromptRegistry│◄────────────────────┘              │
│  │              │                                    │
│  └──────────────┘                                    │
│                                                      │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
         ┌───────────────────┐
         │                   │
         │  MockMCPConnector │
         │                   │
         └─────────┬─────────┘
                   │
                   ▼
         ┌───────────────────┐
         │                   │
         │     Mock data     │
         │                   │
         └───────────────────┘
```

## Struktura projektu

```
AI-agent-Ntier/
├── src/
│   └── memory_agent/
│       ├── graph.py        # Definice StateGraph workflow
│       ├── analyzer.py     # Analýza dotazů a detekce typu
│       ├── prompts.py      # Specializované prompty
│       └── tools.py        # MockMCPConnector
├── mock_data/              # Testovací data
├── langgraph.json          # Konfigurace LangGraph Platform
└── doc/                    # Dokumentace
```
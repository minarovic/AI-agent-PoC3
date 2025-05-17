# Workflow pro AI-agent-Ntier

Tento dokument popisuje podrobný workflow AI-agent-Ntier pro zpracování uživatelských dotazů a generování odpovědí.

## Základní workflow

StateGraph workflow je implementováno v `src/memory_agent/graph.py` a obsahuje následující uzly a hrany:

```
START
  │
  ▼
┌─────────────────────┐
│ analyze_company_input│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  is_error_state     ├─────► handle_error        │
└──────────┬──────────┘     └─────────┬───────────┘
           │                          │
           ▼                          │
┌─────────────────────┐               │
│should_analyze_company│               │
└──────────┬──────────┘               │
           │                          │
           ▼                          │
┌─────────────────────┐               │
│ fetch_company_data  │               │
└──────────┬──────────┘               │
           │                          │
           ▼                          │
┌─────────────────────┐               │
│  is_error_state     ├───────────────┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ fetch_internal_data │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  is_error_state     ├───────────────┐
└──────────┬──────────┘               │
           │                          │
           ▼                          │
┌─────────────────────┐               │
│should_fetch_relations│               │
└──────────┬──────────┘               │
           │                          │
           ▼                          │
┌─────────────────────┐               │
│ fetch_relationships │               │
└──────────┬──────────┘               │
           │                          │
           ▼                          │
┌─────────────────────┐               │
│  is_error_state     ├───────────────┘
└──────────┬──────────┘               
           │                          
           ▼                          
┌─────────────────────┐               
│  generate_response  │◄──────────────┘
└──────────┬──────────┘
           │
           ▼
          END
```

## Detailní popis nodes

### 1. analyze_company_input

- **Vstup**: Query od uživatele
- **Akce**: Analýza dotazu pomocí `analyzer.analyze_query()`
- **Výstup**: Aktualizace stavu s informacemi o identifikovaných společnostech a typu analýzy
- **Pokračuje na**: Kontrola chyb pomocí `is_error_state`

### 2. is_error_state

- **Vstup**: Aktuální stav
- **Akce**: Kontrola, zda došlo k chybě
- **Výstup**: "error" nebo "success" pro podmíněné větvení
- **Pokračuje na**: `handle_error` pokud došlo k chybě, jinak pokračuje dál

### 3. should_analyze_company

- **Vstup**: Aktuální stav s výsledky analýzy
- **Akce**: Rozhodnutí, zda se má provést analýza společnosti
- **Výstup**: "analyze" nebo "skip" pro podmíněné větvení
- **Pokračuje na**: `fetch_company_data` nebo `generate_response`

### 4. fetch_company_data

- **Vstup**: State s identifikovanou společností
- **Akce**: Získání dat o společnosti pomocí `MockMCPConnector`
- **Výstup**: Aktualizace stavu s daty o společnosti
- **Pokračuje na**: Kontrola chyb pomocí `is_error_state`

### 5. fetch_internal_data

- **Vstup**: State s identifikovanou společností
- **Akce**: Získání interních dat o společnosti
- **Výstup**: Aktualizace stavu s interními daty
- **Pokračuje na**: Kontrola chyb pomocí `is_error_state`

### 6. should_fetch_relations

- **Vstup**: Aktuální stav 
- **Akce**: Rozhodnutí, zda se mají získat data o vztazích
- **Výstup**: "fetch" nebo "skip" pro podmíněné větvení
- **Pokračuje na**: `fetch_relationships` nebo `generate_response`

### 7. fetch_relationships

- **Vstup**: State s identifikovanou společností
- **Akce**: Získání dat o vztazích společnosti
- **Výstup**: Aktualizace stavu s daty o vztazích
- **Pokračuje na**: Kontrola chyb pomocí `is_error_state`

### 8. generate_response

- **Vstup**: State se všemi získanými daty
- **Akce**: 
  1. Výběr specializovaného promptu podle typu analýzy
  2. Formátování dat pro prompt
  3. Generování odpovědi pomocí LLM
- **Výstup**: Aktualizace stavu s odpovědí pro uživatele
- **Pokračuje na**: END

### 9. handle_error

- **Vstup**: State s chybou
- **Akce**: Zpracování chyby a generování chybové zprávy
- **Výstup**: Aktualizace stavu s chybovou zprávou
- **Pokračuje na**: `generate_response`

## Typy analýz

Workflow podporuje tři typy analýz, každá s jiným zaměřením:

### 1. risk_comparison

- **Zaměření**: Hodnocení rizikových faktorů společnosti
- **Data**: Základní data, interní data, vztahy
- **Výstup**: Strukturovaná analýza rizik

### 2. supplier_analysis

- **Zaměření**: Analýza dodavatelského řetězce
- **Data**: Základní data, interní data, vztahy, dodavatelský řetězec
- **Výstup**: Strukturovaná analýza dodavatelského řetězce

### 3. general

- **Zaměření**: Obecné informace o společnosti
- **Data**: Základní data, interní data, vztahy
- **Výstup**: Obecný přehled o společnosti

## Zacházení s chybami

Workflow obsahuje robustní zpracování chyb:

1. Každý uzel obsahuje `try/except` blok pro zachycení chyb
2. Při chybě je nastaven `error` atribut ve stavu
3. Podmíněné hrany s `is_error_state` automaticky přesměrují tok na `handle_error`
4. `handle_error` vytvoří uživatelsky přívětivou chybovou zprávu

## Persistentní stav

Každá konverzace má svůj vlastní persistentní stav pomocí `thread_id`:

1. Klient poskytne `thread_id` při každém volání API
2. LangGraph Platform automaticky ukládá a načítá stav pro daný `thread_id`
3. Stav obsahuje historii konverzace, výsledky analýz a získaná data
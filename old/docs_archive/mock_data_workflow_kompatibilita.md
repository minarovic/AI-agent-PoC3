# Analýza kompatibility dat a workflow

## Přehled dat v mock_data_2

### Dostupné soubory pro každou společnost:

1. **entity_search_[společnost].json**
   - **Obsah:** Základní informace o entitě (ID, typ, název, země, adresy, rizikové faktory)
   - **Vhodné pro:** General analýzu, první fázi risk_comparison

2. **entity_detail_[společnost].json**
   - **Obsah:** Rozšířené informace včetně detailů o riziku, metadata, popis
   - **Vhodné pro:** Risk comparison, detailnější general analýzu

3. **relationships_[společnost].json**
   - **Obsah:** Dva formáty vztahů (jednodušší `data` a detailnější `relationships`)
   - **Vhodné pro:** Supplier analysis, vztahové analýzy

4. **supply_chain_[společnost].json**
   - **Obsah:** Hierarchická struktura s cestami mezi entitami, produkty, HS kódy
   - **Vhodné pro:** Supplier analysis, analýzu dodavatelského řetězce

5. **internal_[společnost].json**
   - **Obsah:** Interní data, tier klasifikace, HS kódy, obchodní aktivity
   - **Vhodné pro:** Doplňkové informace pro všechny typy analýz

## Struktura workflow v projektu

Workflow v projektu AI-agent-Ntier je navrženo pro zpracování dotazů a analýzu dat s následujícími komponenty:

### Analytické uzly:
- `route_query` - Určuje typ dotazu (company, person, relationship, custom)
- `prepare_company_query` - Připraví parametry pro dotazy na společnost
- `retrieve_company_data` - Získá základní data o společnosti
- `retrieve_additional_company_data` - Získá další data o společnosti
- `analyze_company_data` - Provede analýzu dat společnosti

### Detekce dotazů:
- `analyze_query_sync` - Synchronní funkce pro určení typu dotazu
- `analyze_company_query` - Specializovaná LLM funkce pro detekci společnosti

## Nesoulad mezi daty a workflow

1. **Nedostatečná specializace podle typu analýzy**
   - Aktuální workflow nerozlišuje mezi risk_comparison, supplier_analysis a general typy
   - Zatímco data jsou jasně strukturována pro různé typy analýz

2. **Chybějící mapování datových souborů**
   - Workflow neobsahuje jasné mapování na konkrétní soubory v mock_data_2
   - Například není definováno, kdy použít entity_detail vs entity_search

3. **Nekonzistentní použití MCP konektoru**
   - MCP konektor v projektu pravděpodobně nepracuje konzistentně se všemi typy souborů
   - Některé uzly mohou očekávat data v odlišném formátu

## Doporučené úpravy

### 1. Přidat explicitní podporu pro typy analýz
```python
def determine_analysis_type(state: State) -> State:
    """
    Určí typ požadované analýzy (risk_comparison, supplier_analysis, general)
    na základě dotazu a předchozí detekce společnosti.
    """
    # Přidání logiky rozlišení typů analýz
    analysis_type = "general"  # výchozí hodnota
    
    query = state.current_query.lower()
    # Detekce typů analýz
    if any(kw in query for kw in ["risk", "sankce", "compliance", "riziko"]):
        analysis_type = "risk_comparison"
    elif any(kw in query for kw in ["supplier", "dodavatel", "vztah", "relationship"]):
        analysis_type = "supplier_analysis"
        
    return {"analysis_type": analysis_type}
```

### 2. Přidat mapování na soubory podle typu analýzy
```python
def load_specialized_data(state: State) -> State:
    """
    Načte specializovaná data podle typu analýzy.
    """
    company_name = state.company_data.get("basic_info", {}).get("name", "")
    analysis_type = state.analysis_type
    
    # Mapování typu analýzy na soubory
    if analysis_type == "risk_comparison":
        # Načíst entity_detail_*.json pro rizikovou analýzu
        # ...
    elif analysis_type == "supplier_analysis":
        # Načíst relationships_*.json a supply_chain_*.json
        # ...
    else:  # general
        # Načíst základní informace z entity_search_*.json
        # ...
        
    return {"specialized_data": specialized_data}
```

### 3. Upravit retrieve_additional_company_data
Rozšířit funkci `retrieve_additional_company_data` tak, aby načítala data specifická pro daný typ analýzy z příslušných souborů v mock_data_2.

### 4. Upravit MockMCPConnector
Přizpůsobit MockMCPConnector pro práci s více typy souborů a poskytování různých sad dat podle typu požadované analýzy.

## Závěr

Mock data v mock_data_2 obsahují bohatou sadu informací pro různé typy analýz, ale současné workflow v projektu AI-agent-Ntier není plně optimalizováno pro jejich využití. Implementací výše uvedených doporučení by bylo možné lépe využít potenciál těchto dat a poskytnout kvalitnější analýzy pro koncové uživatele.

# Analýza implementace typů analýz v Memory Agent

Tento dokument popisuje implementaci podpory pro různé typy analýz v Memory Agent a vysvětluje, jak jednotlivé komponenty spolupracují při zpracování různých typů dotazů.

## Typy podporovaných analýz

Memory Agent nyní podporuje tři základní typy analýz:

1. **General** - Obecná analýza společnosti zaměřená na základní informace
2. **Risk Comparison** - Analýza rizik a compliance pro společnosti
3. **Supplier Analysis** - Analýza dodavatelských vztahů a řetězců.

## Detekce typů analýz

Určení typu analýzy je implementováno v modulu `analyzer.py` pomocí funkce `detect_analysis_type()`:

```python
def detect_analysis_type(query: str, response: str = "") -> AnalysisType:
    """Detekuje typ analýzy na základě klíčových slov v dotazu."""
    response = response.lower() if response else ""
    query = query.lower()
    
    # Rozšířené seznamy klíčových slov pro lepší detekci
    risk_keywords = [
        "risk", "rizik", "rizic", "compliance", "sanctions", "sankce", 
        "bezpečnost", "security", "regulace", "regulation",
        "aml", "kyc", "fatf", "ofac", "embargo", "reputace"
    ]
    
    supplier_keywords = [
        "supplier", "dodavatel", "supply chain", "relationships", 
        "vztahy", "dodávky", "tier", "odběratel", "procurement",
        "logistics", "logistika", "distributor", "vendor", "nákup"
    ]
    
    if any(kw in response or kw in query for kw in risk_keywords):
        return "risk_comparison"
    elif any(kw in response or kw in query for kw in supplier_keywords):
        return "supplier_analysis"
    else:
        return "general"
```

Tato funkce je volána z funkce `determine_analysis_type()` v modulu `graph_nodes.py`, která aktualizuje stav workflow:

```python
def determine_analysis_type(state: State) -> State:
    """Zjednodušená funkce pro určení typu analýzy z dotazu."""
    analysis_type = "general"  # Výchozí typ
    query = state.current_query.lower() if state.current_query else ""
    
    try:
        from memory_agent.analyzer import detect_analysis_type
        analysis_type = detect_analysis_type(query)
    except Exception as e:
        # Záložní řešení
        logger.warning(f"Nelze použít analyzer.detect_analysis_type: {str(e)}")
        
        if any(kw in query for kw in ["risk", "riziko", "sankce", "compliance"]):
            analysis_type = "risk_comparison"
        elif any(kw in query for kw in ["supplier", "dodavatel", "supply chain"]):
            analysis_type = "supplier_analysis"
    
    return {"analysis_type": analysis_type}
```

## Načítání dat podle typu analýzy

Podle zjištěného typu analýzy jsou načtena příslušná data v funkci `retrieve_additional_company_data()`:

```python
def retrieve_additional_company_data(state: State) -> State:
    """Zjednodušená funkce pro získání dat pro analýzu podle typu analýzy."""
    try:
        company_id = state.company_data.get("basic_info", {}).get("id")
        analysis_type = getattr(state, "analysis_type", "general")
        
        # Inicializace návratových dat
        financial_data = {}
        search_info = {}
        relationships_data = {}
        supply_chain_data = {}
        risk_factors_data = {}
        
        # Načteme dodatečná data podle typu analýzy
        if analysis_type == "general":
            search_info = mcp_connector.get_company_search_data(company_id)
        elif analysis_type == "risk_comparison":
            risk_factors_data = mcp_connector.get_risk_factors_data(company_id)
        elif analysis_type == "supplier_analysis":
            relationships = mcp_connector.get_company_relationships(company_id)
            relationships_data = {company_id: relationships}
            
            supply_chain = mcp_connector.get_supply_chain_data(company_id)
            supply_chain_data = {company_id: supply_chain}
        
        # Sestavení výsledku podle typu analýzy
        result = {
            "company_data": {},
            "mcp_connector": mcp_connector
        }
        
        # Přidání dat podle typu analýzy
        if analysis_type == "general":
            result["company_data"] = {
                "financials": financial_data,
                "search_info": search_info
            }
        elif analysis_type == "risk_comparison":
            result["company_data"] = {
                "financials": financial_data
            }
            result["risk_factors_data"] = risk_factors_data
        elif analysis_type == "supplier_analysis":
            result["relationships_data"] = relationships_data
            result["supply_chain_data"] = supply_chain_data
        
        return result
    except Exception as e:
        return {"error_state": {"error": "Data retrieval error", "error_type": "data_access_error"}}
```

## Analýza dat podle typu analýzy

Analýza načtených dat je realizována ve funkci `analyze_company_data()`:

```python
def analyze_company_data(state: State) -> State:
    """Provede analýzu dat společnosti podle určeného typu analýzy."""
    analysis_type = getattr(state, "analysis_type", "general")
    
    # Inicializace základní struktury výsledku analýzy
    analysis_result = {
        "company_name": company_name,
        "company_id": company_id,
        "analysis_type": analysis_type,
        "timestamp": utils.get_current_timestamp(),
    }
    
    # Specializovaná analýza podle typu
    if analysis_type == "general":
        # Zpracování základních informací a finančních dat
        search_info = state.company_data.get("search_info", {})
        financials = state.company_data.get("financials", {})
        
        # Sestavení analýzy pro general typ
        analysis_result.update({
            "summary": f"Obecná analýza společnosti {company_name}",
            "basic_info": {...},
            "financial_overview": {...},
            "key_findings": [...]
        })
    
    elif analysis_type == "risk_comparison":
        # Zpracování rizikových faktorů
        risk_factors_data = getattr(state, "risk_factors_data", {})
        
        # Sestavení analýzy pro risk_comparison typ
        analysis_result.update({
            "summary": f"Analýza rizik pro společnost {company_name}",
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "key_findings": [...]
        })
    
    elif analysis_type == "supplier_analysis":
        # Zpracování vztahů a dodavatelského řetězce
        relationships_data = getattr(state, "relationships_data", {}).get(company_id, [])
        supply_chain_data = getattr(state, "supply_chain_data", {}).get(company_id, [])
        
        # Sestavení analýzy pro supplier_analysis typ
        analysis_result.update({
            "summary": f"Analýza dodavatelů pro společnost {company_name}",
            "suppliers": suppliers,
            "supply_chain": supply_chain,
            "key_findings": [...]
        })
    
    return {"analysis_result": analysis_result}
```

## Mapování typů analýz na soubory mock dat

| Typ analýzy | Potřebné soubory | Metody MockMCPConnector |
|-------------|-----------------|------------------------|
| General | entity_search_*.json, internal_*.json | get_company_search_data(), get_company_financials() |
| Risk Comparison | entity_detail_*.json | get_risk_factors_data() |
| Supplier Analysis | relationships_*.json, supply_chain_*.json | get_company_relationships(), get_supply_chain_data() |

## Ukázka workflow s různými typy analýz

### General analýza
```
1. Dotaz: "Jaké jsou základní informace o společnosti Adis?"
2. Detekce typu analýzy: general
3. Načtení dat: entity_search_adis.json, internal_adis.json
4. Analýza dat: Zpracování základních informací a finančních údajů
5. Výstup: Základní profil společnosti s finančním přehledem
```

### Risk Comparison analýza
```
1. Dotaz: "Jaká jsou rizika spojená se společností BOS Automotive?"
2. Detekce typu analýzy: risk_comparison
3. Načtení dat: entity_detail_bos_cze.json (sekce risk)
4. Analýza dat: Zpracování rizikových faktorů a výpočet rizikového skóre
5. Výstup: Přehled rizik a compliance status společnosti
```

### Supplier Analysis analýza
```
1. Dotaz: "Kteří jsou hlavní dodavatelé společnosti Flidr?"
2. Detekce typu analýzy: supplier_analysis
3. Načtení dat: relationships_flidr.json, supply_chain_flidr.json
4. Analýza dat: Zpracování dodavatelských vztahů a řetězce
5. Výstup: Seznam dodavatelů s detaily o vztazích
```

## Závěr

Implementace podpory pro typy analýz umožňuje Memory Agent efektivně zpracovávat různé typy dotazů a poskytovat relevantní informace z dostupných dat. Architektura je navržena modulárně, takže je možné v budoucnu snadno přidat další typy analýz nebo rozšířit stávající.

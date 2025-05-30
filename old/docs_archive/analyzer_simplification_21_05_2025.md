# Zjednodušení analyzer.py - 21.05.2025

## Provedené změny

### 1. Odstranění komplexních struktur

- Odstraněna komplexní struktura s few-shot examples (`RISK_EXAMPLES`, `SUPPLIER_EXAMPLES`, `GENERAL_EXAMPLES`)
- Odstraněny kroky uvažování (`REASONING_STEPS`)
- Odstraněn složitý prompt s few-shot příklady (`ANALYZER_PROMPT`)
- Odstraněna funkce pro formátování příkladů (`format_examples`)

### 2. Zjednodušení funkcí

#### Funkce `detect_analysis_type`
- Ponechána jednoduchá implementace založená na klíčových slovech
- Přímá detekce typu analýzy bez dotazování LLM

```python
def detect_analysis_type(query: str) -> AnalysisType:
    """
    Detekce typu analýzy na základě klíčových slov v dotazu.
    
    Args:
        query: Text uživatelského dotazu
        
    Returns:
        AnalysisType: Zjištěný typ analýzy (risk_comparison, supplier_analysis, general)
    """
    query = query.lower()
    
    # Klíčová slova pro detekci typu "risk_comparison"
    risk_keywords = [
        "risk", "rizik", "rizic", "compliance", "sanctions", "sankce", 
        "bezpečnost", "security", "regulace", "regulation", "embargo"
    ]
    
    # Klíčová slova pro detekci typu "supplier_analysis"
    supplier_keywords = [
        "supplier", "dodavatel", "supply chain", "vztahy", "dodávky", 
        "tier", "odběratel", "vendor", "nákup"
    ]
    
    if any(kw in query for kw in risk_keywords):
        logger.info(f"Detekován typ analýzy 'risk_comparison' pro dotaz: {query[:30]}...")
        return "risk_comparison"
    elif any(kw in query for kw in supplier_keywords):
        logger.info(f"Detekován typ analýzy 'supplier_analysis' pro dotaz: {query[:30]}...")
        return "supplier_analysis"
    else:
        logger.info(f"Detekován výchozí typ analýzy 'general' pro dotaz: {query[:30]}...")
        return "general"
```

#### Funkce `analyze_company_query`
- Zjednodušena pro přímou extrakci názvu společnosti a typu analýzy
- Prioritizace známých společností z definovaného slovníku

```python
def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Jednoduchá funkce pro extrakci názvu společnosti a typu analýzy z dotazu.
    
    Args:
        query: Uživatelský dotaz k analýze
        
    Returns:
        Tuple of (název_společnosti, typ_analýzy)
    """
    # Kontrola známých společností
    for company, analysis_type in KNOWN_COMPANIES.items():
        if company in query:
            logger.info(f"Nalezena známá společnost: {company}, typ analýzy: {analysis_type}")
            return company, analysis_type
    
    # Jednoduchá extrakce pomocí regex - hledáme velká písmena následovaná textem
    company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
    matches = re.findall(company_pattern, query)
    
    if matches:
        company = matches[0].strip()
        logger.info(f"Extrahován název společnosti pomocí regex: {company}")
    else:
        company = "Unknown Company"
        logger.warning("Nepodařilo se extrahovat název společnosti z dotazu")
    
    # Detekce typu analýzy
    analysis_type = detect_analysis_type(query)
    
    return company, analysis_type
```

#### Funkce `analyze_query_sync`
- Zjednodušena pro přímé určení typu dotazu
- Prioritizace detekce dotazů o společnostech

```python
def analyze_query_sync(user_input: str, ...) -> str:
    """
    Jednoduchá synchronní funkce pro analýzu typu dotazu.
    Prioritně vrací "company" pro dotazy o firmách.
    """
    # Kontrola, zda dotaz obsahuje název známé společnosti
    if any(company in user_input for company in KNOWN_COMPANIES):
        return "company"
    
    # Pokud nenajdeme známou společnost, hledáme kapitalizované názvy
    company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
    matches = re.findall(company_pattern, user_input)
    if any(len(match.strip()) > 2 for match in matches):
        return "company"
    
    # Další kontroly pro různé typy dotazů...
```

### 3. Zachování kompatibility

- Zachována zpětná kompatibilita pro všechny klíčové funkce
- Ponechány aliasy pro zpětnou kompatibilitu (`analyze_query_async = analyze_query_sync`)
- Zachována stejná struktura návratových hodnot

## Výhody změn

1. **Zjednodušení kódu** - odstranění nepotřebné komplexity
2. **Vyšší rychlost zpracování** - eliminace volání LLM pro rutinní analýzu
3. **Vyšší spolehlivost** - menší závislost na externích službách
4. **Lepší čitelnost kódu** - zjednodušení pro snadnější údržbu
5. **Eliminace hallucinations** - LLM již není využíván pro klíčové rozhodování

## Testování

Testy potvrzují, že zjednodušený analyzer.py správně detekuje:
- Typy analýz pro různé dotazy (risk_comparison, supplier_analysis, general)
- Názvy společností (MB TOOL, ADIS TACHOV, BOS AUTOMOTIVE, Flídr plast, ŠKODA AUTO)
- Typy dotazů (company, person, relationship, custom)

Kód byl testován samostatnými testy i v rámci celého workflow.

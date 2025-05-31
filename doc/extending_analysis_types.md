# Rozšíření typů analýz v Memory Agent

Tento návod popisuje detailní postupy pro přidávání nových typů analýz do Memory Agent aplikace.

## Současné typy analýz

Aplikace aktuálně podporuje:

1. **`general`** - Obecné informace o společnosti
2. **`risk_comparison`** - Analýza rizik a compliance
3. **`supplier_analysis`** - Analýza dodavatelských vztahů

## Architektura systému typů analýz

### Tok zpracování

```
User Query → Type Detection → Data Loading → Analysis → Response
     ↓              ↓             ↓           ↓         ↓
  "Risk analysis" → risk_comparison → risk_data → analysis → JSON
```

### Klíčové komponenty

1. **Detekce typu** - `analyzer.py` (pokud rozšiřujeme)
2. **Data loading** - `MockMCPConnector` v `tools.py`
3. **Analýza** - logika v `analyze_company` funkci
4. **Mock data** - JSON soubory v `mock_data_2/`

## Přidání nového typu analýzy

### Krok 1: Definice nového typu

Předpokládejme, že chceme přidat typ `financial_analysis` pro finanční analýzu společností.

### Krok 2: Příprava mock dat

Vytvořte nové JSON soubory v `mock_data_2/`:

```json
// mock_data_2/financial_adis.json
{
  "company_id": "adis",
  "financial_metrics": {
    "revenue": {
      "2023": 150000000,
      "2022": 135000000,
      "2021": 120000000,
      "currency": "CZK"
    },
    "profit_margin": {
      "2023": 0.12,
      "2022": 0.10,
      "2021": 0.08
    },
    "debt_to_equity": 0.35,
    "current_ratio": 1.8,
    "quick_ratio": 1.2
  },
  "financial_health": "stable",
  "credit_rating": "BBB+",
  "recommendations": [
    "Strong cash flow management",
    "Consider expansion opportunities",
    "Monitor debt levels"
  ]
}
```

```json
// mock_data_2/financial_mbtool.json
{
  "company_id": "mbtool", 
  "financial_metrics": {
    "revenue": {
      "2023": 85000000,
      "2022": 78000000,
      "2021": 72000000,
      "currency": "CZK"
    },
    "profit_margin": {
      "2023": 0.15,
      "2022": 0.13,
      "2021": 0.11
    },
    "debt_to_equity": 0.28,
    "current_ratio": 2.1,
    "quick_ratio": 1.5
  },
  "financial_health": "strong",
  "credit_rating": "A-",
  "recommendations": [
    "Excellent financial position",
    "Ready for aggressive expansion",
    "Consider dividend distribution"
  ]
}
```

### Krok 3: Rozšíření MockMCPConnector

```python
# src/memory_agent/tools.py - přidejte novou metodu

def get_financial_analysis_data(self, company_id: str) -> Dict[str, Any]:
    """
    Načte finanční analýzu pro společnost podle ID.
    
    Args:
        company_id: Identifikátor společnosti
        
    Returns:
        Dict s finančními daty pro analýzu
        
    Raises:
        EntityNotFoundError: Pokud finanční data nejsou dostupná
    """
    try:
        file_path = os.path.join(self.data_path, f"financial_{company_id}.json")
        return self._load_json_file(file_path)
    except FileNotFoundError:
        logger.warning(f"Finanční data pro {company_id} nenalezena")
        return {
            "company_id": company_id,
            "financial_metrics": {},
            "financial_health": "unknown",
            "error": "Financial data not available"
        }
```

### Krok 4: Rozšíření detekce typu (volitelné)

Pokud chcete rozšířit automatickou detekci typu:

```python
# src/memory_agent/analyzer.py - pokud budete rozšiřovat
# POZNÁMKA: Současná verze má zjednodušenou implementaci

def detect_analysis_type(query: str) -> str:
    """Rozšířená detekce typů analýz."""
    query = query.lower()
    
    # Klíčová slova pro finanční analýzu
    financial_keywords = [
        "financial", "finance", "finanční", "revenue", "profit", 
        "margin", "cash flow", "debt", "equity", "ratio",
        "income", "balance sheet", "performance", "výnosy",
        "zisk", "bilance", "cash"
    ]
    
    risk_keywords = [
        "risk", "rizik", "rizic", "compliance", "sanctions", "sankce", 
        "bezpečnost", "security", "regulace", "regulation", "embargo"
    ]
    
    supplier_keywords = [
        "supplier", "dodavatel", "supply chain", "relationships", 
        "vztahy", "dodávky", "tier", "odběratel", "procurement"
    ]
    
    # Priorita detekce - specifické typy před obecnými
    if any(kw in query for kw in financial_keywords):
        return "financial_analysis"
    elif any(kw in query for kw in risk_keywords):
        return "risk_comparison"
    elif any(kw in query for kw in supplier_keywords):
        return "supplier_analysis"
    else:
        return "general"
```

### Krok 5: Rozšíření hlavní analýzy

```python
# src/memory_agent/analyzer.py - rozšíření analyze_company funkce

def analyze_company(query: str) -> str:
    """
    Rozšířená analýza s podporou finančního typu.
    """
    try:
        connector = MockMCPConnector()
        
        # Získání základních dat společnosti
        company_data = connector.get_company_by_name(query)
        company_id = company_data.get("id") if company_data else None
        
        # Detekce typu analýzy
        analysis_type = detect_analysis_type(query)
        
        # Inicializace výsledku
        result = {
            "query_type": analysis_type,
            "company_data": company_data,
            "analysis_complete": True,
            "query": query
        }
        
        if company_id:
            if analysis_type == "financial_analysis":
                # Specifická logika pro finanční analýzu
                financial_data = connector.get_financial_analysis_data(company_id)
                
                # Výpočet dodatečných metrik
                additional_metrics = calculate_financial_metrics(financial_data)
                
                result.update({
                    "financial_data": financial_data,
                    "calculated_metrics": additional_metrics,
                    "financial_summary": generate_financial_summary(financial_data)
                })
                
            elif analysis_type == "risk_comparison":
                # Existující logika pro risk analýzu
                # ...
                
            elif analysis_type == "supplier_analysis":
                # Existující logika pro supplier analýzu
                # ...
                
            else:  # general
                # Existující obecná logika
                # ...
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query_type": analysis_type if 'analysis_type' in locals() else "unknown",
            "analysis_complete": False,
            "query": query
        })

def calculate_financial_metrics(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vypočítá dodatečné finanční metriky.
    """
    metrics = financial_data.get("financial_metrics", {})
    revenue = metrics.get("revenue", {})
    
    # Výpočet růstu příjmů
    revenue_growth = None
    if "2023" in revenue and "2022" in revenue:
        revenue_growth = ((revenue["2023"] - revenue["2022"]) / revenue["2022"]) * 100
    
    # ROE odhad (zjednodušený)
    profit_margin = metrics.get("profit_margin", {}).get("2023", 0)
    debt_to_equity = metrics.get("debt_to_equity", 0)
    estimated_roe = profit_margin * (1 + debt_to_equity) if profit_margin else None
    
    return {
        "revenue_growth_2023": revenue_growth,
        "estimated_roe": estimated_roe,
        "liquidity_score": calculate_liquidity_score(metrics),
        "financial_strength": assess_financial_strength(metrics)
    }

def calculate_liquidity_score(metrics: Dict[str, Any]) -> float:
    """Vypočítá skóre likvidity na škále 0-100."""
    current_ratio = metrics.get("current_ratio", 1.0)
    quick_ratio = metrics.get("quick_ratio", 1.0)
    
    # Zjednodušené skóre
    liquidity_score = min(100, (current_ratio * 30) + (quick_ratio * 40))
    return round(liquidity_score, 2)

def assess_financial_strength(metrics: Dict[str, Any]) -> str:
    """Posoudí celkovou finanční sílu."""
    debt_to_equity = metrics.get("debt_to_equity", 0)
    current_ratio = metrics.get("current_ratio", 1.0)
    profit_margin = metrics.get("profit_margin", {}).get("2023", 0)
    
    if debt_to_equity < 0.3 and current_ratio > 1.5 and profit_margin > 0.1:
        return "excellent"
    elif debt_to_equity < 0.5 and current_ratio > 1.2 and profit_margin > 0.05:
        return "good"
    elif debt_to_equity < 0.7 and current_ratio > 1.0:
        return "fair" 
    else:
        return "weak"

def generate_financial_summary(financial_data: Dict[str, Any]) -> str:
    """Generuje textový souhrn finanční analýzy."""
    health = financial_data.get("financial_health", "unknown")
    rating = financial_data.get("credit_rating", "N/A")
    recommendations = financial_data.get("recommendations", [])
    
    summary = f"Finanční zdraví: {health}. Credit rating: {rating}."
    if recommendations:
        summary += f" Klíčová doporučení: {', '.join(recommendations[:2])}."
    
    return summary
```

### Krok 6: Testování nového typu

```python
# tests/test_financial_analysis.py

import json
from src.memory_agent.analyzer import analyze_company

def test_financial_analysis_detection():
    """Test detekce finančního typu analýzy."""
    queries = [
        "Jaká je finanční situace společnosti ADIS?",
        "Analýza výnosů a ziskovosti MB TOOL",
        "Financial performance of BOS Automotive",
        "Cash flow analysis for Flídr plast"
    ]
    
    for query in queries:
        result = analyze_company(query)
        data = json.loads(result)
        
        assert data["query_type"] == "financial_analysis"
        assert data["analysis_complete"] is True
        assert "financial_data" in data
        assert "calculated_metrics" in data

def test_financial_metrics_calculation():
    """Test výpočtu finančních metrik."""
    from src.memory_agent.analyzer import calculate_financial_metrics
    
    sample_data = {
        "financial_metrics": {
            "revenue": {"2023": 150000000, "2022": 135000000},
            "profit_margin": {"2023": 0.12},
            "debt_to_equity": 0.35,
            "current_ratio": 1.8,
            "quick_ratio": 1.2
        }
    }
    
    metrics = calculate_financial_metrics(sample_data)
    
    assert "revenue_growth_2023" in metrics
    assert metrics["revenue_growth_2023"] > 0  # Očekáváme růst
    assert "liquidity_score" in metrics
    assert 0 <= metrics["liquidity_score"] <= 100

if __name__ == "__main__":
    # Rychlý test
    test_queries = [
        "Finanční analýza ADIS TACHOV",
        "Revenue analysis for MB TOOL"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing: {query} ===")
        result = analyze_company(query)
        data = json.loads(result)
        print(f"Type detected: {data['query_type']}")
        print(f"Analysis complete: {data['analysis_complete']}")
        if 'financial_summary' in data:
            print(f"Summary: {data['financial_summary']}")
```

## Best practices pro nové typy analýz

### 1. Konzistentní struktura dat

Všechny typy analýz by měly vracet JSON se standardní strukturou:

```json
{
  "query_type": "your_analysis_type",
  "company_data": {...},
  "specific_data": {...},        // Data specifická pro typ
  "calculated_metrics": {...},   // Vypočítané metriky
  "summary": "...",              // Textový souhrn
  "analysis_complete": true,
  "query": "original query"
}
```

### 2. Error handling

```python
def robust_analysis_function(query: str) -> str:
    """Template s robustním error handlingem."""
    try:
        # Hlavní logika
        result = perform_analysis(query)
        return json.dumps(result, indent=2)
        
    except DataNotFoundError as e:
        # Specifické chyby
        return json.dumps({
            "error": "Data not available",
            "error_type": "data_missing",
            "query_type": "your_type",
            "analysis_complete": False,
            "query": query,
            "suggestions": ["Try different company name", "Check data availability"]
        })
        
    except Exception as e:
        # Obecné chyby
        logger.error(f"Unexpected error in analysis: {str(e)}")
        return json.dumps({
            "error": str(e),
            "error_type": "unexpected_error", 
            "query_type": "your_type",
            "analysis_complete": False,
            "query": query
        })
```

### 3. Mock data konvence

- **Naming**: `{type}_{company_id}.json`
- **Structure**: Konzistentní struktura napříč typy
- **Fallbacks**: Vždy poskytněte fallback data
- **Validation**: Validujte strukturu při načítání

### 4. Performance considerations

```python
# Cachování pro zlepšení výkonu
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_analysis_data(company_id: str, analysis_type: str) -> Dict[str, Any]:
    """Cachovaná verze načítání dat."""
    connector = MockMCPConnector()
    
    if analysis_type == "financial_analysis":
        return connector.get_financial_analysis_data(company_id)
    # Další typy...
```

## Deployment nového typu

### 1. Lokální testování

```bash
# Test nového typu
python -c "
from src.memory_agent.analyzer import analyze_company
result = analyze_company('Financial analysis of ADIS')
print(result)
"

# Test všech typů
python tests/test_financial_analysis.py
```

### 2. Přidání do CI/CD

```yaml
# .github/workflows/test.yml - přidání testu nového typu
- name: Test financial analysis type
  run: python tests/test_financial_analysis.py
```

### 3. Dokumentace

Aktualizujte dokumentaci:
- Přidejte nový typ do této dokumentace
- Aktualizujte hlavní README.md
- Přidejte example použití

### 4. Monitoring

Po nasazení sledujte:
- Úspěšnost detekce typu
- Performance metrik  
- Error rate pro nový typ
- User feedback

## Příklady použití

```python
# Testování různých dotazů pro finanční analýzu
queries = [
    "Jaká je finanční výkonnost společnosti ADIS TACHOV?",
    "Revenue trends for MB TOOL over last 3 years",
    "Debt to equity ratio analysis for BOS Automotive", 
    "Cash flow situation of Flídr plast",
    "Profitability analysis of ŠKODA AUTO suppliers"
]

for query in queries:
    result = analyze_company(query)
    print(f"Query: {query}")
    print(f"Result type: {json.loads(result)['query_type']}")
    print("---")
```

---

**Poznámka**: Tento návod předpokládá rozšíření současné zjednodušené implementace. Před implementací konzultujte s týmem o nejlepším přístupu pro vaše konkrétní požadavky.
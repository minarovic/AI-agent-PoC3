## [2025-05-18] - Oprava IndentationError v GitHub Action

### Identifikovaný problém:
- GitHub Action selhal s chybou: `IndentationError: unexpected indent`
- Chyba byla v řádku s definicí `is_company_analysis: bool = Field(description="Indicates whether the query is about company analysis")`
- Tento řádek byl nesprávně indentován v souboru `src/memory_agent/analyzer.py`

### Analýza příčiny:
- Při předchozích úpravách pro kompatibilitu s LangGraph Platform došlo k přesunu definice `AnalysisResult` do souboru `schema.py`
- V souboru `analyzer.py` zůstaly pozůstatky definice polí, které měly být součástí třídy `AnalysisResult`
- Tyto pozůstatky způsobovaly syntaktickou chybu kvůli nesprávné indentaci a absenci třídy, do které by patřily

### Navrhované řešení:
- [x] Odstranit nesprávně indentované řádky z `analyzer.py`
- [x] Přidat chybějící pole (`is_company_analysis` a `confidence`) do třídy `AnalysisResult` v `schema.py`

### Implementace:
1. Aktualizován soubor `src/memory_agent/schema.py`:
   - Přidáno pole `is_company_analysis: bool` do třídy `AnalysisResult`
   - Přidáno pole `confidence: float` s validátorem rozsahu do třídy `AnalysisResult`

2. Upraven soubor `src/memory_agent/analyzer.py`:
   - Odstraněny nesprávně indentované řádky obsahující definice polí `is_company_analysis` a `confidence`
   - Odstraněn nesprávně indentovaný řádek `model_config = {"extra": "forbid"}`

### Verifikace:
- Testováno lokálně pomocí flake8:
  ```bash
  flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
  ```
- Kód již neobsahuje chyby indentace a je syntakticky správný
- Očekáváme, že GitHub Action nyní proběhne úspěšně

### Další doporučení:
- Provést podrobnou kontrolu dalších souborů pro podobné zbytky kódu po přesunu definic
- Aktualizovat jednotkové testy pro ověření správnosti struktury a požadovaných polí v `AnalysisResult`
- Průběžně monitorovat logy z GitHub Action pro detekci podobných problémů

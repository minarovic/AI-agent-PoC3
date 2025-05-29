# Analýza N8N workflow a datových toků

## Typy analýz v N8N workflow

N8N workflow poskytuje tři hlavní typy analýz:

1. **Risk Comparison** - Analýza rizikových faktorů a compliance
2. **Supplier Analysis** (někde označeno jako "common_suppliers") - Analýza dodavatelských vztahů a struktury
3. **General** - Obecné informace o společnosti

## Workflow proces v N8N

### 1. Zpracování uživatelského dotazu
- Uživatel zadá dotaz ve formátu: "Název společnosti; typ_analýzy"
- Uzel `parse_user_query` extrahuje z dotazu:
  - Seznam společností (oddělených čárkou)
  - Typ analýzy (risk_comparison, supplier_analysis/common_suppliers, general)
  - Pokud typ analýzy není specifikován, defaultně se použije "general"

### 2. Příprava dat podle typu analýzy
Na základě detekovaného typu analýzy se aktivují různé části workflow:

#### Pro všechny typy analýz:
- `prepare_internal_data` - Načte základní interní data o společnosti
- `prepare_external_data` - Načte externí data o společnosti

#### Podmíněné větve:
- Pro analýzu vztahů (`supplier_analysis`):
  - `prepare_relationships` - Načte data o vztazích mezi společnostmi
  - `analyze_relationships` - Provede analýzu vztahů
- Pro analýzu bez vztahů:
  - `prepare_empty_relationships_data` - Vytvoří prázdnou strukturu pro vztahy

### 3. Analytické uzly
- `analyze_internal_data` - Analýza interních dat společnosti
- `analyze_external_risks` - Analýza externích rizik a compliance dat
- `analyze_relationships` - Analýza vztahů (aktivní pouze pro supplier_analysis)

### 4. Kombinace výsledků
- `combine_data_objects` - Sloučí všechny výsledky dohromady podle typu analýzy
  - Pro `risk_comparison` klade důraz na data z externích rizik
  - Pro `supplier_analysis` klade důraz na vztahová data
  - Pro `general` používá kombinaci všech základních informací

### 5. Generování odpovědi
- `generate_supervisor_prompt` - Vytvoří prompt pro finálního LLM agenta
- `Supervisor` (AI Agent) - Zpracuje všechna data a vygeneruje odpověď

## Mapování na data v mock_data_2

### Risk Comparison

**Používané datové soubory:**
- `entity_detail_[společnost].json` (primární zdroj) - Obsahuje detailní rizikové faktory
- `entity_search_[společnost].json` - Poskytuje základní kontext
- `internal_[společnost].json` (volitelně) - Doplňuje interní kontext

**Tok dat:**
1. Z entity_detail se extrahují rizikové faktory
2. Ty jsou analyzovány v kontextu entity_search
3. Výsledek je formátován s důrazem na rizika a compliance

### Supplier Analysis

**Používané datové soubory:**
- `relationships_[společnost].json` (primární zdroj) - Vztahy mezi entitami
- `supply_chain_[společnost].json` (primární zdroj) - Informace o dodavatelském řetězci
- `entity_detail_[společnost].json` - Kontext o jednotlivých entitách v řetězci

**Tok dat:**
1. Z relationships a supply_chain se extrahují vztahy a dodavatelský řetězec
2. Z entity_detail se doplní kontext o jednotlivých dodavatelích
3. Výsledek je formátován s důrazem na strukturu dodavatelského řetězce

### General

**Používané datové soubory:**
- `entity_search_[společnost].json` (primární zdroj) - Základní informace
- `entity_detail_[společnost].json` - Detailnější informace
- `internal_[společnost].json` - Interní informace

**Tok dat:**
1. Ze všech zdrojů se extrahují základní informace
2. Data jsou kombinována pro vytvoření komplexního přehledu
3. Výsledek je formátován jako obecný přehled o společnosti

## Nesoulad mezi současnými prompty a dostupnými daty

Současné prompty v projektu AI-agent-Ntier pravděpodobně nejsou optimalizovány pro efektivní využití dat z mock_data_2 adresáře, zejména:

1. **Nekonzistentní struktura** - Prompty mohou očekávat data v jiné struktuře, než je přítomna v mock souborech
2. **Chybějící mapování** - Nemusí existovat jasné mapování mezi typy analýz a příslušnými soubory
3. **Neoptimalizované zpracování** - Prompty mohou být příliš obecné a nespecializované pro konkrétní typy analýz

## Doporučení pro vylepšení

1. **Restrukturalizovat prompty** podle typu analýzy:
   - Risk comparison prompt - Specializovaný na zpracování dat z entity_detail a extrakci rizikových faktorů
   - Supplier analysis prompt - Specializovaný na zpracování vztahů a dodavatelského řetězce
   - General prompt - Flexibilní, schopný zpracovat základní informace z různých zdrojů

2. **Vytvořit jednoznačné mapování** mezi typy analýz a zdrojovými soubory

3. **Posílit robustnost** zpracování dat, aby si prompty poradily s různými formáty a strukturami v datech

# Testovací data pro Memory Agent PoC-2

Tento adresář obsahuje sadu testovacích dat simulujících Sayari API a interní data pro Memory Agent PoC-2.

## Struktura dat

Každá Tier 1 společnost má vlastní sadu souborů s konzistentními identifikátory napříč celou datovou sadou:

### Soubory pro každou společnost

1. **entity_search_[společnost].json**
   - Simuluje výsledky vyhledávání entity v Sayari API
   - Obsahuje základní informace o entitě (ID, typ, název, země, adresy, rizikové faktory)

2. **entity_detail_[společnost].json**
   - Simuluje detailní informace o entitě
   - Obsahuje rozšířené informace včetně detailů o riziku, metadata, popis

3. **relationships_[společnost].json**
   - Obsahuje dva formáty vztahů:
     - `data`: Jednodušší formát pro základní vztahy
     - `relationships`: Detailnější formát s atributy a reverzními atributy

4. **supply_chain_[společnost].json**
   - Simuluje dodavatelský řetězec
   - Obsahuje hierarchickou strukturu s cestami mezi entitami
   - Zahrnuje informace o produktech a HS kódech

5. **internal_[společnost].json**
   - Simuluje interní data o dodavateli
   - Obsahuje tier klasifikaci, HS kódy, obchodní aktivity

## ID systém

### Tier 1 společnosti
- entity_1001: MB TOOL s.r.o. (DUNS: 511391109)
- entity_1002: BOS AUTOMOTIVE (DUNS: 535010490) - závod DEU
- entity_1003: BOS AUTOMOTIVE (DUNS: 366035673) - závod CZE
- entity_1004: ADIS TACHOV, zp (DUNS: 361672367)
- entity_1005: Flídr plast s.r (DUNS: 495185217)

### Tier 2 dodavatelé
- entity_2001 - entity_2024: Různí Tier 2 dodavatelé s konzistentními ID

### Tier 3 dodavatelé
- entity_3001 - entity_3008: Tier 3 dodavatelé s konzistentními ID

## Typy analýz

Tato data umožňují testování různých typů analýz:

1. **Risk Comparison**: Analýza rizikových faktorů a jejich kontextu
2. **Supplier Analysis**: Analýza dodavatelských vztahů a struktury
3. **Combined Analysis**: Komplexní pohled zahrnující rizika, vztahy a interní data

## Použití v Memory Agentovi

Pro použití těchto dat v Memory Agentovi je potřeba:

1. Upravit MockMCPConnector pro načítání těchto testovacích dat místo interních pevně zakódovaných hodnot
2. Implementovat logiku výběru správných dat podle typu analýzy
3. Zajistit konzistentní zpracování dat napříč celým workflow

Všechna data jsou vytvořena s konzistentními identifikátory a strukturou, což umožňuje jejich plynulou integraci do stávajícího kódu.
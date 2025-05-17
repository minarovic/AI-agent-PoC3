# Mock Data pro Memory Agent PoC

Tento adresář obsahuje simulovaná testovací data pro použití s MockMCPConnector. Data jsou organizována podle typů:

## Struktura adresářů

- `companies/` - Data o společnostech (informace o firmách, rizikové faktory, atd.)
- `people/` - Data o osobách (představitelé firem, klíčoví stakeholdeři, atd.)
- `relationships/` - Data o vztazích mezi entitami (dodavatelské vztahy, vlastnické vztahy, atd.)
- `internal_data/` - Interní data o společnostech (tier klasifikace, HS kódy, atd.)

## Formát dat

Všechna data jsou uložena ve formátu JSON s konzistentní strukturou podle typu entity.

### Příklad dat o společnosti

```json
{
  "id": "company-123",
  "label": "BOS",
  "type": "company",
  "metadata": {
    "industry": "Automotive",
    "founded": "1991"
  },
  "risk_score": "25",
  "risk_factors": {
    "sanctioned_entity": false,
    "pep_connection": true
  }
}
```

## Použití s MockMCPConnector

MockMCPConnector používá tato data pro simulaci API volání:

```python
connector = MockMCPConnector(data_root="./mock_data")
company_data = await connector.fetch_company("BOS")
internal_data = await connector.fetch_internal_data("BOS")
```

## Rozšíření testovacích dat

Pro rozšíření testovacích dat stačí přidat nové JSON soubory do příslušných adresářů.

# Implementační plán pro lepší podporu typů analýz

## Přehled změn

Na základě provedené analýzy dat v mock_data_2 a N8N workflow implementujeme tři klíčové změny:

1. **Rozpoznávání typů analýz**
   - Přidání funkce `determine_analysis_type` pro detekci typu analýzy z dotazu
   - Úprava `route_query` pro propagaci typu analýzy do stavu

2. **Načítání dat podle typu analýzy**
   - Aktualizace `retrieve_additional_company_data` pro načítání dat z příslušných souborů
   - Mapování typů analýz na různé soubory v mock_data_2

3. **Specializované zpracování podle typu analýzy**
   - Úprava `analyze_company_data` pro specializované analýzy podle typu
   - Přizpůsobení výstupu analýzy na základě jejího typu

## Implementační plán

### Fáze 1: Rozpoznávání typů analýz
- [x] Vytvořit dokumentaci a diagramy workflow (N8N_analyzy.md, workflow diagramy)
- [ ] Implementovat funkci `determine_analysis_type` v graph_nodes.py
- [ ] Upravit `route_query` pro volání `determine_analysis_type`
- [ ] Přidat testy pro ověření správné detekce typů analýz

### Fáze 2: Načítání dat podle typu analýzy
- [ ] Implementovat mapování typů analýz na soubory v mock_data_2
- [ ] Upravit `retrieve_additional_company_data` pro načítání specifických dat
- [ ] Zajistit robustní zpracování chyb při načítání dat
- [ ] Přidat podporu pro kombinování dat z více zdrojů

### Fáze 3: Specializované zpracování
- [ ] Upravit `analyze_company_data` pro různé typy analýz
- [ ] Implementovat specializované analyzátory pro každý typ
- [ ] Přizpůsobit výstupy analýz pro různé typy dotazů
- [ ] Přidat podporu pro kombinování různých typů analýz

## Sledování změn

Pro každou změnu budeme sledovat:
1. Implementaci změny
2. Lokální testování funkčnosti
3. Verifikaci s použitím `verify_deployment.sh`
4. Nasazení přes `deploy_to_github.sh`
5. Ověření funkčnosti v LangGraph Platform

## Harmonogram

1. Implementace Fáze 1: 2 hodiny
2. Testování Fáze 1: 1 hodina
3. Implementace Fáze 2: 3 hodiny
4. Testování Fáze 2: 1 hodina
5. Implementace Fáze 3: 2 hodiny
6. Testování Fáze 3: 1 hodina
7. Finální nasazení a verifikace: 2 hodiny

Celkový čas: ~12 hodin

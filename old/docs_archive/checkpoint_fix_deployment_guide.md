# Příprava nástroje pro kontrolu nasazení na LangGraph Platform

Tento soubor obsahuje postup pro nasazení opravy problému s checkpointy v Memory Agent na GitHub a následně na LangGraph Platform.

## 1. Příprava opravy pro nasazení

Oprava problému s checkpointy je připravena k nasazení prostřednictvím skriptu `deploy_checkpoint_fix_to_github.sh`. Tento skript:
1. Vytvoří novou větev `fix/checkpoint-serialization`
2. Spustí testy ověřující funkčnost opravy
3. Přidá do commitu pouze relevantní soubory spojené s opravou
4. Odešle změny na GitHub

## 2. Soubory zahrnuté v opravě

Oprava zahrnuje úpravy následujících souborů:

- `src/memory_agent/state.py` - Úprava funkce `merge_dict_values` pro robustní zpracování objektů bez metody `copy()`
- `src/memory_agent/graph_nodes.py` - Odstranění ukládání instance `MockMCPConnector` do stavu
- `test_checkpoint_fix.py` - Testovací skript pro ověření funkčnosti opravy
- `deploy_logs/checkpoint_mcp_connector_fix.md` - Dokumentace provedených změn

## 3. Implementované změny

Hlavní úpravy:

1. **V souboru `state.py`**: Přidání ochrany proti chybějící metodě `copy()`:
   ```python
   if left is None:
       result = {}
   else:
       try:
           result = left.copy()
       except AttributeError:
           # Pokud objekt nemá metodu copy(), vytvoříme nový slovník
           result = {}
           logger.warning(f"Objekt typu {type(left)} nemá metodu copy(), vytvářím nový slovník")
   ```

2. **V souboru `graph_nodes.py`**: Odstranění ukládání instance `MockMCPConnector` do stavu:
   ```python
   # Ukládáme pouze základní data do state (bez MCP konektoru, který není serializovatelný)
   return {
       "company_name": company_name,
       "analysis_type": analysis_type,
       "company_data": company_data
       # NEUKLÁDAT mcp_connector do state - není serializovatelný pro checkpointy
   }
   ```

3. **V souboru `graph_nodes.py`**: Vytváření nové instance `MockMCPConnector`:
   ```python
   # Vždy vytvoříme novou instanci MockMCPConnector - neukládáme ji do stavu
   from memory_agent.tools import MockMCPConnector
   logger.info("Vytvářím novou instanci MockMCPConnector")
   mcp_connector = MockMCPConnector()
   ```

## 4. Postup nasazení na LangGraph Platform

Jakmile je kód odeslán na GitHub:

1. Vytvoříme Pull Request z větve `fix/checkpoint-serialization` do hlavní větve
2. Po schválení a sloučení PR přejdeme do administrace LangGraph Platform
3. Propojíme GitHub repozitář s projektem na LangGraph Platform
4. Nastavíme automatické nasazení při push do hlavní větve

## 5. Ověření nasazení na LangGraph Platform

Po nasazení je potřeba ověřit funkčnost:

1. Zkontrolovat, zda aplikace správně startuje
2. Otestovat komunikaci s Memory Agentem ve více konverzacích
3. Ověřit zachování kontextu mezi voláními pomocí stejného `thread_id`

## 6. Monitorování v produkci

Po nasazení je vhodné monitorovat:
1. Chybové logy spojené s checkpointy
2. Využití databáze pro ukládání checkpointů
3. Konzistenci odpovědí v dlouhodobých konverzacích

## 7. Spuštění nasazení

Pro odeslání opravy na GitHub spusťte:

```bash
./deploy_checkpoint_fix_to_github.sh
```

Tento příkaz připraví a odešle opravu na GitHub.

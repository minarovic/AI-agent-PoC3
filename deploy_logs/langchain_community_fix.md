# Řešení chyby s chybějícím modulem langchain_community

## Identifikovaný problém
Při nasazení aplikace AI-agent-Ntier na LangGraph Platform se objevila chyba:

```
ModuleNotFoundError: No module named 'langchain_community'
```

Tato chyba vzniká v souboru `/deps/AI-agent-PoC3/src/memory_agent/graph.py` při importu:

```python
from langchain.chat_models import ChatOpenAI
```

## Analýza
1. Novější verze LangChain knihovny rozdělila původně monolitickou `langchain` do několika specializovaných balíčků
2. Kód využívá import z původního umístění v `langchain`, ale ten interně potřebuje `langchain_community`
3. V kontejneru pro LangGraph Platform není `langchain_community` balíček nainstalován

## Implementované řešení

1. **Přidání závislosti do requirements.txt**
   ```
   langchain_community>=0.1.0
   ```

2. **Aktualizace GitHub Actions workflow** - přidána explicitní instalace balíčku:
   ```yaml
   pip install langchain_community  # Přidáváme chybějící závislost
   ```

3. **Vytvoření requirements-platform.txt** - speciálně pro LangGraph Platform:
   ```
   langchain_community>=0.1.0
   ```

4. **Aktualizace langgraph.json** - aby zahrnoval dodatečné závislosti:
   ```json
   "dependencies": [".", "./requirements-platform.txt"]
   ```

## Důvod zvoleného řešení
Tento přístup s oddělením požadavků do dvou souborů byl zvolen, protože:

1. Zachováváme původní requirements.txt pro lokální vývoj
2. Přidáváme specifické požadavky pro nasazení v souboru requirements-platform.txt
3. LangGraph Platform build process nainstaluje oboje díky konfiguraci v langgraph.json

Díky tomuto přístupu by měl být proces nasazení robustnější vůči změnám v závislostech knihovny LangChain.

Na základě poskytnutých zdrojů a naší konverzace zde uvádím, co je nezbytné pro fungování AI agenta na platformě LangGraph (konkrétně LangGraph Studio) a další důležité informace pro Copilot Agent.

**Co musí být v kódu, aby jakýkoliv AI agent fungoval na platformě LangGraph Studio:**

Aby bylo možné agenta vizualizovat a ladit v LangGraph Studiu, musí být jeho základní struktura definována pomocí knihovny `langgraph` v Pythonu (nebo JavaScriptu). K tomu jsou nezbytné následující komponenty:

*   **Definice grafu pomocí `StateGraph`**: Základní architektura agenta je definována pomocí třídy `StateGraph` z knihovny `langgraph.graph`. `StateGraph` slouží jako framework pro navrhování a správu toku úloh.
*   **Definice schématu stavu (`State Schema`)**: Musí být definována sdílená datová struktura (`State`) (často pomocí `TypedDict` nebo Pydantic `BaseModel`), která uchovává kontext a informace agenta během jeho běhu. Tato struktura drží veškeré informace, jak aplikace běží. Běžným vzorem pro konverzační agenty je použití `MessagesState` s klíčem `messages`, často s redukcí `add_messages` pro slučování zpráv.
*   **Přidání uzlů (`Nodes`)**: Graf musí obsahovat uzly, které představují jednotlivé kroky nebo akce agenta. Uzly jsou typicky implementovány jako Python funkce, které přijímají aktuální stav (`State`) jako vstup a vracejí aktualizace stavu. Příkladem je uzel pro volání LLM (`model_call`) nebo uzel pro volání nástrojů (`ToolNode`).
*   **Definice hran (`Edges`)**: Musí být definovány hrany, které propojují uzly a určují tok řízení v grafu. To zahrnuje přímé hrany (`add_edge`) a podmíněné hrany (`add_conditional_edges`), které umožňují dynamické směrování na základě výsledku uzlu nebo stavu.
*   **Nastavení vstupního bodu (`Entry Point`)**: Musí být definováno, kde graf začíná (`set_entry_point(START)`).
*   **Kompilace grafu**: Vytvořený graf musí být zkompilován pomocí metody `.compile()`. Tím se vytvoří spustitelná aplikace (`app` nebo `agent`).
*   **Integrace s LangChain**: Ačkoliv je LangGraph samostatná knihovna, je postavená na LangChain a využívá její komponenty, zejména pro práci s LLM, zprávami a nástroji. Použití tříd jako `ChatOpenAI`, `HumanMessage`, `AIMessage`, `SystemMessage`, `ToolCall` a `ToolNode` je běžné a LangGraph s nimi počítá. LLM musí podporovat volání nástrojů, pokud je agent používá. Nástroje se k LLM přiřazují pomocí `.bind_tools()`.
*   **Volání nástrojů (pokud agent používá nástroje)**: Funkce představující nástroje by měly být označené dekorátorem `@tool`.

**Důležité doplňkové informace pro kontrolu a ověření (pro Copilot Agent):**

*   **Role LangGraph Studia**: LangGraph Studio je **specializované IDE pro vizualizaci toku grafu a ladění spuštění agentů**, které jste nakódovali. **Není to nástroj pro psaní základní logiky agenta**.
*   **Vizualizace a ladění ve Studiu**: Studio zobrazuje strukturu grafu a umožňuje **sledovat spuštění kro za krokem**, vizualizovat, jak se **stav agenta (`State`) aktualizuje v každém uzlu**, a ladit.
*   **LangSmith integrace**: LangGraph Studio se typicky integruje s LangSmith pro detailní trasování a analýzu spuštění agenta. Trasování v LangSmith ukazuje kompletní cestu exekuce a interakce.
*   **Assistants a Versions**: LangGraph Studio umožňuje vytvořit z jedné základní architektury grafu různé *Assistenty* (konfigurace agenta, např. výběr LLM modelu, dostupné nástroje, systémový prompt) a spravovat jejich *Versions*. To umožňuje **rapidní testování a iteraci s různými konfiguracemi bez změny základního kódu grafu**.
*   **Docstringy pro nástroje**: **Docstringy u funkcí označených `@tool` jsou klíčové**. Poskytují LLM popis funkce nástroje a informují ho o tom, k čemu nástroj slouží a jak ho použít. Bez nich nemusí graf fungovat správně.
*   **Typy zpráv**: Rozumět různým typům zpráv (`HumanMessage`, `AIMessage`, `SystemMessage`, `ToolMessage`, `ToolCall`, `BaseMessage`) je důležité. Zejména `SystemMessage` se používá k poskytnutí instrukcí nebo role LLM. Reducer `add_messages` automaticky spravuje přidávání zpráv do stavu.
*   **Podmíněné hrany a rozhodovací funkce**: Použití podmíněných hran s Python funkcemi pro rozhodování je základem dynamického toku v grafu (např. kontrola, zda LLM volal nástroj, a podle toho rozhodnutí, kam dále směřovat).
*   **Paměť/Persistence**: Pro udržení konverzace napříč spuštěními je důležité implementovat persistenci stavu, často pomocí `checkpointeru` (např. `SqliteSaver`) při kompilaci grafu. Studio může zobrazit data uložená v checkpointeru.
*   **Hierarchické/Multi-agent systémy**: LangGraph podporuje komplexnější architektury, jako jsou systémy s nadřazeným agentem (supervisor) a podřízenými agenty, s mechanismy předávání informací (handoffs) a děděním historie zpráv.
*   **Prompting Reasoning Modelů**: Při použití speciálních "reasoning" modelů (jako o3/o4-mini nebo Claude 3.7) je třeba pamatovat, že se promptují odlišně od chat modelů – zaměřuje se spíše na zadání úkolu ("tell it what you want") a poskytnutí kontextu, než na explicitní popis postupu myšlení ("don't tell it how to think"). Claude 3.7 může navíc explicitně odhalit proces svého "myšlení" ("thinking block") a umožňuje nastavit rozpočet pro toto myšlení ("thinking budget").

Doufám, že tyto instrukce pomohou Copilot Agentovi lépe pochopit kontext a požadavky pro tvorbu kódu agenta pro LangGraph Studio.

# Kontrola souborů
import json

# Načtu langgraph.json
with open('langgraph.json', 'r') as f:
    config = json.load(f)
    print("Aktuální langgraph.json:")
    print(json.dumps(config, indent=2))

# Zkontroluju, co je v graph.py
with open('src/memory_agent/graph.py', 'r') as f:
    content = f.read()
    # Hledám název grafu
    if 'memory_agent = StateGraph' in content:
        print("\n✅ Graf se jmenuje 'memory_agent'")
    elif 'graph = StateGraph' in content:
        print("\n❌ Graf se jmenuje 'graph'")
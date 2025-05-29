# Příklady implementace pro LangGraph Platform

Tento dokument obsahuje příklady kódu, které demonstrují implementaci klíčových funkcionalit pro kompatibilitu s LangGraph Platform.

## 1. State jako Pydantic BaseModel

```python
# Implementace pomocí Pydantic BaseModel
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class State(BaseModel):
    """State pro StateGraph workflow s typovou bezpečností a serializací."""
    messages: List[BaseMessage] = Field(default_factory=list)
    company_analysis: Dict[str, Any] = Field(default_factory=dict)
    company_data: Optional[Dict[str, Any]] = Field(default=None)
    internal_data: Optional[Dict[str, Any]] = Field(default=None)
    relationships_data: Optional[Dict[str, Any]] = Field(default=None)
    original_query: str = Field(default="")
    current_step: str = Field(default="initialized")
    error: Optional[str] = Field(default=None)
```

## 2. Explicitní input/output schémata

```python
# Explicitní definice vstupních a výstupních typů
class InputState(TypedDict):
    """Vstupní stav pro agenta."""
    messages: List[BaseMessage]
    original_query: str

class OutputState(TypedDict):
    """Výstupní stav agenta."""
    messages: List[BaseMessage]
    error: Optional[str]

# Použití v definici grafu
workflow = StateGraph(State, input=InputState, output=OutputState)
```

## 3. Vrácení přímých aktualizací stavu

```python
# Přímé vrácení aktualizace stavu
async def analyze_company_input(state: State) -> Dict[str, Any]:
    """Analyzuje uživatelský dotaz a identifikuje společnosti a typ analýzy."""
    try:
        # Získání vstupního dotazu
        query = state.get("original_query", "")
        
        # Analýza dotazu pomocí Analyzeru
        result = await analyze_query(query)
        
        # Převod výsledku na slovník pro aktualizaci stavu
        company_analysis = {
            "companies": result.companies,
            "company": result.company,
            "analysis_type": result.analysis_type,
            "is_company_analysis": result.is_company_analysis,
            "confidence": result.confidence,
            "query": result.query
        }
        
        # Vrácení přímé aktualizace stavu
        return {
            "company_analysis": company_analysis,
            "current_step": "analyzed_input"
        }
    except Exception as e:
        # Zpracování chyby
        logger.error(f"Error analyzing input: {str(e)}")
        return {
            "error": f"Error analyzing input: {str(e)}",
            "current_step": "error_analyzing_input"
        }
```

## 4. Detekce chyb pomocí funkce podmínění

```python
# Funkce pro detekci chybového stavu
def is_error_state(state: State) -> Literal["error", "success"]:
    """Určuje, zda stav obsahuje chybu."""
    return "error" if state.get("error") is not None else "success"

# Použití v podmíněné hraně
workflow.add_conditional_edges(
    "analyze_company_input",
    is_error_state,
    {
        "error": "handle_error",
        "success": None  # Pokračuje podle předchozí podmíněné hrany
    }
)
```

## 5. Exportování grafu pro LangGraph Platform

```python
# Vytvoření hlavního grafu
def build_company_analysis_graph() -> Graph:
    # ...definice grafu...
    return workflow.compile()

# Export grafu pro LangGraph Platform
graph = build_company_analysis_graph()
```

## 6. Langgraph.json konfigurace

```json
{
    "graphs": {
        "agent": "./src/memory_agent/graph.py:graph"
    },
    "env": ".env",
    "python_version": "3.11",
    "dependencies": ["."]
}
```

## 7. Specializované prompty pro různé typy analýz

```python
# Implementace PromptRegistry
class PromptRegistry:
    """Centralizovaný registr specializovaných promptů pro analýzy."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Implementace Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(PromptRegistry, cls).__new__(cls)
            cls._instance.prompts = {}
            cls._instance._initialize_default_prompts()
        return cls._instance
    
    def get_prompt(self, analysis_type: str) -> ChatPromptTemplate:
        """Získá prompt pro specifikovaný typ analýzy."""
        return self.prompts.get(analysis_type, self.prompts.get("general"))
    
    def _initialize_default_prompts(self) -> None:
        """Inicializuje výchozí prompty pro všechny typy analýz."""
        
        # Risk Comparison Prompt
        self.prompts["risk_comparison"] = ChatPromptTemplate.from_template(
            """Analyzuj rizikové faktory pro společnost {company}.
            
            Externí data:
            {external_data}
            
            Interní data:
            {internal_data}
            
            Vztahy:
            {relationships_data}
            
            Zaměř se na sankce, compliance problémy a rizikové faktory.
            Poskytni strukturovanou analýzu rizik."""
        )
        
        # Supplier Analysis Prompt
        self.prompts["supplier_analysis"] = ChatPromptTemplate.from_template(
            """Analyzuj dodavatelské vztahy pro společnost {company}.
            
            Externí data:
            {external_data}
            
            Interní data:
            {internal_data}
            
            Vztahy:
            {relationships_data}
            
            Zaměř se na dodavatele a dodavatelský řetězec.
            Poskytni strukturovanou analýzu dodavatelského řetězce."""
        )
        
        # General Analysis Prompt
        self.prompts["general"] = ChatPromptTemplate.from_template(
            """Analyzuj následující informace o společnosti {company}.
            
            Externí data:
            {external_data}
            
            Interní data:
            {internal_data}
            
            Vztahy:
            {relationships_data}
            
            Poskytni vyváženou a strukturovanou analýzu."""
        )
```

## 8. Základní zpracování chyb

```python
def handle_error(state: State) -> Dict[str, Any]:
    """Zpracovává chyby ve workflow."""
    error = state.get("error", "Neznámá chyba")
    logger.error(f"Workflow error: {error}")
    
    # Vytvoření chybové zprávy pro uživatele
    error_message = AIMessage(
        content=f"Omlouvám se, při zpracování dotazu došlo k chybě: {error}"
    )
    
    return {
        "messages": [error_message],
        "current_step": "error_handled"
    }
```
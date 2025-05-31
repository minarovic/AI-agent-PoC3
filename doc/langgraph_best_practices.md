# LangGraph Best Practices pro Memory Agent

Tento návod shrnuje osvědčené postupy pro vývoj a údržbu Memory Agent aplikace postavené na LangGraph Platform.

## Obsah

1. [LangGraph vzory a architektury](#langgraph-vzory-a-architektury)
2. [State management](#state-management)  
3. [Tools a funkce](#tools-a-funkce)
4. [Error handling a resilience](#error-handling-a-resilience)
5. [Performance optimization](#performance-optimization)
6. [Security best practices](#security-best-practices)
7. [Testing strategies](#testing-strategies)
8. [Monitoring a debugging](#monitoring-a-debugging)

## LangGraph vzory a architektury

### React Agent pattern

Memory Agent používá `create_react_agent` vzor, který poskytuje:

```python
# Doporučená struktura
from langgraph.prebuilt import create_react_agent

def create_optimized_agent():
    """Optimální konfigurace pro produkční použití."""
    
    # 1. Model konfigurace
    model = "openai:gpt-4"  # String syntax je preferována
    
    # 2. Tools s jasnou odpovědností
    tools = [
        analyze_company,        # Hlavní analytický nástroj
        # validate_query,       # Validace vstupu (volitelné)
        # get_help_info,        # Nápověda (volitelné)
    ]
    
    # 3. Optimalizovaný prompt
    prompt = create_system_prompt()
    
    # 4. Robustní checkpointer
    checkpointer = create_production_checkpointer()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=prompt,
        checkpointer=checkpointer
    )
    
    return agent

def create_system_prompt() -> str:
    """Vytvoří optimalizovaný system prompt."""
    return """You are a business intelligence assistant specializing in company analysis.

Key guidelines:
- Always use the analyze_company tool for company-related queries
- Provide structured, data-driven responses
- If data is unavailable, clearly state limitations
- Focus on actionable insights
- Maintain professional tone

Available analysis types:
- General company information
- Risk and compliance analysis  
- Supplier relationship analysis

Format responses clearly with relevant data points and conclusions."""
```

### Custom graph patterns (pro pokročilé případy)

Pokud potřebujete více kontroly nad workflow:

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver

def create_custom_workflow():
    """Custom workflow pro komplexní analýzy."""
    
    # Definice workflow grafu
    workflow = StateGraph(State)
    
    # Přidání uzlů
    workflow.add_node("validate_input", validate_input_node)
    workflow.add_node("determine_type", determine_analysis_type_node) 
    workflow.add_node("analyze_data", analyze_data_node)
    workflow.add_node("generate_response", generate_response_node)
    
    # Definice přechodů
    workflow.set_entry_point("validate_input")
    workflow.add_edge("validate_input", "determine_type")
    workflow.add_edge("determine_type", "analyze_data")
    workflow.add_edge("analyze_data", "generate_response")
    
    # Conditional routing (pokud potřeba)
    workflow.add_conditional_edges(
        "determine_type",
        route_by_analysis_type,
        {
            "general": "analyze_data",
            "risk": "analyze_risk_data", 
            "supplier": "analyze_supplier_data"
        }
    )
    
    return workflow.compile(checkpointer=InMemorySaver())
```

## State management

### Optimální State struktura

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from typing_extensions import Annotated
from langgraph.graph import add_messages

@dataclass(kw_only=True)
class OptimizedState:
    """Optimalizovaná struktura stavu pro Memory Agent."""
    
    # Základní komunikace
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Hlavní data s reducery
    company_data: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    analysis_result: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    
    # Metadata a konfigurace
    current_query: Optional[str] = None
    analysis_type: Optional[str] = None
    query_timestamp: Optional[str] = None
    
    # Error handling
    error_state: Dict[str, Any] = field(default_factory=dict)
    
    # Performance tracking
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
```

### State reducers

```python
def merge_dict_values(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimalizovaný reducer pro slovníky.
    """
    if not right:
        return left or {}
    
    if not left:
        return right.copy() if hasattr(right, 'copy') else dict(right)
    
    # Deep merge pro vnořené struktury
    result = left.copy() if hasattr(left, 'copy') else dict(left)
    
    for key, value in right.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict_values(result[key], value)
        else:
            result[key] = value
    
    return result

def merge_performance_metrics(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Speciální reducer pro performance metriky."""
    if not right:
        return left or {}
    
    result = left.copy() if left else {}
    
    # Akumulace časů
    if "execution_time" in right:
        result["total_execution_time"] = result.get("total_execution_time", 0) + right["execution_time"]
        result["step_count"] = result.get("step_count", 0) + 1
    
    # Merge ostatních metrik
    result.update(right)
    return result
```

## Tools a funkce

### Optimální struktura tools

```python
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def performance_monitor(func):
    """Dekorátor pro monitoring výkonu tools."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

def error_handler(func):
    """Dekorátor pro konzistentní error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            # Vrátit strukturovanou chybu místo raise
            return json.dumps({
                "error": str(e),
                "error_type": type(e).__name__,
                "function": func.__name__,
                "analysis_complete": False,
                "timestamp": time.time()
            })
    return wrapper

@performance_monitor
@error_handler
def analyze_company(query: str) -> str:
    """
    Optimalizovaná verze analýzy společnosti.
    """
    logger.info(f"Starting analysis for query: {query[:50]}...")
    
    try:
        # Input validation
        if not query or not query.strip():
            raise ValueError("Empty query provided")
        
        # Inicializace
        connector = MockMCPConnector()
        start_time = time.time()
        
        # Hlavní logika
        company_data = connector.get_company_by_name(query)
        
        if not company_data:
            return json.dumps({
                "query_type": "company",
                "company_data": None,
                "analysis_complete": True,
                "message": "No company data found for the query",
                "query": query,
                "execution_time": time.time() - start_time
            })
        
        # Rozšířené načítání dat
        company_id = company_data.get("id")
        additional_data = {}
        
        if company_id:
            # Paralelní načítání různých typů dat
            additional_data = load_additional_data(connector, company_id)
        
        # Strukturovaný výsledek
        result = {
            "query_type": "company",
            "company_data": company_data,
            "additional_data": additional_data,
            "analysis_complete": True,
            "query": query,
            "execution_time": time.time() - start_time,
            "timestamp": time.time()
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        # Error už je zpracována dekorátorem
        raise

def load_additional_data(connector: MockMCPConnector, company_id: str) -> Dict[str, Any]:
    """
    Načte dodatečná data s error handling pro každý typ.
    """
    additional_data = {}
    
    # Financial data
    try:
        additional_data["financial"] = connector.get_company_financials(company_id)
    except Exception as e:
        logger.warning(f"Financial data not available for {company_id}: {str(e)}")
        additional_data["financial"] = {"error": "Not available"}
    
    # Relationships
    try:
        additional_data["relationships"] = connector.get_company_relationships(company_id)
    except Exception as e:
        logger.warning(f"Relationships data not available for {company_id}: {str(e)}")
        additional_data["relationships"] = {"error": "Not available"}
    
    return additional_data
```

### Tool validation

```python
from pydantic import BaseModel, Field, validator

class CompanyQueryInput(BaseModel):
    """Validace vstupu pro company queries."""
    query: str = Field(..., min_length=1, max_length=1000)
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        
        # Základní sanitizace
        v = v.strip()
        
        # Check for suspicious patterns
        suspicious_patterns = ['<script', 'javascript:', 'sql injection']
        if any(pattern in v.lower() for pattern in suspicious_patterns):
            raise ValueError('Invalid query content')
            
        return v

def validated_analyze_company(query: str) -> str:
    """Verze s Pydantic validací."""
    # Validace vstupu
    try:
        input_data = CompanyQueryInput(query=query)
        validated_query = input_data.query
    except ValueError as e:
        return json.dumps({
            "error": f"Input validation failed: {str(e)}",
            "error_type": "validation_error",
            "analysis_complete": False,
            "query": query
        })
    
    # Pokračovat s validovaným query
    return analyze_company(validated_query)
```

## Error handling a resilience

### Retry mechanismus

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=60.0):
    """
    Retry dekorátor s exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Exponential backoff s jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)
                    sleep_time = delay + jitter
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
            
            # Všechny pokusy selhaly
            logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator

# Použití
@retry_with_backoff(max_retries=2, base_delay=0.5)
def load_company_data(company_id: str) -> Dict[str, Any]:
    """Načte data společnosti s retry mechanimu."""
    connector = MockMCPConnector()
    return connector.get_company_by_name(company_id)
```

### Circuit breaker pattern

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker pro external dependencies.
    """
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Vykoná funkci přes circuit breaker."""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Zkontroluje, zda je čas na pokus o reset."""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Resetuje circuit breaker po úspěchu."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Zaznamenává selhání."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Globální circuit breaker instance
data_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

def robust_data_loading(company_id: str) -> Dict[str, Any]:
    """Načítání dat s circuit breaker ochranou."""
    def _load_data():
        connector = MockMCPConnector()
        return connector.get_company_by_name(company_id)
    
    try:
        return data_circuit_breaker.call(_load_data)
    except Exception as e:
        logger.error(f"Data loading failed (circuit breaker): {str(e)}")
        # Vrátit fallback data
        return {
            "id": company_id,
            "name": "Data temporarily unavailable",
            "error": "Service temporarily unavailable",
            "fallback": True
        }
```

## Performance optimization

### Caching strategies

```python
from functools import lru_cache
import time
import threading

class TimedCache:
    """
    Cache s TTL (time-to-live).
    """
    
    def __init__(self, ttl_seconds=300):  # 5 minut default
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.Lock()
    
    def get(self, key):
        """Získá hodnotu z cache."""
        with self.lock:
            if key in self.cache:
                if time.time() - self.timestamps[key] < self.ttl_seconds:
                    return self.cache[key]
                else:
                    # Vypršela TTL
                    del self.cache[key]
                    del self.timestamps[key]
            return None
    
    def set(self, key, value):
        """Uloží hodnotu do cache."""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self):
        """Vymaže cache."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

# Globální cache instance
company_cache = TimedCache(ttl_seconds=600)  # 10 minut

def cached_get_company_data(company_id: str) -> Dict[str, Any]:
    """Cachovaná verze načítání company dat."""
    
    # Pokus o načtení z cache
    cached_data = company_cache.get(company_id)
    if cached_data:
        logger.info(f"Company data for {company_id} loaded from cache")
        return cached_data
    
    # Načtení z datového zdroje
    connector = MockMCPConnector()
    data = connector.get_company_by_name(company_id)
    
    # Uložení do cache
    if data:
        company_cache.set(company_id, data)
        logger.info(f"Company data for {company_id} cached")
    
    return data
```

### Async operations (pokud potřeba)

```python
import asyncio
import aiofiles
import json

async def async_load_company_data(company_id: str) -> Dict[str, Any]:
    """Asynchronní načítání company dat."""
    
    file_path = f"mock_data_2/{company_id}.json"
    
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return {"error": "Company not found", "company_id": company_id}

async def parallel_data_loading(company_ids: List[str]) -> Dict[str, Any]:
    """Paralelní načítání dat pro více společností."""
    
    tasks = [async_load_company_data(company_id) for company_id in company_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Zpracování výsledků
    combined_results = {}
    for company_id, result in zip(company_ids, results):
        if isinstance(result, Exception):
            combined_results[company_id] = {"error": str(result)}
        else:
            combined_results[company_id] = result
    
    return combined_results
```

## Security best practices

### Input sanitization

```python
import re
import html
from typing import Any

def sanitize_input(input_data: Any) -> str:
    """
    Sanitizuje uživatelský vstup.
    """
    if not isinstance(input_data, str):
        input_data = str(input_data)
    
    # HTML escape
    sanitized = html.escape(input_data)
    
    # Odstranění potenciálně nebezpečných znaků
    sanitized = re.sub(r'[<>"\'\{\}]', '', sanitized)
    
    # Omezení délky
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()

def validate_company_query(query: str) -> bool:
    """
    Validuje company query z bezpečnostního hlediska.
    """
    if not query or len(query.strip()) == 0:
        return False
    
    # Kontrola délky
    if len(query) > 1000:
        return False
    
    # Blacklist patterns
    blacklist_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'expression\s*\(',
        r'@import',
        r'\.\./',
        r'\\.\\.\\',
    ]
    
    query_lower = query.lower()
    for pattern in blacklist_patterns:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return False
    
    return True
```

### Secrets management

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class SecureConfig:
    """
    Bezpečná konfigurace s validací.
    """
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Načte konfiguračí z environment variables."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY") 
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        
        # Validace kritických klíčů
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def validate_api_keys(self) -> bool:
        """Validuje formát API klíčů."""
        if self.openai_api_key and not self.openai_api_key.startswith('sk-'):
            return False
        
        return True

# Globální konfigurace
try:
    config = SecureConfig()
    if not config.validate_api_keys():
        raise ValueError("Invalid API key format")
except Exception as e:
    logger.error(f"Configuration error: {str(e)}")
    # Fallback nebo graceful degradation
    config = None
```

## Testing strategies

### Unit testing

```python
# tests/test_tools_advanced.py
import pytest
import json
from unittest.mock import patch, MagicMock
from src.memory_agent.analyzer import analyze_company

class TestAnalyzeCompany:
    
    def test_valid_company_query(self):
        """Test s validním dotazem."""
        result = analyze_company("ADIS TACHOV")
        data = json.loads(result)
        
        assert data["query_type"] == "company"
        assert data["analysis_complete"] is True
        assert "company_data" in data
        assert "execution_time" in data
    
    def test_empty_query(self):
        """Test s prázdným dotazem."""
        result = analyze_company("")
        data = json.loads(result)
        
        assert data["analysis_complete"] is False
        assert "error" in data
    
    @patch('src.memory_agent.tools.MockMCPConnector')
    def test_mocked_connector(self, mock_connector_class):
        """Test s mocknutým konektorem."""
        # Nastavení mock objektu
        mock_connector = MagicMock()
        mock_connector.get_company_by_name.return_value = {
            "id": "test_company",
            "name": "Test Company"
        }
        mock_connector_class.return_value = mock_connector
        
        result = analyze_company("Test Company")
        data = json.loads(result)
        
        assert data["company_data"]["name"] == "Test Company"
        mock_connector.get_company_by_name.assert_called_once()
    
    def test_performance_timing(self):
        """Test performance timing."""
        result = analyze_company("ADIS TACHOV")
        data = json.loads(result)
        
        assert "execution_time" in data
        assert isinstance(data["execution_time"], (int, float))
        assert data["execution_time"] > 0

@pytest.mark.asyncio 
async def test_async_operations():
    """Test asynchronních operací."""
    # Pokud používáte async funkce
    pass
```

### Integration testing

```python
# tests/test_integration.py
import pytest
from src.memory_agent.graph import memory_agent

class TestMemoryAgentIntegration:
    
    def test_full_workflow(self):
        """Test celého workflow."""
        config = {"configurable": {"thread_id": "test_thread"}}
        
        messages = [{"role": "user", "content": "Analyze ADIS TACHOV company"}]
        
        result = memory_agent.invoke({"messages": messages}, config=config)
        
        assert "messages" in result
        assert len(result["messages"]) > 1  # User message + AI response
    
    def test_multiple_interactions(self):
        """Test více interakcí v jednom thread."""
        config = {"configurable": {"thread_id": "multi_test"}}
        
        # První dotaz
        result1 = memory_agent.invoke({
            "messages": [{"role": "user", "content": "Analyze ADIS TACHOV"}]
        }, config=config)
        
        # Druhý dotaz ve stejném thread
        result2 = memory_agent.invoke({
            "messages": [{"role": "user", "content": "What about MB TOOL?"}]
        }, config=config)
        
        # Kontrola, že kontext je zachován
        assert len(result2["messages"]) > len(result1["messages"])
```

## Monitoring a debugging

### Logging setup

```python
import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """
    Nastavení konzistentního loggingu.
    """
    # Formát log zpráv
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root logger konfigurace
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    # Specifické loggery
    logging.getLogger('src.memory_agent').setLevel(level)
    logging.getLogger('langgraph').setLevel(logging.WARNING)  # Méně verbose
    
    return logger

# Inicializace při startu aplikace
logger = setup_logging()
```

### Custom metrics

```python
from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class PerformanceMetrics:
    """
    Sběr performance metrik.
    """
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    
    # Metriky pro jednotlivé komponenty
    tool_execution_times: Dict[str, float] = field(default_factory=dict)
    data_loading_time: Optional[float] = None
    analysis_time: Optional[float] = None
    
    # Error tracking
    errors_count: int = 0
    warnings_count: int = 0
    
    def finish(self):
        """Dokončí měření."""
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time
    
    def add_tool_time(self, tool_name: str, execution_time: float):
        """Přidá čas vykonání nástroje."""
        self.tool_execution_times[tool_name] = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Převede metriky do dict pro logování."""
        return {
            "execution_time": self.execution_time,
            "data_loading_time": self.data_loading_time,
            "analysis_time": self.analysis_time,
            "tool_times": self.tool_execution_times,
            "errors_count": self.errors_count,
            "warnings_count": self.warnings_count
        }

# Použití v tools
def instrumented_analyze_company(query: str) -> str:
    """Verze s instrumentací."""
    metrics = PerformanceMetrics()
    
    try:
        # Měření data loading
        load_start = time.time()
        connector = MockMCPConnector()
        company_data = connector.get_company_by_name(query)
        metrics.data_loading_time = time.time() - load_start
        
        # Měření analýzy
        analysis_start = time.time()
        # ... analysis logic ...
        metrics.analysis_time = time.time() - analysis_start
        
        # Finalizace
        metrics.finish()
        
        # Logování metrik
        logger.info(f"Performance metrics: {metrics.to_dict()}")
        
        return json.dumps({
            "company_data": company_data,
            "performance": metrics.to_dict(),
            "analysis_complete": True
        })
        
    except Exception as e:
        metrics.errors_count += 1
        metrics.finish()
        logger.error(f"Analysis failed: {str(e)}, metrics: {metrics.to_dict()}")
        raise
```

---

**Tyto best practices poskytují robustní základ pro vývoj a údržbu Memory Agent aplikace na LangGraph Platform. Implementujte je postupně podle potřeb vašeho konkrétního use case.**
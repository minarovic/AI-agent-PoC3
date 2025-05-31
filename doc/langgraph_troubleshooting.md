# LangGraph Troubleshooting Guide

Komplexní troubleshooting guide pro řešení problémů při vývoji Memory Agent aplikace na LangGraph Platform.

## Obsah

1. [Časté vývojářské problémy](#časté-vývojářské-problémy)
2. [LangGraph Platform issues](#langgraph-platform-issues)
3. [Performance problémy](#performance-problémy)
4. [Deployment problémy](#deployment-problémy)
5. [State management issues](#state-management-issues)
6. [Tools a funkcí problémy](#tools-a-funkcí-problémy)
7. [Debugging strategie](#debugging-strategie)
8. [Monitoring a alerting](#monitoring-a-alerting)

## Časté vývojářské problémy

### 1. Import a Module errors

#### Problem: `ModuleNotFoundError: No module named 'memory_agent'`

**Příčina**: Python nemůže najít modul v sys.path

**Řešení**:
```bash
# Lokální development
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Nebo v kódu
import sys
sys.path.append('src')

# Nebo při spouštění
python -m src.memory_agent.graph
```

**Pro trvalé řešení** - vytvořte `setup.py`:
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="memory_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langgraph>=0.2.10",
        "langchain>=0.1.0",
        "langchain_core>=0.1.0",
        # ... další dependencies
    ]
)
```

Pak nainstalujte v development mode:
```bash
pip install -e .
```

#### Problem: `ImportError: cannot import name 'X' from 'memory_agent'`

**Příčina**: Kruhové importy nebo neexistující symboly

**Debugging**:
```python
# Debug importů
python -c "
import sys
print('Python path:', sys.path)
try:
    import memory_agent
    print('memory_agent location:', memory_agent.__file__)
    print('memory_agent contents:', dir(memory_agent))
except Exception as e:
    print('Import error:', str(e))
"
```

**Řešení**:
- Zkontrolujte `__init__.py` soubory
- Přesuňte importy do funkcí (lazy import)
- Použijte relative importy ve stejném package

```python
# Místo absolutních importů
from memory_agent.tools import MockMCPConnector

# Použijte relative importy
from .tools import MockMCPConnector
```

### 2. JSON Serialization chyby

#### Problem: `TypeError: Object of type 'datetime' is not JSON serializable`

**Řešení**:
```python
import json
from datetime import datetime
from typing import Any

def json_serializer(obj: Any) -> Any:
    """Custom JSON serializer pro problematické typy."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif hasattr(obj, '_asdict'):  # namedtuple
        return obj._asdict()
    
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Použití
data = {"timestamp": datetime.now(), "value": 123}
json_string = json.dumps(data, default=json_serializer)
```

#### Problem: `UnicodeDecodeError` při načítání JSON

**Řešení**:
```python
# Explicitní encoding
def safe_load_json(file_path: str) -> Dict[str, Any]:
    """Bezpečné načítání JSON s error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        # Zkusit jiný encoding
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return {}
```

### 3. Pydantic validation errors

#### Problem: `ValidationError: X field required`

**Debugging**:
```python
from pydantic import ValidationError

try:
    model_instance = MyModel(**data)
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        print(f"  Field: {error['loc']}")
        print(f"  Message: {error['msg']}")
        print(f"  Input: {error['input']}")
```

**Řešení**:
```python
# Použití Optional a default hodnot
from typing import Optional
from pydantic import BaseModel, Field

class RobustModel(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    default_field: str = Field(default="default_value")
    
    class Config:
        # Povolí extra fields
        extra = "allow"
        # Validate assignment
        validate_assignment = True
```

## LangGraph Platform issues

### 1. Configuration schema problémy

#### Problem: `Configuration schema not found` nebo `Invalid graph reference`

**Příčina**: Nesprávný `langgraph.json`

**Kontrola**:
```bash
# Ověření syntax
python -c "import json; print(json.load(open('langgraph.json')))"

# Ověření, že graf existuje
python -c "from src.memory_agent.graph import memory_agent; print('Graph OK')"
```

**Správný formát `langgraph.json`**:
```json
{
  "dependencies": ["."],
  "graphs": {
    "memory_agent": "src.memory_agent.graph:memory_agent"
  },
  "env": ".env"
}
```

**Troubleshooting checklist**:
- [ ] Existuje soubor `src/memory_agent/graph.py`?
- [ ] Obsahuje `memory_agent` proměnnou?
- [ ] Je modul importovatelný?
- [ ] Jsou všechny dependencies v requirements.txt?

#### Problem: `Environment variables not loaded`

**Debugging**:
```python
# Test environment variables
import os
print("Environment variables:")
for key, value in os.environ.items():
    if 'API' in key or 'LANG' in key:
        print(f"{key}: {'***' if 'API' in key else value}")
```

**Řešení**: 
- Nastavte variables v LangGraph Platform administration
- Zkontrolujte `.env` soubor pro lokální development
- Použijte fallback hodnoty

```python
# Robust configuration
class Config:
    def __init__(self):
        self.openai_api_key = (
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("OPENAI_API_KEY_FALLBACK") or
            "demo-key"  # Pro development
        )
```

### 2. Graph compilation errors

#### Problem: `Graph compilation failed`

**Debugging steps**:
```python
# 1. Test základní import
try:
    from src.memory_agent.graph import memory_agent
    print("✓ Graph import OK")
except Exception as e:
    print(f"✗ Graph import failed: {str(e)}")

# 2. Test graph compilation
try:
    result = memory_agent.invoke({"messages": []})
    print("✓ Graph invocation OK")
except Exception as e:
    print(f"✗ Graph invocation failed: {str(e)}")

# 3. Test individual tools
try:
    from src.memory_agent.analyzer import analyze_company
    result = analyze_company("test")
    print("✓ Tools OK")
except Exception as e:
    print(f"✗ Tools failed: {str(e)}")
```

#### Problem: `Checkpointer initialization failed`

**Řešení**:
```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteCheckpoint
import os

def create_robust_checkpointer():
    """Vytvoří checkpointer s fallback options."""
    try:
        # Pro produkci
        if os.getenv("DATABASE_URL"):
            return SqliteCheckpoint(os.getenv("DATABASE_URL"))
        
        # Pro development
        if os.path.exists("checkpoints.db"):
            return SqliteCheckpoint("checkpoints.db")
        
        # Fallback
        logger.warning("Using InMemoryCheckpointer - data will not persist")
        return InMemorySaver()
        
    except Exception as e:
        logger.error(f"Checkpointer initialization failed: {str(e)}")
        return InMemorySaver()
```

## Performance problémy

### 1. Pomalé response times

#### Diagnostic tools:

```python
import time
import cProfile
import io
import pstats
from functools import wraps

def profile_function(func):
    """Profiling dekorátor."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        pr.disable()
        
        # Print profiling results
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        print(f"Function {func.__name__} took {end_time - start_time:.2f}s")
        print("Top time consumers:")
        print(s.getvalue())
        
        return result
    return wrapper

# Použití
@profile_function 
def analyze_company(query: str) -> str:
    # ... implementace
```

#### Optimization strategie:

```python
# 1. Lazy loading
def lazy_connector():
    """Lazy initialization MockMCPConnector."""
    if not hasattr(lazy_connector, '_connector'):
        lazy_connector._connector = MockMCPConnector()
    return lazy_connector._connector

# 2. Connection pooling pro external services
class ConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.pool = []
        self.active_connections = 0
    
    def get_connection(self):
        if self.pool:
            return self.pool.pop()
        elif self.active_connections < self.max_connections:
            self.active_connections += 1
            return self.create_connection()
        else:
            raise Exception("Connection pool exhausted")
    
    def release_connection(self, conn):
        self.pool.append(conn)

# 3. Batch processing
def process_multiple_queries(queries: List[str]) -> List[str]:
    """Zpracování více dotazů najednou."""
    connector = MockMCPConnector()
    results = []
    
    # Batch load all needed data
    company_data_batch = {}
    for query in queries:
        # Extract company names and pre-load data
        company_name = extract_company_name(query)
        if company_name not in company_data_batch:
            company_data_batch[company_name] = connector.get_company_by_name(company_name)
    
    # Process queries with cached data
    for query in queries:
        company_name = extract_company_name(query)
        data = company_data_batch[company_name]
        result = process_single_query(query, data)
        results.append(result)
    
    return results
```

### 2. Memory leaks

#### Debugging memory usage:

```python
import psutil
import gc
import tracemalloc
from typing import Dict, Any

class MemoryTracker:
    """Sledování memory usage."""
    
    def __init__(self):
        self.start_memory = None
        tracemalloc.start()
    
    def start_tracking(self):
        """Začne sledování."""
        gc.collect()  # Force garbage collection
        self.start_memory = psutil.Process().memory_info().rss
        
    def get_memory_usage(self) -> Dict[str, Any]:
        """Vrátí aktuální memory usage."""
        current_memory = psutil.Process().memory_info().rss
        memory_diff = current_memory - self.start_memory if self.start_memory else 0
        
        # Tracemalloc statistics
        current, peak = tracemalloc.get_traced_memory()
        
        return {
            "current_memory_mb": current_memory / 1024 / 1024,
            "memory_diff_mb": memory_diff / 1024 / 1024,
            "tracemalloc_current_mb": current / 1024 / 1024,
            "tracemalloc_peak_mb": peak / 1024 / 1024
        }
    
    def print_top_allocations(self, limit=10):
        """Vypíše top memory allocations."""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        print(f"Top {limit} memory allocations:")
        for stat in top_stats[:limit]:
            print(f"  {stat}")

# Použití
memory_tracker = MemoryTracker()

def memory_monitored_function(query: str) -> str:
    """Funkce s memory monitoring."""
    memory_tracker.start_tracking()
    
    try:
        result = analyze_company(query)
        
        # Log memory usage
        memory_info = memory_tracker.get_memory_usage()
        logger.info(f"Memory usage: {memory_info}")
        
        return result
        
    finally:
        # Clean up
        gc.collect()
```

## Deployment problémy

### 1. GitHub Actions failures

#### Problem: Tests failing in CI but passing locally

**Debugging checklist**:
- [ ] Same Python version? (Check `.github/workflows/`)
- [ ] Same dependencies versions? (`requirements.txt` vs local)
- [ ] Environment variables set?
- [ ] File paths (Windows vs Linux)?
- [ ] Timezone differences?

**Řešení**:
```yaml
# .github/workflows/test.yml - robust configuration
name: Test and Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'  # Specific version
          
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Set environment variables
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          echo "Environment variables set"
          
      - name: Run basic tests
        run: |
          python -c "from src.memory_agent.graph import memory_agent; print('Graph OK')"
          
      - name: Run full test suite
        run: python -m pytest tests/ -v --tb=short
```

#### Problem: Inconsistent test results

**Řešení - deterministic testing**:
```python
# tests/conftest.py
import random
import os
import pytest

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Nastavení konzistentního test prostředí."""
    # Fixed random seed
    random.seed(42)
    
    # Test environment variables
    os.environ.setdefault("MOCK_DATA_PATH", "mock_data_2")
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Clear caches
    if hasattr(setup_test_environment, '_cache_cleared'):
        return
    
    # Clear import caches
    import sys
    modules_to_clear = [k for k in sys.modules.keys() if k.startswith('memory_agent')]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    
    setup_test_environment._cache_cleared = True

@pytest.fixture
def isolated_connector():
    """Izolovaný connector pro testing."""
    from src.memory_agent.tools import MockMCPConnector
    
    # Use test-specific data path
    test_data_path = "tests/test_data"
    os.makedirs(test_data_path, exist_ok=True)
    
    return MockMCPConnector(data_path=test_data_path)
```

### 2. LangGraph Platform deployment issues

#### Problem: Deployment succeeds but application doesn't work

**Diagnostic steps**:

1. **Check deployment logs**:
   - GitHub Actions logs
   - LangGraph Platform deployment logs
   - Application runtime logs

2. **Test endpoints manually**:
```bash
# Test if application is reachable
curl -X POST "https://your-app.langchain.app/api/v1/runs" \
  -H "Content-Type: application/json" \
  -d '{"input": {"messages": [{"role": "user", "content": "test"}]}}'
```

3. **Verify configuration**:
```python
# Add health check endpoint
def health_check() -> str:
    """Health check pro deployment verification."""
    try:
        # Test basic functionality
        from src.memory_agent.graph import memory_agent
        from src.memory_agent.analyzer import analyze_company
        
        # Test tools
        test_result = analyze_company("test query")
        
        # Test graph
        graph_result = memory_agent.invoke({
            "messages": [{"role": "user", "content": "health check"}]
        })
        
        return json.dumps({
            "status": "healthy",
            "tools_working": True,
            "graph_working": True,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return json.dumps({
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": time.time()
        })
```

## State management issues

### 1. State corruption

#### Problem: State contains unexpected or corrupted data

**Debugging**:
```python
def debug_state(state: State) -> None:
    """Debug utility pro state inspection."""
    print("=== STATE DEBUG ===")
    print(f"Messages count: {len(state.messages) if state.messages else 0}")
    print(f"Company data keys: {list(state.company_data.keys()) if state.company_data else 'None'}")
    print(f"Analysis result keys: {list(state.analysis_result.keys()) if state.analysis_result else 'None'}")
    print(f"Error state: {state.error_state}")
    print(f"Current query: {state.current_query}")
    
    # Type checking
    for field_name, field_value in state.__dict__.items():
        print(f"{field_name}: {type(field_value)}")

# Použití v graph nodes
def debug_node(state: State) -> State:
    """Debug node pro state inspection."""
    debug_state(state)
    return state
```

#### Problem: State reducers not working correctly

**Testing reducers**:
```python
def test_merge_dict_values():
    """Test merge_dict_values reducer."""
    from src.memory_agent.state import merge_dict_values
    
    left = {"a": 1, "b": {"nested": "value1"}}
    right = {"b": {"nested": "value2", "new": "value"}, "c": 3}
    
    result = merge_dict_values(left, right)
    
    assert result["a"] == 1
    assert result["b"]["nested"] == "value2"
    assert result["b"]["new"] == "value"
    assert result["c"] == 3
    
    print("✓ merge_dict_values working correctly")

def test_state_updates():
    """Test state updates."""
    from src.memory_agent.state import State
    
    # Create initial state
    state = State(messages=[])
    
    # Test company_data update
    state.company_data = {"company_id": "test", "name": "Test Company"}
    assert state.company_data["company_id"] == "test"
    
    # Test merge update
    new_data = {"additional_info": "extra data"}
    # Simulate reducer behavior
    state.company_data = merge_dict_values(state.company_data, new_data)
    
    assert "company_id" in state.company_data
    assert "additional_info" in state.company_data
    
    print("✓ State updates working correctly")
```

## Tools a funkcí problémy

### 1. Tool execution failures

#### Problem: Tools raising unexpected exceptions

**Robust tool wrapper**:
```python
from functools import wraps
import traceback

def robust_tool(func):
    """Wrapper pro robustní tool execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Executing tool {func.__name__} with args: {args[:2]}...")  # Truncate args
            
            result = func(*args, **kwargs)
            
            # Validate result
            if not isinstance(result, str):
                logger.warning(f"Tool {func.__name__} returned non-string: {type(result)}")
                result = str(result)
            
            # Validate JSON if expected
            try:
                json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Tool {func.__name__} returned invalid JSON")
            
            return result
            
        except Exception as e:
            logger.error(f"Tool {func.__name__} failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return structured error
            error_result = {
                "error": str(e),
                "error_type": type(e).__name__,
                "tool_name": func.__name__,
                "analysis_complete": False,
                "timestamp": time.time()
            }
            
            return json.dumps(error_result)
    
    return wrapper

# Apply to all tools
@robust_tool
def analyze_company(query: str) -> str:
    # ... implementation
```

#### Problem: Tools returning inconsistent data formats

**Standardization**:
```python
from typing import TypedDict, Any, Optional

class ToolResponse(TypedDict):
    """Standardní formát tool response."""
    query_type: str
    analysis_complete: bool
    timestamp: float
    query: str
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    error_type: Optional[str]

def create_standard_response(
    query_type: str,
    query: str,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    error_type: Optional[str] = None
) -> str:
    """Vytvoří standardizovanou response."""
    
    response: ToolResponse = {
        "query_type": query_type,
        "analysis_complete": error is None,
        "timestamp": time.time(),
        "query": query,
        "data": data,
        "error": error,
        "error_type": error_type
    }
    
    return json.dumps(response, indent=2, ensure_ascii=False)

# Použití v tools
def standardized_analyze_company(query: str) -> str:
    """Standardizovaná verze analyze_company."""
    try:
        connector = MockMCPConnector()
        company_data = connector.get_company_by_name(query)
        
        return create_standard_response(
            query_type="company",
            query=query,
            data={"company_data": company_data}
        )
        
    except Exception as e:
        return create_standard_response(
            query_type="company",
            query=query,
            error=str(e),
            error_type=type(e).__name__
        )
```

## Debugging strategie

### 1. Comprehensive logging

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """Strukturované logování pro debugging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def log_function_entry(self, func_name: str, args: tuple, kwargs: dict):
        """Log function entry."""
        self.logger.info(json.dumps({
            "event": "function_entry",
            "function": func_name,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_function_exit(self, func_name: str, result_type: str, execution_time: float):
        """Log function exit."""
        self.logger.info(json.dumps({
            "event": "function_exit",
            "function": func_name,
            "result_type": result_type,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }))
    
    def log_error(self, func_name: str, error: Exception, context: Dict[str, Any] = None):
        """Log error with context."""
        self.logger.error(json.dumps({
            "event": "error",
            "function": func_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }))

def debug_trace(func):
    """Comprehensive debugging decorator."""
    logger = StructuredLogger(f"debug.{func.__module__}.{func.__name__}")
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Log entry
        logger.log_function_entry(func.__name__, args, kwargs)
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful exit
            execution_time = time.time() - start_time
            logger.log_function_exit(
                func.__name__, 
                type(result).__name__, 
                execution_time
            )
            
            return result
            
        except Exception as e:
            # Log error with context
            context = {
                "args_types": [type(arg).__name__ for arg in args],
                "kwargs": {k: type(v).__name__ for k, v in kwargs.items()},
                "execution_time": time.time() - start_time
            }
            logger.log_error(func.__name__, e, context)
            raise
    
    return wrapper

# Apply to critical functions
@debug_trace
def analyze_company(query: str) -> str:
    # ... implementation
```

### 2. Interactive debugging

```python
def enable_interactive_debugging():
    """Povolí interaktivní debugging v production."""
    import code
    import sys
    
    def debug_here(local_vars=None):
        """Spustí interaktivní shell s lokálními proměnnými."""
        if local_vars is None:
            local_vars = sys._getframe(1).f_locals
        
        code.interact(local=local_vars)
    
    # Make available globally
    import builtins
    builtins.debug_here = debug_here

# Použití
def problematic_function(data):
    """Funkce s potential issues."""
    processed_data = process_data(data)
    
    # Drop into interactive shell if needed
    if os.getenv("DEBUG_MODE"):
        debug_here(locals())
    
    return analyzed_data
```

## Monitoring a alerting

### 1. Application monitoring

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading
import time

@dataclass
class ApplicationMetrics:
    """Application-level metriky."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    
    response_times: List[float] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def add_request(self, success: bool, response_time: float, error_type: Optional[str] = None):
        """Přidá request metriku."""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        self.response_times.append(response_time)
        
        # Udržovat pouze posledních 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Update average
        self.average_response_time = sum(self.response_times) / len(self.response_times)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Vrátí health status."""
        success_rate = (self.successful_requests / self.total_requests) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "success_rate": success_rate,
            "average_response_time": self.average_response_time,
            "error_types": self.error_types,
            "health": "healthy" if success_rate > 0.95 else "unhealthy"
        }

# Global metrics instance
app_metrics = ApplicationMetrics()

def monitored_function(func):
    """Monitoring decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        error_type = None
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            raise
            
        finally:
            response_time = time.time() - start_time
            app_metrics.add_request(success, response_time, error_type)
    
    return wrapper

# Apply monitoring
@monitored_function
def analyze_company(query: str) -> str:
    # ... implementation
```

### 2. Alerting system

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    """Jednoduchý alerting systém."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "response_time": 5.0,  # 5 seconds
            "consecutive_failures": 10
        }
        
        self.consecutive_failures = 0
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minut
    
    def check_and_alert(self, metrics: ApplicationMetrics):
        """Zkontroluje metriky a pošle alerty."""
        current_time = time.time()
        
        # Cooldown check
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        alerts = []
        
        # Error rate check
        if metrics.total_requests > 0:
            error_rate = metrics.failed_requests / metrics.total_requests
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append(f"High error rate: {error_rate:.2%}")
        
        # Response time check
        if metrics.average_response_time > self.alert_thresholds["response_time"]:
            alerts.append(f"High response time: {metrics.average_response_time:.2f}s")
        
        # Send alerts if any
        if alerts:
            self.send_alert(alerts, metrics)
            self.last_alert_time = current_time
    
    def send_alert(self, alerts: List[str], metrics: ApplicationMetrics):
        """Pošle alert email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = "admin@example.com"  # Configure appropriately
            msg['Subject'] = "Memory Agent Alert"
            
            body = f"""
            Memory Agent Alert
            
            Issues detected:
            {chr(10).join(f"- {alert}" for alert in alerts)}
            
            Current metrics:
            - Total requests: {metrics.total_requests}
            - Success rate: {metrics.successful_requests / metrics.total_requests:.2%}
            - Average response time: {metrics.average_response_time:.2f}s
            - Error types: {metrics.error_types}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

# Usage
if os.getenv("ENABLE_ALERTS"):
    alert_manager = AlertManager(
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("SMTP_USERNAME"),
        password=os.getenv("SMTP_PASSWORD")
    )
    
    # Periodic check (run in background thread)
    def periodic_check():
        while True:
            time.sleep(60)  # Check every minute
            alert_manager.check_and_alert(app_metrics)
    
    threading.Thread(target=periodic_check, daemon=True).start()
```

---

**Tento troubleshooting guide poskytuje systematický přístup k řešení většiny problémů, které se mohou objevit při vývoji Memory Agent aplikace. Při řešení problémů postupujte systematicky od jednoduchých kontrol po komplexní debugging.**
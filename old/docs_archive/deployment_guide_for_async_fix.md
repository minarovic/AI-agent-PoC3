# Deployment Guide for LangGraph Platform - KeyError Resolution

## [2025-05-18] - Resolution of KeyError involving coroutine objects

### Issue Summary
When deploying the AI-agent-Ntier application to LangGraph Platform, the following error was encountered:
```
KeyError: <coroutine object analyze_query at 0x7b3556b87b50>
```

This error occurred in the `route_query` node of the graph workflow, specifically when the asynchronous function `analyze_query` was being called from a synchronous context, resulting in a coroutine object that wasn't being properly awaited before use.

### Root Cause Analysis
LangGraph nodes operate in a synchronous manner, but our code was using an asynchronous function (`analyze_query`). When an async function is called without awaiting it, it returns a coroutine object rather than the actual result. When this coroutine object was used as a key in a dictionary or passed to conditional routing logic, it caused the KeyError.

### Solution Implementation
The solution that has been implemented involves:

1. **Using a synchronous wrapper**: We've implemented and are using `analyze_query_sync` which properly handles the asynchronous `analyze_query` function by using `loop.run_until_complete()`.

2. **Proper imports**: The `graph_nodes.py` file has been updated to import the synchronous wrapper instead of the asynchronous function:
   ```python
   # Before:
   from memory_agent.analyzer import analyze_query
   
   # After:
   from memory_agent.analyzer import analyze_query_sync
   ```

3. **Correct function usage**: The `route_query` function has been updated to call the synchronous wrapper:
   ```python
   # Before (problematic code):
   query_type = analyze_query(state.current_query)  # Returns coroutine object
   
   # After (correct code):
   query_type = analyze_query_sync(state.current_query)  # Returns string value
   ```

4. **Support modules**: The necessary utility modules (`utils.py` and `schema.py`) have been created to support this functionality.

5. **Clear naming**: The original asynchronous function has been renamed to `analyze_query_async` for clarity, while maintaining the original name for backward compatibility:
   ```python
   # Alias for clarity
   analyze_query_async = analyze_query
   ```

### Deployment Checklist

Before deploying to LangGraph Platform, ensure:

1. ✅ All modules import the synchronous wrapper `analyze_query_sync` instead of the asynchronous `analyze_query`
2. ✅ The lambda function in `graph.py` correctly accesses the `query_type` attribute directly from the State object:
   ```python
   lambda x: x.query_type  # x is directly the State object, not a dictionary
   ```
3. ✅ The synchronous wrapper `analyze_query_sync` is properly implemented in `analyzer.py`
4. ✅ The `utils.py` and `schema.py` files have been properly created and contain the required functions and classes
5. ✅ All dependencies are properly listed in `requirements.txt` and/or `requirements-platform.txt`

### Best Practices for Future Development

1. **Asynchronous Functions in LangGraph**:
   - Always create synchronous wrappers for asynchronous functions used in LangGraph nodes
   - Use clear naming conventions (_sync, _async) to distinguish between synchronous and asynchronous versions
   - Use `asyncio.run_until_complete()` to properly await asynchronous results in synchronous contexts

2. **Error Handling**:
   - Add robust error handling in synchronous wrappers to catch any exceptions from asynchronous code
   - Log error details to help diagnose issues during deployment
   - Return sensible default values or error indicators when async functions fail

3. **Testing**:
   - Create specific tests for synchronous wrappers to ensure they handle asynchronous code properly
   - Test with the same environment that will be used in LangGraph Platform
   - Validate that all graph nodes are using synchronous functions where appropriate

### Additional Resources

- [LangGraph documentation on handling async functions](https://langchain-ai.github.io/langgraph/)
- [Asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [LangGraph Platform deployment best practices](https://docs.langchain.com/langgraph-platform/)

# OpenAI API Key Authentication Issue - Resolution Guide

## Issue Summary
The application was experiencing a 401 authentication error when trying to use OpenAI API with the error message:
```
AuthenticationError("Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-proj-...MOoA. You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_api_key'}}")
```

## Root Cause
The issue was that the OpenAI API key stored in GitHub secrets was either:
1. Invalid/expired/revoked
2. Incorrectly formatted due to copy/paste errors
3. Not properly configured in GitHub secrets

## Solution Implemented

### 1. API Key Validation Module (`src/memory_agent/api_validation.py`)
- Added comprehensive validation that checks:
  - API key format (must start with 'sk-')
  - Minimum length requirements
  - Detection of placeholder/test keys
  - Formatting issues (spaces, newlines)
  - Fake/test key patterns

### 2. Enhanced Error Handling (`src/memory_agent/graph.py`)
- Integrated validation into the memory agent creation
- Provides detailed diagnostic information when validation fails
- Gracefully handles missing or invalid API keys

### 3. Improved Testing (`tests/test_api.py`)
- Added API key validation tests
- Enhanced OpenAI API connection test with better error messages
- Updated memory agent import tests to handle validation scenarios

### 4. Troubleshooting Tools
- **`troubleshoot_api_key.py`**: Interactive script to diagnose API key issues
- **Enhanced `test_api_keys.py`**: Better validation of all required API keys

## Quick Diagnosis Commands

### Check API Key Status
```bash
# Run comprehensive troubleshooting
python troubleshoot_api_key.py

# Quick API key validation
python test_api_keys.py

# Test specific validation
python -c "from src.memory_agent.api_validation import validate_openai_api_key; print(validate_openai_api_key())"
```

### Test Memory Agent Creation
```bash
# Test agent creation with current environment
python -c "from src.memory_agent.graph import create_memory_agent; create_memory_agent()"
```

## Common Issues and Solutions

### Issue: "OPENAI_API_KEY environment variable is not set"
**Solutions:**
- For GitHub Actions: Ensure `OPENAI_API_KEY` secret is configured
- For local development: Create `.env` file with your API key
- For manual testing: `export OPENAI_API_KEY='your-key-here'`

### Issue: "OpenAI API key should start with 'sk-'"
**Solutions:**
- Verify the key was copied correctly from OpenAI platform
- Check for extra characters or formatting issues
- Regenerate the API key if necessary

### Issue: "API key appears to be fake/test key"
**Solutions:**
- Replace placeholder keys with real API keys
- Remove test patterns from the key
- Use actual keys from https://platform.openai.com/account/api-keys

### Issue: 401 Authentication Error with Valid Format
**Solutions:**
- Check if the API key has expired
- Verify the key hasn't been revoked
- Check OpenAI account status and billing
- Regenerate the API key

## GitHub Actions Configuration

Ensure your GitHub workflow has the API key properly configured:

```yaml
- name: Set up environment variables
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    # ... other keys
  run: |
    # Your setup commands
```

## Testing the Fix

### Local Testing
```bash
# Test with no API key (should show clear error)
unset OPENAI_API_KEY
python troubleshoot_api_key.py

# Test with invalid API key
export OPENAI_API_KEY="invalid-key"
python troubleshoot_api_key.py

# Test with valid format but fake key
export OPENAI_API_KEY="sk-proj-validformatbutfakekeyexample"
python troubleshoot_api_key.py
```

### GitHub Actions Testing
The improved tests will provide detailed error messages in GitHub Actions logs, making it easier to identify if the issue is:
- Missing secret configuration
- Invalid API key format
- Expired/revoked API key

## Prevention

1. **Use the validation tools**: Run `python troubleshoot_api_key.py` before deployment
2. **Monitor API key expiration**: Set up alerts for API key rotation
3. **Use environment-specific keys**: Different keys for development, staging, production
4. **Regular validation**: Include API key validation in CI/CD pipeline

## Files Modified

- `src/memory_agent/api_validation.py` - New validation module
- `src/memory_agent/graph.py` - Enhanced error handling
- `tests/test_api.py` - Improved test coverage
- `test_api_keys.py` - Enhanced validation
- `troubleshoot_api_key.py` - New troubleshooting tool

This solution provides comprehensive error handling and diagnostic tools to quickly identify and resolve OpenAI API key authentication issues.
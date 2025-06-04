"""
API key validation utilities for Memory Agent.
Helps diagnose and validate API key issues.
"""

import os
import re
from typing import Optional, Tuple


def validate_openai_api_key(api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate OpenAI API key format and basic checks.
    
    Args:
        api_key: The API key to validate. If None, gets from environment.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return False, "OPENAI_API_KEY environment variable is not set"
    
    # Check if the key is just a placeholder
    if api_key in ["your_openai_api_key", "your_openai_api_key_here", "test-key"]:
        return False, f"API key appears to be a placeholder: {api_key}"
    
    # Basic format validation for OpenAI API keys
    # OpenAI keys typically start with "sk-" and have specific patterns
    if not api_key.startswith("sk-"):
        return False, f"OpenAI API key should start with 'sk-', got: {api_key[:10]}..."
    
    # Check minimum length (OpenAI keys are typically longer)
    if len(api_key) < 20:
        return False, f"API key appears too short (length: {len(api_key)})"
    
    # Check for common formatting issues
    if " " in api_key:
        return False, "API key contains spaces"
    
    if "\n" in api_key or "\r" in api_key:
        return False, "API key contains newline characters"
    
    # Check for obvious test/fake keys
    fake_patterns = ["fake", "test", "dummy", "invalid", "example"]
    for pattern in fake_patterns:
        if pattern.lower() in api_key.lower():
            return False, f"API key appears to be fake/test key (contains '{pattern}')"
    
    return True, "API key format appears valid"


def get_validated_openai_api_key() -> str:
    """
    Get and validate OpenAI API key from environment.
    
    Returns:
        Valid API key
        
    Raises:
        EnvironmentError: If API key is missing or invalid
    """
    is_valid, message = validate_openai_api_key()
    
    if not is_valid:
        raise EnvironmentError(f"Invalid OpenAI API key: {message}")
    
    return os.environ["OPENAI_API_KEY"]


def diagnose_api_key_issue() -> str:
    """
    Provide detailed diagnosis of API key configuration issues.
    
    Returns:
        Diagnostic message
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return """
OpenAI API key not found. Please check:
1. OPENAI_API_KEY environment variable is set
2. In GitHub Actions, ensure the secret is properly configured
3. For local development, create a .env file with your API key
"""
    
    is_valid, message = validate_openai_api_key(api_key)
    
    if not is_valid:
        return f"""
OpenAI API key validation failed: {message}

Current key preview: {api_key[:15]}...{api_key[-4:] if len(api_key) > 4 else ''}

Please check:
1. The API key is correctly copied from https://platform.openai.com/account/api-keys
2. No extra spaces or newlines were added
3. The key hasn't expired or been revoked
4. GitHub secret is properly configured (if using GitHub Actions)
"""
    
    return "API key format appears valid. If you're still getting 401 errors, the key may be expired or revoked."
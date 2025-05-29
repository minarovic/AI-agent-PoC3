#!/usr/bin/env python3
"""
Test script to verify GitHub Actions environment variables and API keys.
This script checks if the required environment variables are properly set.
"""

import os
import sys

def test_api_keys():
    """Test that all required API keys are available and properly formatted."""
    required_keys = {
        'OPENAI_API_KEY': 'sk-',
        'ANTHROPIC_API_KEY': 'sk-ant-',
        'LANGSMITH_API_KEY': 'ls-'
    }
    
    all_good = True
    
    print("🔍 Testing API Keys availability...")
    print("-" * 50)
    
    for key_name, expected_prefix in required_keys.items():
        value = os.environ.get(key_name)
        
        if not value:
            print(f"❌ {key_name}: NOT SET")
            all_good = False
        elif value.startswith('sk-mock-') or value.startswith('sk-ant-mock-') or value.startswith('ls-mock-'):
            print(f"⚠️  {key_name}: MOCK KEY (value: {value[:20]}...)")
            print(f"   This is a mock key, not a real API key!")
        elif value.startswith(expected_prefix):
            print(f"✅ {key_name}: PROPERLY SET (prefix: {expected_prefix})")
        else:
            print(f"❌ {key_name}: INVALID FORMAT (expected prefix: {expected_prefix})")
            all_good = False
    
    print("-" * 50)
    
    # Test environment detection
    if os.environ.get('GITHUB_ACTIONS'):
        print("🏃 Running in GitHub Actions")
        if os.environ.get('GITHUB_REPOSITORY'):
            print(f"📦 Repository: {os.environ.get('GITHUB_REPOSITORY')}")
        if os.environ.get('GITHUB_REF'):
            print(f"🌿 Branch: {os.environ.get('GITHUB_REF')}")
    else:
        print("💻 Running locally")
    
    print("-" * 50)
    
    if all_good:
        print("✅ ALL API KEYS ARE PROPERLY CONFIGURED!")
        return True
    else:
        print("❌ SOME API KEYS ARE NOT PROPERLY CONFIGURED!")
        return False

if __name__ == "__main__":
    success = test_api_keys()
    sys.exit(0 if success else 1)

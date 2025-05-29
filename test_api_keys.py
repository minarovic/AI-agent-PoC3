#!/usr/bin/env python3
"""
Test script to verify GitHub Actions environment variables and API keys.
This script checks if the required environment variables are properly set.
"""

import os
import sys

def test_api_keys():
    """Test that all required API keys are available and properly formatted."""
    # Critical keys for LangGraph Platform deployment
    critical_keys = {
        'OPENAI_API_KEY': 'sk-',
        'ANTHROPIC_API_KEY': 'sk-ant-',
    }
    
    # Optional keys (for monitoring and logging)
    optional_keys = {
        'LANGSMITH_API_KEY': 'ls-'
    }
    
    all_critical_good = True
    
    print("🔍 Testing API Keys availability...")
    print("-" * 50)
    
    # Test critical keys
    print("🚨 CRITICAL KEYS (required for deployment):")
    for key_name, expected_prefix in critical_keys.items():
        value = os.environ.get(key_name)
        
        if not value:
            print(f"❌ {key_name}: NOT SET")
            all_critical_good = False
        elif value.startswith('sk-mock-') or value.startswith('sk-ant-mock-'):
            print(f"⚠️  {key_name}: MOCK KEY (value: {value[:20]}...)")
            print(f"   This is a mock key, not a real API key!")
            all_critical_good = False
        elif value.startswith(expected_prefix):
            print(f"✅ {key_name}: PROPERLY SET (prefix: {expected_prefix})")
        else:
            print(f"❌ {key_name}: INVALID FORMAT (expected prefix: {expected_prefix})")
            all_critical_good = False
    
    # Test optional keys
    print("\n📊 OPTIONAL KEYS (for monitoring):")
    for key_name, expected_prefix in optional_keys.items():
        value = os.environ.get(key_name)
        
        if not value:
            print(f"⚠️  {key_name}: NOT SET (optional)")
        elif value.startswith('ls-mock-'):
            print(f"⚠️  {key_name}: MOCK KEY (value: {value[:20]}...)")
        elif value.startswith(expected_prefix):
            print(f"✅ {key_name}: PROPERLY SET (prefix: {expected_prefix})")
        else:
            print(f"⚠️  {key_name}: NON-STANDARD FORMAT (expected: {expected_prefix}, might still work)")
    
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
    
    if all_critical_good:
        print("✅ ALL CRITICAL API KEYS ARE PROPERLY CONFIGURED!")
        print("🚀 Ready for LangGraph Platform deployment!")
        return True
    else:
        print("❌ SOME CRITICAL API KEYS ARE NOT PROPERLY CONFIGURED!")
        print("💡 Please check your GitHub Repository Secrets")
        return False

if __name__ == "__main__":
    success = test_api_keys()
    sys.exit(0 if success else 1)

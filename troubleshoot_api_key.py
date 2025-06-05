#!/usr/bin/env python3
"""
OpenAI API Key Troubleshooting Script

This script helps diagnose common issues with OpenAI API key configuration.
Run this script to get detailed information about potential API key problems.
"""

import os
import sys

# Add src to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, "src")
sys.path.insert(0, src_path)


def main():
    print("🔍 OpenAI API Key Troubleshooting")
    print("=" * 50)

    try:
        from memory_agent.api_validation import (
            diagnose_api_key_issue,
            validate_openai_api_key,
        )

        print("\n1. Checking API key environment variable...")
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            print("❌ OPENAI_API_KEY environment variable is not set")
            print("\n💡 Solutions:")
            print("   - For local development: Create a .env file with your API key")
            print("   - For GitHub Actions: Ensure the secret OPENAI_API_KEY is set")
            print("   - For manual testing: export OPENAI_API_KEY='your-key-here'")
            return

        print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")
        print(
            f"   Preview: {api_key[:15]}...{api_key[-4:] if len(api_key) > 4 else ''}"
        )

        print("\n2. Validating API key format...")
        is_valid, message = validate_openai_api_key(api_key)

        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            print("\n" + diagnose_api_key_issue())
            return

        print("\n3. Testing basic OpenAI API connection...")
        try:
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI

            chat_model = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=10)
            response = chat_model.invoke([HumanMessage(content="Say 'Hello'")])

            print("✅ OpenAI API connection successful!")
            print(f"   Response: {response.content}")

        except Exception as e:
            print(f"❌ OpenAI API connection failed: {str(e)}")

            # Provide specific guidance based on error type
            error_str = str(e).lower()
            if "401" in error_str or "authentication" in error_str:
                print("\n💡 This looks like an authentication error:")
                print("   - The API key might be expired or revoked")
                print("   - Check https://platform.openai.com/account/api-keys")
                print("   - Regenerate the API key if necessary")
            elif "429" in error_str or "rate limit" in error_str:
                print("\n💡 This looks like a rate limit error:")
                print("   - You may have exceeded your API quota")
                print(
                    "   - Check your OpenAI usage at https://platform.openai.com/usage"
                )
            elif "network" in error_str or "connection" in error_str:
                print("\n💡 This looks like a network error:")
                print("   - Check your internet connection")
                print("   - Verify firewall settings")
            else:
                print("\n💡 For more help:")
                print("   - Check OpenAI status: https://status.openai.com/")
                print(
                    "   - Review OpenAI documentation: https://platform.openai.com/docs"
                )

        print("\n4. Checking LangGraph configuration...")
        langgraph_config = "langgraph.json"
        if os.path.exists(langgraph_config):
            print("✅ langgraph.json found")
            import json

            with open(langgraph_config, "r") as f:
                config = json.load(f)

            if "env" in config:
                print(f"✅ Environment config: {config['env']}")
            else:
                print(
                    "⚠️  No 'env' field in langgraph.json - environment variables may not be loaded"
                )
        else:
            print("⚠️  langgraph.json not found")

    except ImportError as e:
        print(f"❌ Could not import validation modules: {e}")
        print("   Make sure you're running this script from the project root directory")

    print("\n" + "=" * 50)
    print("Troubleshooting complete!")


if __name__ == "__main__":
    main()

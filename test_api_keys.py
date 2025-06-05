import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from memory_agent.api_validation import (
        validate_openai_api_key,
        diagnose_api_key_issue,
    )

    validation_available = True
except ImportError:
    validation_available = False


def validate_api_keys():
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LANGSMITH_API_KEY"]

    for key in keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Chybí environment variable: {key}")

        # Special validation for OpenAI API key if validation is available
        if key == "OPENAI_API_KEY" and validation_available:
            is_valid, message = validate_openai_api_key(value)
            if not is_valid:
                print(f"⚠️  VAROVÁNÍ pro {key}: {message}")
                print(diagnose_api_key_issue())
                raise ValueError(f"Invalid {key}: {message}")
            else:
                print(f"✅ {key}: {message}")
        else:
            print(f"✅ {key}: nastavený (délka: {len(value)})")

    print("Všechny API klíče jsou správně nastavené.")


if __name__ == "__main__":
    validate_api_keys()

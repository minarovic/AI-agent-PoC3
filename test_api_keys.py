import os

def validate_api_keys():
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LANGSMITH_API_KEY"]
    for key in keys:
        if not os.getenv(key):
            raise ValueError(f"Chybí environment variable: {key}")
    print("Všechny API klíče jsou správně nastavené.")

if __name__ == "__main__":
    validate_api_keys()
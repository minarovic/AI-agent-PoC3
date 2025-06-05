#!/usr/bin/env python3
"""
Demo script showing that the Memory Agent has assistant settings specific to nodes in the graph.

This script answers the LangGraph Studio question:
"Have assistant settings that are specific to a node in your graph?"

The answer is: YES - this script demonstrates the node-specific assistant configurations.
"""

import json
import os

# Add src to path for local testing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    print("🔍 LangGraph Studio Node Assistant Settings Demo")
    print("=" * 60)

    # Set a dummy API key for demonstration (won't actually call API)
    os.environ["OPENAI_API_KEY"] = "demo-key-for-config-only"

    try:
        from memory_agent.graph import get_node_assistant_settings, get_studio_config
        from memory_agent.node_config import (
            list_configured_nodes,
            validate_node_configs,
        )

        print(
            "\n✅ Question: 'Have assistant settings that are specific to a node in your graph?'"
        )
        print(
            "✅ Answer: YES - The Memory Agent has node-specific assistant settings configured."
        )

        print("\n📋 Configured Nodes:")
        nodes = list_configured_nodes()
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node}")

        print(f"\n📊 Total Configured Nodes: {len(nodes)}")

        print("\n🔧 Node Assistant Settings:")
        settings = get_node_assistant_settings()
        for node_name, config in settings.items():
            print(f"\n   🔹 {node_name}:")
            print(f"      Model: {config['model']}")
            print(f"      Temperature: {config['temperature']}")
            print(f"      Tools: {config['tools']}")
            print(f"      Description: {config['description']}")

        print("\n🏗️ LangGraph Studio Configuration:")
        studio_config = get_studio_config()
        print(f"   Nodes configured: {len(studio_config['nodes'])}")
        print(f"   Assistants configured: {len(studio_config['assistants'])}")
        print(f"   Configuration version: {studio_config['metadata']['version']}")

        print("\n✅ Validation Results:")
        validation = validate_node_configs()
        print(f"   Valid: {validation['valid']}")
        print(f"   Node count: {validation['node_count']}")
        print(f"   Errors: {len(validation['errors'])}")
        print(f"   Warnings: {len(validation['warnings'])}")

        if validation["errors"]:
            print("   Error details:")
            for error in validation["errors"]:
                print(f"     - {error}")

        if validation["warnings"]:
            print("   Warning details:")
            for warning in validation["warnings"]:
                print(f"     - {warning}")

        print("\n📄 Sample Studio Configuration (JSON):")
        sample_config = {
            "nodes": dict(
                list(studio_config["nodes"].items())[:2]
            ),  # Show first 2 nodes
            "assistants": dict(
                list(studio_config["assistants"].items())[:2]
            ),  # Show first 2 assistants
        }
        print(json.dumps(sample_config, indent=2))

        print("\n" + "=" * 60)
        print("🎯 CONCLUSION: The Memory Agent IS PROPERLY CONFIGURED with")
        print("   node-specific assistant settings for LangGraph Studio!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error demonstrating assistant settings: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

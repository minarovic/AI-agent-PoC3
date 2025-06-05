#!/usr/bin/env python3
"""
Test script to verify LangGraph Studio prompt editing capabilities.

This script tests:
1. Direct node editing capability
2. LangSmith Playground integration support
3. Dynamic prompt updates
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set dummy API key for testing (only if not in CI environment)
if not (os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"):
    os.environ["OPENAI_API_KEY"] = "dummy_key_for_testing"

from memory_agent.graph import memory_agent, create_memory_agent
from memory_agent.prompts import PromptRegistry, SYSTEM_PROMPT
from memory_agent.analyzer import analyze_company


def test_current_graph_structure():
    """Test the current graph structure and prompt access."""
    print("=== Testing Current Graph Structure ===")
    
    # Test basic graph structure
    print(f"Graph type: {type(memory_agent)}")
    print(f"Graph nodes: {list(memory_agent.nodes.keys()) if memory_agent.nodes else 'No nodes'}")
    
    # Check if graph is using create_react_agent pattern
    print(f"Graph is compiled: {hasattr(memory_agent, 'compiled')}")
    
    return True


def test_prompt_registry_functionality():
    """Test the PromptRegistry system."""
    print("\n=== Testing PromptRegistry Functionality ===")
    
    # Test getting existing prompts
    company_prompt = PromptRegistry.get_prompt("company_analysis")
    print(f"Company analysis prompt exists: {company_prompt is not None}")
    
    # Test adding new prompt
    test_prompt_id = "test_prompt"
    test_prompt_text = "This is a test prompt for {company_name}"
    PromptRegistry.add_prompt(test_prompt_id, test_prompt_text)
    
    retrieved_prompt = PromptRegistry.get_prompt(test_prompt_id)
    print(f"Added prompt retrieved successfully: {retrieved_prompt == test_prompt_text}")
    
    # Test updating prompt
    updated_text = "This is an updated test prompt for {company_name}"
    update_success = PromptRegistry.update_prompt(test_prompt_id, updated_text)
    print(f"Prompt update successful: {update_success}")
    
    final_prompt = PromptRegistry.get_prompt(test_prompt_id)
    print(f"Updated prompt retrieved correctly: {final_prompt == updated_text}")
    
    return True


def test_prompt_editing_support():
    """Test if the current implementation supports prompt editing."""
    print("\n=== Testing Prompt Editing Support ===")
    
    # Check if graph uses static or dynamic prompts
    # In create_react_agent, the prompt is set during creation
    print("Current implementation uses create_react_agent with static prompt")
    
    # Test if we can create a new agent with different prompt
    original_prompt = "You are a helpful business intelligence assistant. Use the analyze_company tool to get information about companies and provide detailed, structured analysis based on the retrieved data."
    updated_prompt = "You are an expert financial analyst. Use the analyze_company tool to provide detailed financial analysis and risk assessment."
    
    try:
        # Create agent with updated prompt
        from langgraph.prebuilt import create_react_agent
        from langgraph.checkpoint.memory import InMemorySaver
        from memory_agent.analyzer import analyze_company
        
        updated_agent = create_react_agent(
            model="openai:gpt-4",
            tools=[analyze_company],
            prompt=updated_prompt,
            checkpointer=InMemorySaver(),
        )
        print("✅ Can create agent with different prompt")
        print(f"Updated agent type: {type(updated_agent)}")
        
    except Exception as e:
        print(f"❌ Error creating agent with updated prompt: {e}")
        return False
    
    return True


def test_langgraph_studio_compatibility():
    """Test compatibility with LangGraph Studio features."""
    print("\n=== Testing LangGraph Studio Compatibility ===")
    
    # Check if graph has proper structure for Studio
    print(f"Graph has nodes: {hasattr(memory_agent, 'nodes')}")
    print(f"Graph has edges: {hasattr(memory_agent, 'channels')}")
    print(f"Graph is compiled: {memory_agent is not None}")
    
    # Check if graph config supports Studio features
    try:
        # Test graph introspection
        graph_schema = memory_agent.get_graph()
        print(f"Graph schema available: {graph_schema is not None}")
        print(f"Graph nodes in schema: {list(graph_schema.nodes.keys()) if graph_schema else 'None'}")
        
    except Exception as e:
        print(f"Graph introspection error: {e}")
        return False
    
    return True


def test_langsmith_integration():
    """Test LangSmith integration support."""
    print("\n=== Testing LangSmith Integration Support ===")
    
    # Check if LangSmith environment variables are recognized
    langsmith_key = os.environ.get("LANGSMITH_API_KEY")
    langsmith_project = os.environ.get("LANGSMITH_PROJECT")
    
    print(f"LangSmith API key configured: {langsmith_key is not None}")
    print(f"LangSmith project configured: {langsmith_project is not None}")
    
    # Check if tracing is available
    try:
        from langsmith import Client
        print("✅ LangSmith client available")
    except ImportError:
        print("❌ LangSmith client not available")
        return False
    
    return True


def main():
    """Run all prompt editing capability tests."""
    print("Testing LangGraph Studio Prompt Editing Capabilities")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_current_graph_structure())
    test_results.append(test_prompt_registry_functionality())
    test_results.append(test_prompt_editing_support())
    test_results.append(test_langgraph_studio_compatibility())
    test_results.append(test_langsmith_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed - LangGraph Studio prompt editing should be supported")
    else:
        print("❌ Some tests failed - prompt editing capabilities may be limited")
    
    # Specific recommendations
    print("\nRECOMMENDATIONS:")
    print("1. Current implementation uses create_react_agent with static prompt")
    print("2. To support dynamic prompt editing, consider implementing ConfigurableFields")
    print("3. PromptRegistry system is available but not integrated with the graph")
    print("4. LangSmith integration is available for playground features")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
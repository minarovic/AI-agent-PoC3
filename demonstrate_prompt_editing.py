#!/usr/bin/env python3
"""
Demonstration of LangGraph Studio prompt editing capabilities.

This script shows practical examples of how to edit prompts using both
supported methods: direct node editing and LangSmith Playground integration.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set API key for demonstration (only if not in CI environment)
if not (os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"):
    os.environ["OPENAI_API_KEY"] = "dummy_key_for_testing"

from memory_agent.graph import memory_agent, create_memory_agent
from memory_agent.prompts import PromptRegistry, SYSTEM_PROMPT


def demonstrate_direct_prompt_editing():
    """Demonstrate direct prompt editing through PromptRegistry."""
    print("=== Direct Prompt Editing Demonstration ===")
    
    # Show current system prompt
    current_prompt = PromptRegistry.get_prompt("system_prompt")
    print(f"📝 Current system prompt (first 100 chars):")
    print(f"   {current_prompt[:100]}...")
    
    # Create different prompt variations for different use cases
    prompt_variations = {
        "financial_analyst": """You are a senior financial analyst with expertise in:
- Financial statement analysis and ratio calculations
- Risk assessment and credit evaluation  
- Investment recommendations and portfolio analysis
- Market trend analysis and forecasting

Provide detailed financial insights with specific metrics and recommendations.""",

        "compliance_officer": """You are a compliance and risk management officer specializing in:
- Regulatory compliance assessment
- Anti-money laundering (AML) monitoring
- Sanctions and embargo screening
- Corporate governance evaluation

Focus on identifying compliance risks and regulatory violations.""",

        "market_researcher": """You are a market research analyst focused on:
- Competitive landscape analysis
- Market share and positioning assessment
- Industry trend identification
- Customer and supplier relationship mapping

Provide strategic market insights and competitive intelligence."""
    }
    
    print(f"\n🔄 Available prompt variations:")
    for name, prompt in prompt_variations.items():
        print(f"   - {name}: {prompt[:60]}...")
    
    # Demonstrate switching between prompts
    print(f"\n🔧 Switching to financial analyst mode...")
    PromptRegistry.update_prompt("system_prompt", prompt_variations["financial_analyst"])
    
    # Create new agent with updated prompt
    updated_agent = create_memory_agent()
    print(f"✅ Agent recreated with financial analyst prompt")
    
    # Show the change took effect
    new_prompt = PromptRegistry.get_prompt("system_prompt")
    print(f"📝 Updated prompt (first 100 chars):")
    print(f"   {new_prompt[:100]}...")
    
    # Restore original prompt
    PromptRegistry.update_prompt("system_prompt", current_prompt)
    print(f"🔄 Original prompt restored")
    
    return True


def demonstrate_configurable_fields():
    """Demonstrate ConfigurableField usage for runtime prompt customization."""
    print("\n=== ConfigurableField Demonstration ===")
    
    # Show configuration schema
    from memory_agent.graph_with_configurable_prompts import get_agent_configuration_schema
    
    schema = get_agent_configuration_schema()
    print(f"📋 Available configuration fields:")
    for field, config in schema["configurable"].items():
        print(f"   - {field}: {config.get('description', 'No description')}")
    
    # Create example configurations for different scenarios
    configurations = {
        "executive_briefing": {
            "configurable": {
                "system_prompt": "Provide executive-level briefings with key insights, strategic implications, and actionable recommendations. Keep responses concise and business-focused.",
                "analysis_style": "executive",
                "temperature": 0.1,
                "model_name": "gpt-4"
            }
        },
        "detailed_analysis": {
            "configurable": {
                "system_prompt": "Conduct thorough, detailed analysis with comprehensive data examination, multiple perspectives, and in-depth explanations.",
                "analysis_style": "detailed", 
                "temperature": 0.2,
                "model_name": "gpt-4"
            }
        },
        "risk_focused": {
            "configurable": {
                "system_prompt": "Focus specifically on risk identification, assessment, and mitigation strategies. Highlight potential problems and compliance issues.",
                "analysis_style": "technical",
                "temperature": 0.0,
                "model_name": "gpt-4"
            }
        }
    }
    
    print(f"\n🎯 Example configurations:")
    for name, config in configurations.items():
        print(f"\n   {name.upper()}:")
        print(f"   └─ Prompt: {config['configurable']['system_prompt'][:80]}...")
        print(f"   └─ Style: {config['configurable']['analysis_style']}")
        print(f"   └─ Temperature: {config['configurable']['temperature']}")
    
    # Show how these would be used in practice
    print(f"\n💡 Usage example:")
    print(f"""
    # In LangGraph Studio or runtime:
    result = agent.invoke(
        {{"messages": [{{"role": "user", "content": "Analyze MB TOOL"}}]}},
        config=configurations["executive_briefing"]
    )
    """)
    
    return True


def demonstrate_langsmith_integration():
    """Demonstrate LangSmith Playground integration setup."""
    print("\n=== LangSmith Playground Integration Demonstration ===")
    
    # Show environment setup
    print(f"🔧 Environment setup for LangSmith:")
    
    env_vars = {
        "LANGCHAIN_TRACING_V2": "true",
        "LANGSMITH_API_KEY": "your_langsmith_api_key_here",
        "LANGSMITH_PROJECT": "memory-agent-prompt-testing",
        "LANGCHAIN_ENDPOINT": "https://api.smith.langchain.com",
    }
    
    for var, value in env_vars.items():
        current = os.environ.get(var, "Not set")
        print(f"   export {var}={value}")
        print(f"   Current: {current}")
    
    # Show trace configuration
    print(f"\n📊 Trace configuration:")
    trace_config = {
        "project_name": "memory-agent-prompt-testing",
        "tags": ["prompt-editing", "memory-agent"],
        "metadata": {
            "purpose": "Prompt optimization",
            "version": "1.0",
            "agent_type": "business_intelligence"
        }
    }
    
    print(json.dumps(trace_config, indent=2))
    
    # Show playground workflow
    print(f"\n🎮 Playground workflow:")
    workflow_steps = [
        "1. Run agent with tracing enabled",
        "2. Agent execution creates trace in LangSmith",
        "3. Open trace in LangSmith web interface",
        "4. Click 'Open in Playground'",
        "5. Edit prompts, test variations",
        "6. Compare results side-by-side",
        "7. Export optimal prompts to code"
    ]
    
    for step in workflow_steps:
        print(f"   {step}")
    
    return True


def demonstrate_prompt_editing_workflow():
    """Demonstrate complete prompt editing workflow."""
    print("\n=== Complete Prompt Editing Workflow ===")
    
    print(f"🔄 Recommended workflow for prompt optimization:")
    
    workflow = {
        "phase_1_discovery": {
            "description": "Initial prompt exploration",
            "steps": [
                "Start with default system prompt",
                "Test with sample company data",
                "Identify areas for improvement",
                "Note specific issues or gaps"
            ]
        },
        "phase_2_experimentation": {
            "description": "LangSmith Playground experimentation",
            "steps": [
                "Enable LangSmith tracing",
                "Run multiple test cases",
                "Open traces in Playground",
                "Try different prompt variations",
                "Test edge cases and error scenarios"
            ]
        },
        "phase_3_refinement": {
            "description": "Studio direct editing refinement",
            "steps": [
                "Use best prompts from Playground",
                "Test in full graph context",
                "Make incremental adjustments",
                "Validate with different input types"
            ]
        },
        "phase_4_deployment": {
            "description": "Production deployment",
            "steps": [
                "Update PromptRegistry with final versions",
                "Configure default settings",
                "Set up runtime configurability",
                "Deploy to LangGraph Platform"
            ]
        }
    }
    
    for phase, details in workflow.items():
        print(f"\n   📌 {phase.upper().replace('_', ' ')}")
        print(f"      {details['description']}")
        for step in details['steps']:
            print(f"      • {step}")
    
    return True


def create_practical_examples():
    """Create practical examples for different use cases."""
    print("\n=== Practical Examples ===")
    
    examples = {
        "startup_analysis": {
            "description": "Analyzing early-stage startups",
            "system_prompt": """You are a venture capital analyst specializing in startup evaluation.
Focus on:
- Business model viability and scalability
- Market opportunity and competitive advantages  
- Team capability and execution track record
- Financial projections and funding requirements
- Risk factors specific to early-stage companies

Provide investment-focused insights with clear recommendations.""",
            "use_case": "VC firms, angel investors, startup accelerators"
        },
        
        "supply_chain_analysis": {
            "description": "Supply chain risk assessment",
            "system_prompt": """You are a supply chain risk analyst focusing on:
- Supplier financial stability and reliability
- Geographic and geopolitical risks
- Regulatory compliance across jurisdictions
- Business continuity and contingency planning
- Cost optimization and efficiency opportunities

Emphasize supply chain vulnerabilities and mitigation strategies.""",
            "use_case": "Manufacturing companies, procurement teams"
        },
        
        "m_and_a_analysis": {
            "description": "Mergers and acquisitions due diligence",
            "system_prompt": """You are an M&A analyst conducting due diligence.
Evaluate:
- Strategic fit and synergy opportunities
- Financial performance and valuation metrics
- Cultural compatibility and integration challenges
- Regulatory approval requirements
- Post-merger integration planning

Provide acquisition-focused recommendations with risk assessment.""",
            "use_case": "Investment banks, corporate development teams"
        }
    }
    
    for name, example in examples.items():
        print(f"\n📈 {name.upper().replace('_', ' ')}")
        print(f"   Purpose: {example['description']}")
        print(f"   Use case: {example['use_case']}")
        print(f"   Prompt: {example['system_prompt'][:100]}...")
    
    # Show how to apply these
    print(f"\n💼 How to apply these examples:")
    print(f"""
    # Update system prompt for startup analysis:
    PromptRegistry.update_prompt("system_prompt", examples["startup_analysis"]["system_prompt"])
    
    # Or use as configuration:
    config = {{
        "configurable": {{
            "system_prompt": examples["supply_chain_analysis"]["system_prompt"],
            "analysis_style": "technical"
        }}
    }}
    """)
    
    return True


def main():
    """Run complete demonstration of prompt editing capabilities."""
    print("LangGraph Studio Prompt Editing Demonstration")
    print("=" * 60)
    print("This demonstration shows how to edit prompts using both supported methods:")
    print("1. Direct node editing via PromptRegistry")  
    print("2. LangSmith Playground integration")
    print("=" * 60)
    
    # Run all demonstrations
    demonstrations = [
        ("Direct Prompt Editing", demonstrate_direct_prompt_editing),
        ("ConfigurableField Usage", demonstrate_configurable_fields),
        ("LangSmith Integration", demonstrate_langsmith_integration),
        ("Complete Workflow", demonstrate_prompt_editing_workflow),
        ("Practical Examples", create_practical_examples),
    ]
    
    results = []
    for name, demo_func in demonstrations:
        try:
            result = demo_func()
            results.append((name, result))
            print(f"\n✅ {name} completed successfully")
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMONSTRATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Completed demonstrations: {successful}/{total}")
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Set up LangSmith account and API key")
    print(f"2. Deploy agent to LangGraph Platform")
    print(f"3. Open LangGraph Studio")
    print(f"4. Start editing prompts using demonstrated methods")
    print(f"5. Refer to docs/langgraph_studio_prompt_editing.md for detailed guidance")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
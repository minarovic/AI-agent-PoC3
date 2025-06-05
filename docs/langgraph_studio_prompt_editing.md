# LangGraph Studio Prompt Editing Capabilities

This document explains how to edit prompts in LangGraph Studio for the Memory Agent using two supported methods.

## Overview

LangGraph Studio supports two primary approaches for editing and iterating on prompts:

1. **Direct Node Editing** - Edit prompts directly in the Studio interface
2. **LangSmith Playground Integration** - Use LangSmith Playground for advanced prompt experimentation

## Method 1: Direct Node Editing

### Description
Edit prompts directly within the LangGraph Studio interface by modifying node configurations.

### How to Use

1. **Open LangGraph Studio**
   ```bash
   # Start LangGraph Studio (requires LangGraph Cloud/Platform)
   langgraph studio
   ```

2. **Load Your Graph**
   - Load the `memory_agent` graph from `langgraph.json`
   - The graph will appear with nodes: `__start__`, `agent`, `tools`

3. **Select Node for Editing**
   - Click on the `agent` node which contains the main prompt
   - The node editor will show the current configuration

4. **Modify Prompt Text**
   - Locate the prompt configuration in the node
   - Edit the system prompt directly in the interface
   - Changes are applied immediately for testing

5. **Save and Test**
   - Save changes (they persist for the session)
   - Test the modified prompt with sample inputs
   - Observe changes in agent behavior

### Supported Configurations

The agent supports the following configurable fields:

- **system_prompt**: Main system prompt defining agent behavior
- **model_name**: OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- **temperature**: Response generation temperature (0.0-1.0)
- **analysis_style**: Style of analysis (detailed, summary, technical, executive)

### Limitations

- Changes are session-based and temporary
- To make changes permanent, update the code
- Requires graph restart to apply permanently

## Method 2: LangSmith Playground Integration

### Description
Use LangSmith Playground for sophisticated prompt experimentation and testing.

### Setup

1. **Enable LangSmith Tracing**
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGSMITH_API_KEY=your_langsmith_api_key
   export LANGSMITH_PROJECT=memory-agent-dev
   ```

2. **Configure Agent for Tracing**
   ```python
   # This is already configured in the agent
   # Just ensure environment variables are set
   ```

### How to Use

1. **Run Agent with Tracing**
   ```python
   from memory_agent.graph import memory_agent
   
   # Run agent - traces will appear in LangSmith
   result = memory_agent.invoke({
       "messages": [{"role": "user", "content": "Analyze company MB TOOL"}]
   })
   ```

2. **Open Trace in LangSmith**
   - Go to LangSmith web interface
   - Find your trace in the project
   - Click on the trace to view details

3. **Edit in Playground**
   - Click "Open in Playground" from the trace
   - Modify prompts, model settings, or input data
   - Test variations instantly

4. **Experiment with Variations**
   - Try different system prompts
   - Test various analysis styles
   - Compare model responses
   - Export successful configurations

5. **Export to Code**
   - Once you find optimal prompts, export them
   - Update `src/memory_agent/prompts.py` with new versions
   - Use PromptRegistry to manage changes

### Advanced Configuration

```python
# Example configuration for testing in Playground
config = {
    "configurable": {
        "system_prompt": "You are a financial risk analyst...",
        "model_name": "gpt-4",
        "temperature": 0.2,
        "analysis_style": "executive"
    }
}

# Use with agent
result = memory_agent.invoke(input_data, config=config)
```

## Recommended Workflow

1. **Initial Development**
   - Use LangSmith Playground for rapid experimentation
   - Test multiple prompt variations with real data
   - Identify best-performing prompts

2. **Refinement**
   - Use Studio direct editing for quick tweaks
   - Test in context of full graph execution
   - Validate with different input types

3. **Production Deployment**
   - Update `PromptRegistry` with finalized prompts
   - Use `ConfigurableField` for runtime customization
   - Deploy to LangGraph Platform

4. **Ongoing Optimization**
   - Monitor performance in LangSmith
   - A/B test prompt variations
   - Iterate based on user feedback

## Code Integration

### PromptRegistry Usage

```python
from memory_agent.prompts import PromptRegistry

# View current prompt
current = PromptRegistry.get_prompt("system_prompt")
print(current)

# Update prompt
new_prompt = "You are an expert business analyst..."
PromptRegistry.update_prompt("system_prompt", new_prompt)

# Add new prompt type
PromptRegistry.add_prompt("risk_analysis", "Focus on risk factors...")
```

### ConfigurableField Usage

```python
from langchain_core.runnables import ConfigurableField

# Create configurable component
configurable_llm = ChatOpenAI().configurable_fields(
    model_name=ConfigurableField(id="model"),
    temperature=ConfigurableField(id="temp")
)

# Use with configuration
config = {"configurable": {"model": "gpt-4", "temp": 0.1}}
response = configurable_llm.invoke(messages, config=config)
```

## Verification

To verify that prompt editing capabilities are working:

```bash
# Run verification script
python verify_prompt_editing_capabilities.py
```

This script tests:
- Direct node editing support
- LangSmith integration
- ConfigurableField functionality
- Graph compatibility with Studio
- Complete prompt editing workflow

## Troubleshooting

### Common Issues

1. **Studio not showing graph**
   - Verify `langgraph.json` configuration
   - Check that graph is properly compiled
   - Ensure all dependencies are installed

2. **LangSmith traces not appearing**
   - Check environment variables are set
   - Verify API key is valid
   - Ensure project name matches

3. **Configuration not applying**
   - Verify ConfigurableField IDs match
   - Check configuration format
   - Ensure agent supports the field

### Support

For additional support:
- Check LangGraph documentation
- Review LangSmith Playground guides
- Consult Memory Agent implementation details

## Examples

### Example 1: Business Analysis Focus

```python
config = {
    "configurable": {
        "system_prompt": """You are a business intelligence analyst specializing in:
        - Market analysis and competitive positioning
        - Financial performance evaluation  
        - Strategic recommendations
        
        Provide actionable insights based on available data.""",
        "analysis_style": "executive",
        "temperature": 0.1
    }
}
```

### Example 2: Risk Assessment Focus

```python
config = {
    "configurable": {
        "system_prompt": """You are a risk management specialist focusing on:
        - Compliance and regulatory risks
        - Financial stability assessment
        - Supply chain vulnerabilities
        
        Highlight potential risks and mitigation strategies.""",
        "analysis_style": "technical",
        "temperature": 0.0
    }
}
```

This documentation provides comprehensive guidance for using both LangGraph Studio prompt editing methods effectively.
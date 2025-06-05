"""
Test for node-specific assistant settings.

Validates that the Memory Agent has proper assistant settings for individual nodes
as required by LangGraph Studio.
"""

import os
from unittest.mock import patch

import pytest


def test_node_assistant_settings_available():
    """Test that node assistant settings are available."""
    # Mock environment variable to avoid API key requirement
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        from memory_agent.graph import get_node_assistant_settings

        settings = get_node_assistant_settings()

        # Verify we have assistant settings
        assert isinstance(settings, dict)
        assert len(settings) > 0

        # Check that main_agent configuration exists
        assert "main_agent" in settings
        main_config = settings["main_agent"]

        # Verify required fields
        assert "model" in main_config
        assert "temperature" in main_config
        assert "system_prompt" in main_config
        assert "tools" in main_config
        assert "description" in main_config


def test_studio_config_format():
    """Test that studio configuration has the correct format."""
    from memory_agent.node_config import export_studio_config, validate_node_configs

    # Validate node configurations
    validation = validate_node_configs()
    assert (
        validation["valid"] is True
    ), f"Node config validation failed: {validation['errors']}"

    # Export studio config
    studio_config = export_studio_config()

    # Verify structure
    assert "nodes" in studio_config
    assert "assistants" in studio_config
    assert "metadata" in studio_config

    # Verify we have at least one node
    assert len(studio_config["nodes"]) > 0
    assert len(studio_config["assistants"]) > 0


def test_node_config_validation():
    """Test that node configurations are valid."""
    from memory_agent.node_config import list_configured_nodes, validate_node_configs

    # Get list of configured nodes
    nodes = list_configured_nodes()
    assert len(nodes) > 0

    # Validate configurations
    result = validate_node_configs()
    assert result["valid"] is True
    assert result["node_count"] > 0
    assert len(result["errors"]) == 0


def test_assistant_config_structure():
    """Test that assistant configurations have proper structure."""
    from memory_agent.node_config import NODE_CONFIGURATIONS

    for node_name, config in NODE_CONFIGURATIONS.items():
        # Check NodeConfig structure
        assert hasattr(config, "name")
        assert hasattr(config, "description")
        assert hasattr(config, "assistant")
        assert hasattr(config, "metadata")

        # Check AssistantConfig structure
        assistant = config.assistant
        assert hasattr(assistant, "model")
        assert hasattr(assistant, "temperature")
        assert hasattr(assistant, "system_prompt")
        assert hasattr(assistant, "tools")

        # Validate values
        assert isinstance(assistant.model, str)
        assert ":" in assistant.model  # Should be in format "provider:model"
        assert 0.0 <= assistant.temperature <= 2.0
        assert isinstance(assistant.tools, list)


def test_memory_agent_has_node_settings():
    """Test that memory agent instance has node settings attached."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        try:
            from memory_agent.graph import memory_agent

            if memory_agent is not None:
                # Check if node assistant settings are attached
                assert hasattr(memory_agent, "_node_assistant_settings")
                assert hasattr(memory_agent, "_studio_node_config")

                settings = memory_agent._node_assistant_settings
                assert isinstance(settings, dict)
                assert len(settings) > 0

        except Exception as e:
            # If agent can't be created due to missing API key, that's OK for this test
            if "OPENAI_API_KEY" not in str(e):
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

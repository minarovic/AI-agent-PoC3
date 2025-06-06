"""
Tests for explicit StateGraph workflow implementation.

Tests verify that the explicit StateGraph workflow works correctly
for all supported analysis types and handles errors appropriately.
"""

import pytest
from langchain_core.messages import HumanMessage

from src.memory_agent.graph_stategraph import create_explicit_stategraph
from src.memory_agent.state import State


class TestExplicitStateGraph:
    """Test suite for explicit StateGraph workflow."""

    def test_create_explicit_stategraph(self):
        """Test that create_explicit_stategraph creates a valid graph."""
        graph = create_explicit_stategraph()
        
        assert graph is not None
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'stream')

    def test_general_analysis_workflow(self):
        """Test general analysis workflow."""
        graph = create_explicit_stategraph()
        
        test_state = State(
            messages=[HumanMessage(content='Tell me about MB TOOL')],
            current_query='Tell me about MB TOOL'
        )
        
        result = graph.invoke(test_state)
        
        # Check that result contains output
        assert 'output' in result
        assert result['output'] is not None
        
        output = result['output']
        assert output['status'] == 'completed'
        assert output['analysis_type'] == 'general'
        assert output['company_name'] == 'MB TOOL'
        assert 'summary' in output
        assert 'data_quality' in output

    def test_risk_analysis_workflow(self):
        """Test risk analysis workflow."""
        graph = create_explicit_stategraph()
        
        test_state = State(
            messages=[HumanMessage(content='Analyze risks for MB TOOL')],
            current_query='Analyze risks for MB TOOL'
        )
        
        result = graph.invoke(test_state)
        
        # Check that result contains output
        assert 'output' in result
        assert result['output'] is not None
        
        output = result['output']
        assert output['status'] == 'completed'
        assert output['analysis_type'] == 'risk_comparison'
        assert output['company_name'] == 'MB TOOL'

    def test_supplier_analysis_workflow(self):
        """Test supplier analysis workflow."""
        graph = create_explicit_stategraph()
        
        test_state = State(
            messages=[HumanMessage(content='Show me suppliers of MB TOOL')],
            current_query='Show me suppliers of MB TOOL'
        )
        
        result = graph.invoke(test_state)
        
        # Check that result contains output
        assert 'output' in result
        assert result['output'] is not None
        
        output = result['output']
        assert output['status'] == 'completed'
        assert output['analysis_type'] == 'supplier_analysis'
        assert output['company_name'] == 'MB TOOL'

    def test_error_handling(self):
        """Test error handling in workflow."""
        graph = create_explicit_stategraph()
        
        # Test with empty query that should cause errors
        test_state = State(
            messages=[HumanMessage(content='')],
            current_query=''
        )
        
        result = graph.invoke(test_state)
        
        # Should have some output even for errors
        assert 'output' in result or 'error_state' in result

    def test_workflow_maintains_state(self):
        """Test that workflow correctly maintains and updates state."""
        graph = create_explicit_stategraph()
        
        test_state = State(
            messages=[HumanMessage(content='Tell me about MB TOOL')],
            current_query='Tell me about MB TOOL'
        )
        
        result = graph.invoke(test_state)
        
        # Check that key state fields are preserved/updated
        assert 'current_query' in result
        assert 'analysis_type' in result
        assert 'company_name' in result
        assert result['company_name'] == 'MB TOOL'

    def test_deterministic_flow(self):
        """Test that the workflow follows deterministic flow without LLM tool calls."""
        graph = create_explicit_stategraph()
        
        # Run the same query multiple times - should get consistent results
        test_state = State(
            messages=[HumanMessage(content='Tell me about MB TOOL')],
            current_query='Tell me about MB TOOL'
        )
        
        result1 = graph.invoke(test_state)
        result2 = graph.invoke(test_state)
        
        # Results should be consistent (same analysis type, company name)
        assert result1['analysis_type'] == result2['analysis_type']
        assert result1['company_name'] == result2['company_name']
        assert result1['output']['status'] == result2['output']['status']
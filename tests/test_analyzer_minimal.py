# tests/test_analyzer_minimal.py - NOVÝ TEST
"""Test minimální funkcionality pro LangGraph deployment."""

import os
import sys

# Přidání src do pythonpath pro import
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from memory_agent.analyzer import analyze_company_query


def test_company_extraction_simple():
    """Test že analyzer zvládne jednoduchou větu."""
    test_cases = [
        ("MB TOOL", "MB TOOL"),
        ("Tell me about MB TOOL", "MB TOOL"),
        ("What is BOS AUTOMOTIVE", "BOS AUTOMOTIVE"),
    ]

    for input_text, expected in test_cases:
        company, analysis_type = analyze_company_query(input_text)
        assert company == expected
        assert analysis_type == "general"

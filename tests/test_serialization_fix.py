"""
Tests for MapComposite serialization fix.

This module tests the fix for the serialization issue with proto.marshal.collections.maps.MapComposite 
objects that can occur when external libraries return dict-like objects that aren't actual dicts.
"""

import json
import pytest
from typing import Any, Dict

from memory_agent.state import merge_dict_values, ensure_serializable, State


class MockMapComposite:
    """
    Mock class to simulate proto.marshal.collections.maps.MapComposite
    objects that cause serialization issues.
    """
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def items(self):
        """Simulate dict-like interface"""
        return self._data.items()
    
    def keys(self):
        """Simulate dict-like interface"""
        return self._data.keys()
    
    def values(self):
        """Simulate dict-like interface"""
        return self._data.values()
    
    def get(self, key, default=None):
        """Simulate dict-like interface"""
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        """Simulate dict-like interface"""
        return self._data[key]
    
    def __contains__(self, key):
        """Simulate dict-like interface"""
        return key in self._data
    
    def copy(self):
        """This method exists but returns another MapComposite"""
        return MockMapComposite(self._data.copy())
    
    def __repr__(self):
        return f"MockMapComposite({self._data})"


class TestSerializationFix:
    """Test the serialization fix for MapComposite objects."""
    
    def test_mapcomposite_not_json_serializable(self):
        """Test that MockMapComposite objects fail JSON serialization."""
        map_composite = MockMapComposite({"key": "value", "number": 42})
        
        with pytest.raises(TypeError, match="not JSON serializable"):
            json.dumps(map_composite)
    
    def test_regular_dict_json_serializable(self):
        """Test that regular dicts work with JSON serialization."""
        regular_dict = {"key": "value", "number": 42}
        
        # Should not raise any exception
        json_str = json.dumps(regular_dict)
        assert isinstance(json_str, str)
    
    def test_merge_dict_values_with_mapcomposite_left(self):
        """Test merge_dict_values with MapComposite as left parameter."""
        map_composite = MockMapComposite({"existing": "value"})
        right_dict = {"new_key": "new_value"}
        
        result = merge_dict_values(map_composite, right_dict)
        
        # Should return a regular dict
        assert isinstance(result, dict)
        assert result["existing"] == "value"
        assert result["new_key"] == "new_value"
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_merge_dict_values_with_mapcomposite_right(self):
        """Test merge_dict_values with MapComposite as right parameter."""
        left_dict = {"existing": "value"}
        map_composite = MockMapComposite({"new_key": "new_value"})
        
        result = merge_dict_values(left_dict, map_composite)
        
        # Should return a regular dict
        assert isinstance(result, dict)
        assert result["existing"] == "value"
        assert result["new_key"] == "new_value"
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_merge_dict_values_with_both_mapcomposite(self):
        """Test merge_dict_values with both parameters as MapComposite."""
        left_composite = MockMapComposite({"left": "value"})
        right_composite = MockMapComposite({"right": "value"})
        
        result = merge_dict_values(left_composite, right_composite)
        
        # Should return a regular dict
        assert isinstance(result, dict)
        assert result["left"] == "value"
        assert result["right"] == "value"
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_ensure_serializable_simple_mapcomposite(self):
        """Test ensure_serializable with simple MapComposite."""
        map_composite = MockMapComposite({"key": "value"})
        
        result = ensure_serializable(map_composite)
        
        assert isinstance(result, dict)
        assert result["key"] == "value"
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_ensure_serializable_nested_structure(self):
        """Test ensure_serializable with nested structures containing MapComposite."""
        nested_data = {
            "regular_key": "regular_value",
            "map_composite_key": MockMapComposite({"nested": "value"}),
            "list_with_map": [
                {"normal": "dict"},
                MockMapComposite({"another": "map"})
            ],
            "tuple_with_map": (
                "normal_item",
                MockMapComposite({"tuple_map": "value"})
            )
        }
        
        result = ensure_serializable(nested_data)
        
        # Should be a regular dict
        assert isinstance(result, dict)
        
        # Nested MapComposite should be converted to dict
        assert isinstance(result["map_composite_key"], dict)
        assert result["map_composite_key"]["nested"] == "value"
        
        # List items should be processed
        assert isinstance(result["list_with_map"][1], dict)
        assert result["list_with_map"][1]["another"] == "map"
        
        # Tuple should be converted to list, items processed
        assert isinstance(result["tuple_with_map"], list)
        assert isinstance(result["tuple_with_map"][1], dict)
        assert result["tuple_with_map"][1]["tuple_map"] == "value"
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_ensure_serializable_preserves_regular_types(self):
        """Test that ensure_serializable preserves regular Python types."""
        data = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        result = ensure_serializable(data)
        
        # Should preserve all regular types
        assert result["string"] == "value"
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["bool"] is True
        assert result["none"] is None
        assert result["list"] == [1, 2, 3]
        assert result["dict"] == {"nested": "value"}
        
        # Should be JSON serializable
        json.dumps(result)  # Should not raise
    
    def test_graph_nodes_return_serializable_data(self):
        """Test that graph nodes return serializable data."""
        from memory_agent.graph_nodes import determine_analysis_type, route_query
        
        # Create test state
        test_state = State(
            messages=[],
            current_query="Tell me about MB TOOL supplier risks"
        )
        
        # Test determine_analysis_type
        result = determine_analysis_type(test_state)
        assert isinstance(result, dict)
        json.dumps(result)  # Should not raise
        
        # Test route_query  
        result = route_query(test_state)
        assert isinstance(result, dict)
        json.dumps(result)  # Should not raise
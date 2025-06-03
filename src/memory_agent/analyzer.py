"""
Minimální analyzer pro Memory Agent podle LangGraph dokumentace.
Pouze jedna tool funkce pro načítání company dat.
"""
from typing import Dict, Any
import json
from .tools import MockMCPConnector


def analyze_company(query: str) -> str:
    """
    Analyze company data and return structured information.
    
    Args:
        query: User query about company
        
    Returns:
        JSON string with company analysis results
    """
    try:
        # Inicializace mock MCP connectoru
        connector = MockMCPConnector()
        
        # Načtení dat pomocí různých metod podle potřeby
        company_data = connector.get_company_by_name(query)
        
        # Získání ID společnosti pro další dotazy
        company_id = company_data.get("id") if company_data else None
        
        internal_data = {}
        relationships_data = []
        
        if company_id:
            try:
                internal_data = connector.get_company_financials(company_id)
            except Exception:
                internal_data = {"message": "Financial data not available"}
                
            try:
                relationships_data = connector.get_company_relationships(company_id)
            except Exception:
                relationships_data = []
        
        # Strukturované vrácení dat
        result = {
            "query_type": "company",
            "company_data": company_data,
            "internal_data": internal_data,
            "relationships_data": relationships_data,
            "analysis_complete": True,
            "query": query
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "query_type": "company",
                "analysis_type": "general",
                "analysis_complete": False,
                "query": query,
            }
        )

import logging
import os
from typing import Optional, Any

# LangChain Core imports
from langchain_core.runnables import RunnableConfig
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

# Initialize Anthropic LLM globally
def get_anthropic_llm():
    """Initialize Anthropic LLM with API key from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not found in environment, using fallback")
        return None
    
    try:
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=api_key,
            temperature=0
        )
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic LLM: {e}")
        return None

# Fallback function for company name extraction using simple regex
def extract_company_fallback(query: str) -> str:
    """Fallback company extraction using simple patterns."""
    import re
    
    # Known companies mapping
    known_companies = {
        "MB TOOL": "MB TOOL",
        "ŠKODA AUTO": "ŠKODA AUTO", 
        "ADIS TACHOV": "ADIS TACHOV",
        "Flídr plast": "Flídr plast",
        "BOS AUTOMOTIVE": "BOS AUTOMOTIVE",
        "BOS": "BOS",
        "FLIDR": "FLIDR",
        "Adis": "Adis",
        "Škoda": "Škoda"
    }
    
    # Check known companies first
    for company in known_companies:
        if company.lower() in query.lower():
            return company
    
    # Simple regex for company-like names (capitalized words)
    pattern = r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\b'
    matches = re.findall(pattern, query)
    
    if matches:
        return matches[0]
    
    return "Unknown Company"

def determine_analysis_type_fallback(query: str) -> str:
    """Fallback analysis type detection using keywords."""
    query_lower = query.lower()
    
    # Risk comparison keywords
    risk_keywords = ["risk", "rizik", "compliance", "sankce", "sanctions"]
    if any(keyword in query_lower for keyword in risk_keywords):
        return "risk_comparison"
    
    # Supplier analysis keywords  
    supplier_keywords = ["supplier", "dodavatel", "supply chain", "vztahy"]
    if any(keyword in query_lower for keyword in supplier_keywords):
        return "supplier_analysis"
    
    # Default to general
    return "general"

def analyze_company_query(query: str) -> tuple[str, str]:
    """
    Analyze query to extract company name and analysis type using LLM.
    Falls back to regex if LLM is unavailable.
    
    Args:
        query: User query to analyze
        
    Returns:
        Tuple of (company_name, analysis_type)
    """
    llm = get_anthropic_llm()
    
    if llm is None:
        logger.warning("LLM not available, using fallback method")
        company = extract_company_fallback(query)
        analysis_type = determine_analysis_type_fallback(query)
        return company, analysis_type
    
    try:
        # Create LLM prompt for analysis
        system_message = SystemMessage(content="""You are an expert at analyzing business queries. 
Your task is to extract the company name and determine the analysis type from user queries.

Return your response in this EXACT format:
Company Name; analysis_type

Where analysis_type must be one of: risk_comparison, supplier_analysis, general

Examples:
- "What are the risks of MB TOOL company?" → "MB TOOL; risk_comparison"
- "Tell me about supplier relationships with BOS" → "BOS; supplier_analysis"
- "General information about Škoda Auto" → "Škoda Auto; general"

If no clear company name is found, use "Unknown Company".
If unsure about analysis type, use "general".""")
        
        human_message = HumanMessage(content=f"Analyze this query: {query}")
        
        # Get LLM response
        response = llm.invoke([system_message, human_message])
        result = response.content.strip()
        
        # Parse response
        if ";" in result:
            parts = result.split(";", 1)
            company = parts[0].strip()
            analysis_type = parts[1].strip()
            
            # Validate analysis type
            valid_types = ["risk_comparison", "supplier_analysis", "general"]
            if analysis_type not in valid_types:
                analysis_type = "general"
                
            logger.info(f"LLM analysis: company='{company}', type='{analysis_type}'")
            return company, analysis_type
        else:
            logger.warning(f"LLM returned unexpected format: {result}")
            # Fall back to regex method
            company = extract_company_fallback(query)
            analysis_type = determine_analysis_type_fallback(query)
            return company, analysis_type
            
    except Exception as e:
        logger.error(f"Error in LLM analysis: {e}, falling back to regex")
        company = extract_company_fallback(query)
        analysis_type = determine_analysis_type_fallback(query)
        return company, analysis_type

def analyze_query_sync(
    user_input: str,
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = None,
    mcp_connector: Any = None
) -> str:
    """
    Analyze query type for LangGraph workflow.
    Always returns "company" for company-related queries.
    
    Args:
        user_input: User query
        config: Not used
        model: Not used  
        mcp_connector: Not used
        
    Returns:
        Query type: "company", "person", "relationship", "custom", or "error"
    """
    if not user_input or not user_input.strip():
        logger.warning("Empty query provided")
        return "error"
    
    try:
        # For LangGraph workflow, we primarily handle company queries
        # Use LLM to determine if this is a company-related query
        llm = get_anthropic_llm()
        
        if llm is None:
            # Fallback: simple keyword detection
            query_lower = user_input.lower()
            company_indicators = ["company", "společnost", "firma", "corporation", "s.r.o.", "a.s."]
            if any(indicator in query_lower for indicator in company_indicators):
                return "company"
            return "custom"
        
        try:
            system_message = SystemMessage(content="""Determine if this query is about a company/business entity.
Return only: "company" or "other"

Company queries include:
- Questions about specific companies
- Business analysis requests
- Corporate information queries
- Risk or supplier analysis

Other queries include:
- Personal information requests
- General questions not about businesses
- Technical or procedural questions""")
            
            human_message = HumanMessage(content=f"Classify this query: {user_input}")
            
            response = llm.invoke([system_message, human_message])
            result = response.content.strip().lower()
            
            if "company" in result:
                logger.info(f"LLM classified as company query: {user_input[:50]}...")
                return "company"
            else:
                logger.info(f"LLM classified as non-company query: {user_input[:50]}...")
                return "custom"
                
        except Exception as e:
            logger.error(f"LLM classification error: {e}, using fallback")
            # Simple fallback classification
            query_lower = user_input.lower()
            company_indicators = ["company", "společnost", "firma", "corporation", "s.r.o.", "a.s.", "risk", "supplier"]
            if any(indicator in query_lower for indicator in company_indicators):
                return "company"
            return "custom"
            
    except Exception as e:
        logger.error(f"Error in analyze_query_sync: {e}")
        return "error"

# Extract company name function for backward compatibility
def extract_company_name(query: str) -> str:
    """
    Extract company name from query.
    
    Args:
        query: User query
        
    Returns:
        Company name or empty string
    """
    company, _ = analyze_company_query(query)
    return company if company != "Unknown Company" else ""

# Backwards compatibility aliases
analyze_query_async = analyze_query_sync
analyze_query = analyze_query_sync

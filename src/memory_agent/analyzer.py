import logging
import traceback
import re
from typing import Dict, List, Literal, Optional, Union, Any, Tuple
from typing_extensions import TypedDict
import asyncio
from functools import wraps

# LangChain Core imports
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field, validator
from langchain_core.runnables import RunnableConfig, chain, RunnablePassthrough
from langchain_core.tools import BaseTool, StructuredTool, tool
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_core.exceptions import OutputParserException

# LangChain imports
from langchain.chat_models import init_chat_model

from memory_agent import utils

logger = logging.getLogger(__name__)

# UPDATED: Definition of analysis types with Literal instead of enum
AnalysisType = Literal["risk_comparison", "supplier_analysis", "general"]

# Valid analysis types constant
VALID_ANALYSIS_TYPES = ["risk_comparison", "supplier_analysis", "general"]

# NEW: Define Pydantic model for analysis result
class AnalysisResult(BaseModel):
    """Result of user input analysis."""
    companies: List[str] = Field(description="List of identified companies")
    company: str = Field(description="Primary company (first in the list)")
    analysis_type: AnalysisType = Field(description="Type of analysis to perform")
    query: str = Field(description="Original user query")
    is_company_analysis: bool = Field(description="Indicates whether the query is about company analysis")
    confidence: float = Field(ge=0.0, le=1.0, description="Analysis confidence level (0.0 - 1.0)")
    
    model_config = {"extra": "forbid"}

# NEW: Few-shot examples for each type of analysis
RISK_EXAMPLES = [
    {
        "query": "What are the risks for MB TOOL?",
        "reasoning": "This query is asking about risk factors specific to MB TOOL.",
        "analysis_type": "risk_comparison"
    },
    {
        "query": "Jaká jsou compliance rizika pro ADIS TACHOV?",
        "reasoning": "This query is asking about compliance risks for ADIS TACHOV.",
        "analysis_type": "risk_comparison"
    },
    {
        "query": "Má MB TOOL nějaké sankce?",
        "reasoning": "This query is asking about possible sanctions against MB TOOL, which is a risk factor.",
        "analysis_type": "risk_comparison"
    }
]

SUPPLIER_EXAMPLES = [
    {
        "query": "Show me suppliers for BOS AUTOMOTIVE",
        "reasoning": "This query is asking about the suppliers of BOS AUTOMOTIVE.",
        "analysis_type": "supplier_analysis"
    },
    {
        "query": "Kdo dodává komponenty pro Flídr plast?",
        "reasoning": "This query is asking about the suppliers for Flídr plast.",
        "analysis_type": "supplier_analysis"
    },
    {
        "query": "Ukaž mi dodavatelský řetězec pro BOS AUTOMOTIVE - CZE závod",
        "reasoning": "This query is asking about the supply chain for BOS AUTOMOTIVE - CZE.",
        "analysis_type": "supplier_analysis"
    }
]

GENERAL_EXAMPLES = [
    {
        "query": "Tell me about MB TOOL",
        "reasoning": "This is a general query about MB TOOL without specific focus.",
        "analysis_type": "general"
    },
    {
        "query": "Co je to Flídr plast?",
        "reasoning": "This is a general query about what Flídr plast is.",
        "analysis_type": "general"
    },
    {
        "query": "Poskytni mi informace o společnosti ADIS TACHOV",
        "reasoning": "This is a general request for information about ADIS TACHOV.",
        "analysis_type": "general"
    }
]

# NEW: Reasoning steps for analysis type detection
REASONING_STEPS = """
Follow these steps to analyze the query:

1. ENTITY EXTRACTION
   - Identify all company names mentioned
   - Look for specific entities (products, locations, etc.)

2. INTENT ANALYSIS
   - Determine if query is about risks/compliance
   - Determine if query is about suppliers/supply chain
   - Determine if query is a general information request

3. TYPE DETERMINATION
   - If risk/compliance related → "risk_comparison"
   - If supplier/supply chain related → "supplier_analysis"
   - Otherwise → "general"
"""

# Updated analyzer prompt with few-shot examples and reasoning steps
ANALYZER_PROMPT = ChatPromptTemplate.from_template(
    """Analyze this question and determine the company and analysis type.
    
    Follow these steps:
    {reasoning_steps}
    
    Examples:
    {examples}
    
    Question: {question}
    
    Provide your analysis in this format:
    ENTITY EXTRACTION: <identified companies>
    INTENT ANALYSIS: <intent of the query>
    TYPE DETERMINATION: <appropriate analysis type>
    
    Analysis:
    """
)

# Helper function to format examples for prompt
def format_examples(examples: List[Dict]) -> str:
    """Format examples for inclusion in prompt."""
    formatted = ""
    for ex in examples:
        formatted += f"Query: \"{ex['query']}\"\n"
        formatted += f"ENTITY EXTRACTION: Company \"{ex['query'].split()[3 if 'for' in ex['query'].lower() else 2]}\" is mentioned.\n"
        formatted += f"INTENT ANALYSIS: {ex['reasoning']}\n"
        formatted += f"TYPE DETERMINATION: This is a {ex['analysis_type']} analysis.\n\n"
    return formatted

# Removed complexity_score function for simplification

# Simplified function to detect analysis type
def detect_analysis_type(query: str, response: str = "") -> AnalysisType:
    """
    Detekuje typ analýzy na základě klíčových slov v dotazu.
    
    Podporované typy analýz:
    - risk_comparison: Analýza rizik a compliance
    - supplier_analysis: Analýza dodavatelských vztahů
    - general: Obecné informace o společnosti
    
    Args:
        query: Text uživatelského dotazu
        response: Volitelná odpověď modelu (používá se pro kontext)
        
    Returns:
        AnalysisType: Zjištěný typ analýzy
    """
    # Standard detection based on keywords
    response = response.lower() if response else ""
    query = query.lower()
    
    # Rozšířené seznamy klíčových slov pro lepší detekci
    risk_keywords = [
        "risk", "rizik", "rizic", "compliance", "sanctions", "sankce", 
        "bezpečnost", "security", "regulace", "regulation",
        "aml", "kyc", "fatf", "ofac", "embargo", "reputace"
    ]
    
    supplier_keywords = [
        "supplier", "dodavatel", "supply chain", "relationships", 
        "vztahy", "dodávky", "tier", "odběratel", "procurement",
        "logistics", "logistika", "distributor", "vendor", "nákup"
    ]
    
    if any(kw in response or kw in query for kw in risk_keywords):
        return "risk_comparison"
    elif any(kw in response or kw in query for kw in supplier_keywords):
        return "supplier_analysis"
    else:
        return "general"

# Removed advanced analysis functions for simplification
# Functions advanced_analysis_with_llm, extract_analysis_type_from_reasoning, and process_with_reasoning have been removed

# Simplified parse response function
def parse_response(response: str, original_query: str) -> AnalysisResult:
    """Simplified parsing of LLM response."""
    try:
        # Extract companies from response
        companies = []
        entity_extraction = re.search(r'ENTITY EXTRACTION:\s*(.*?)(?:\n|$)', response)
        if entity_extraction:
            entity_text = entity_extraction.group(1)
            company_pattern = r'\"([^\"]+)\"'
            company_matches = re.findall(company_pattern, entity_text)
            if company_matches:
                companies = company_matches
            else:
                # Simple company extraction
                company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
                companies = re.findall(company_pattern, original_query)
                companies = [c.strip() for c in companies if len(c.strip()) > 2]
        
        # Extract analysis type
        analysis_type = "general"  # Default
        type_determination = re.search(r'TYPE DETERMINATION:\s*(.*?)(?:\n|$)', response)
        if type_determination:
            type_text = type_determination.group(1).lower()
            if "risk_comparison" in type_text:
                analysis_type = "risk_comparison"
            elif "supplier_analysis" in type_text:
                analysis_type = "supplier_analysis"
        else:
            # If not found in the structured output, detect based on keywords
            analysis_type = detect_analysis_type(original_query, response)
        
        # Create structured result
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type=analysis_type,
            query=original_query,
            is_company_analysis=bool(companies),
            confidence=0.8 if companies else 0.6
        )
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        # Basic fallback
        company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
        companies = re.findall(company_pattern, original_query)
        companies = [c.strip() for c in companies if len(c.strip()) > 2]
        
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type="general",
            query=original_query,
            is_company_analysis=bool(companies),
            confidence=0.5
        )

# Removed Error Handler class for simplification

# Simplified analyze_query function
async def analyze_query(
    user_input: str, 
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = None, 
    mcp_connector: Any = None
) -> AnalysisResult:
    """Simplified function to analyze user query."""
    try:
        # Initialize model
        model_name = "anthropic/claude-3-sonnet-20240229"
        if config:
            from langchain_core.runnables.config import Configuration
            configurable = Configuration.from_runnable_config(config or {})
            if configurable.model:
                model_name = utils.split_model_and_provider(configurable.model)[1]
        elif model:
            model_name = utils.split_model_and_provider(model)[1]
            
        llm = init_chat_model(model=model_name)
        
        # Combine examples based on query content
        examples = []
        examples.append(RISK_EXAMPLES[0])
        examples.append(SUPPLIER_EXAMPLES[0])
        examples.append(GENERAL_EXAMPLES[0])
        
        # Create LCEL chain
        analyzer_chain = (
            {
                "question": lambda x: x, 
                "reasoning_steps": lambda _: REASONING_STEPS,
                "examples": lambda _: format_examples(examples)
            }
            | ANALYZER_PROMPT
            | llm
            | StrOutputParser()
        )
        
        # Get LLM analysis response
        response = await analyzer_chain.ainvoke(user_input)
        logger.info(f"LLM analysis response: {response[:100]}...")
        
        # Parse the response into structured format
        result = parse_response(response, user_input)
        logger.info(f"Analysis result: {result}")
        return result
            
    except Exception as e:
        logger.error(f"Error in analyze_query: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Basic fallback
        company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
        companies = re.findall(company_pattern, user_input)
        companies = [c.strip() for c in companies if len(c.strip()) > 2]
        
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type="general",
            query=user_input,
            is_company_analysis=bool(companies),
            confidence=0.4
        )

# Synchronní wrapper pro analyze_query
import asyncio

def analyze_query_sync(
    user_input: str, 
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = None, 
    mcp_connector: Any = None
) -> str:
    """
    Simplified synchronous wrapper for analyze_query.
    
    Args:
        user_input: User input to analyze
        config: Optional runnable configuration
        model: Optional model name
        mcp_connector: Optional MCP connector
        
    Returns:
        Query type as string: "company", "person", "relationship", "custom", or "error"
    """
    # Direct check for known companies
    if "MB TOOL" in user_input or "ŠKODA AUTO" in user_input or "ADIS TACHOV" in user_input or "Flídr plast" in user_input:
        return "company"

    try:
        # Get event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Create new loop if not available
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Run async function synchronously
        result = loop.run_until_complete(
            analyze_query(user_input, config, model, mcp_connector)
        )
        
        # Map results to query type
        if result.companies:
            return "company"
        elif any(keyword in user_input.lower() for keyword in ["osoba", "person", "člověk", "human", "zaměstnanec", "employee"]):
            return "person"
        elif any(keyword in user_input.lower() for keyword in ["vztah", "relationship", "vazba", "connection", "dodavatel", "supplier"]):
            return "relationship"
        else:
            return "custom"
            
    except Exception as e:
        logger.error(f"Error in analyze_query_sync: {str(e)}")
        return "error"

# Alias for the asynchronous function
analyze_query_async = analyze_query

# Simplified direct company recognition function
def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Simplified function to extract company name and analysis type.
    
    Args:
        query: User query to analyze
        
    Returns:
        Tuple of (company_name, analysis_type)
    """
    # Hard-coded common companies for quick lookup
    known_companies = {
        "MB TOOL": "risk_comparison",
        "ŠKODA AUTO": "general",
        "ADIS TACHOV": "general", 
        "Flídr plast": "supplier_analysis",
        "BOS AUTOMOTIVE": "supplier_analysis"
    }
    
    # Check for known companies first
    for company, analysis_type in known_companies.items():
        if company in query:
            return company, analysis_type
    
    # Simple regex for company extraction
    company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
    matches = re.findall(company_pattern, query)
    company = matches[0] if matches else "Unknown Company"
    
    # Simple analysis type detection
    lower_query = query.lower()
    if any(kw in lower_query for kw in ["risk", "riziko", "compliance", "sanctions", "sankce"]):
        analysis_type = "risk_comparison"
    elif any(kw in lower_query for kw in ["supplier", "dodavatel", "supply chain", "vztahy", "dodávky"]):
        analysis_type = "supplier_analysis"
    else:
        analysis_type = "general"
        
    return company, analysis_type

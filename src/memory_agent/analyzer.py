from typing import Any, Dict, List, Optional, Tuple, Literal
import json
import logging
import os
import re
import traceback
from datetime import datetime

# LangChain Core imports
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_core.runnables import RunnableConfig, chain, RunnablePassthrough
from langchain_core.tools import BaseTool, StructuredTool, tool
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_core.exceptions import OutputParserException

# LangChain imports
from langchain_openai import ChatOpenAI

from memory_agent import utils

logger = logging.getLogger(__name__)

# Helper function to replace init_chat_model
def get_chat_model(model: str = "gpt-4", temperature: float = 0.0, **kwargs):
    """Initialize a chat model with the given parameters."""
    # Handle Anthropic models
    if "anthropic" in model.lower() or "claude" in model.lower():
        # NOTE: For Anthropic models, we'd need to import from langchain_anthropic
        # This is a placeholder that will use OpenAI as fallback
        logger.warning(f"Anthropic model '{model}' requested but using OpenAI fallback")
        return ChatOpenAI(model="gpt-4", temperature=temperature, **kwargs)
    # Handle OpenAI models (default)
    else:
        return ChatOpenAI(model=model, temperature=temperature, **kwargs)

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

# NEW: Function to measure query complexity
def complexity_score(query: str) -> float:
    """Calculate complexity score of query to determine if reasoning process is needed."""
    score = 0.0
    if len(query.split()) > 10:  # Longer queries are potentially more complex
        score += 0.3
    if "?" in query and any(x in query.lower() for x in ["why", "how", "when", "proč", "jak", "kdy"]):
        score += 0.3
    if re.search(r'(and|or|but|a|nebo|ale)', query.lower()):  # Conjunctions indicate complexity
        score += 0.2
    if len(re.findall(r'[A-Z][A-Za-z0-9\s]+', query)) > 1:  # Multiple entities with capital letters
        score += 0.2
    return min(score, 1.0)  # Limit score to range 0.0-1.0

# NEW: Function to detect analysis type
def detect_analysis_type(query: str, response: str = "") -> AnalysisType:
    """Detect analysis type based on LLM response and original query."""
    # Use advanced analysis for complex queries
    if complexity_score(query) > 0.7:
        return advanced_analysis_with_llm(query)
    
    # Standard detection based on keywords
    response = response.lower() if response else ""
    query = query.lower()
    
    # Detection based on keywords
    risk_keywords = ["risk", "riziko", "compliance", "sanctions", "sankce", "bezpečnost", "security"]
    supplier_keywords = ["supplier", "dodavatel", "supply chain", "relationships", "vztahy", "dodávky"]
    
    if any(kw in response or kw in query for kw in risk_keywords):
        return "risk_comparison"
    elif any(kw in response or kw in query for kw in supplier_keywords):
        return "supplier_analysis"
    else:
        return "general"

# NEW: Advanced analysis with LLM and reasoning
def advanced_analysis_with_llm(query: str) -> AnalysisType:
    """Advanced analysis of complex queries using LLM and few-shot examples."""
    try:
        # Combine all examples for comprehensive analysis
        all_examples = RISK_EXAMPLES + SUPPLIER_EXAMPLES + GENERAL_EXAMPLES
        result = process_with_reasoning(query, all_examples)
        
        # Extract analysis type from result
        analysis_type = extract_analysis_type_from_reasoning(result)
        
        if analysis_type not in VALID_ANALYSIS_TYPES:
            return "general"  # Fallback to general for invalid types
        
        return analysis_type
    except Exception as e:
        logger.error(f"Error in advanced analysis: {str(e)}")
        return "general"  # Fallback to general in case of errors

# NEW: Extract analysis type from reasoning response
def extract_analysis_type_from_reasoning(reasoning: str) -> AnalysisType:
    """Extract analysis type from reasoning text."""
    reasoning = reasoning.lower()
    
    if "risk_comparison" in reasoning:
        return "risk_comparison"
    elif "supplier_analysis" in reasoning:
        return "supplier_analysis"
    else:
        return "general"

# NEW: Process query with reasoning steps
def process_with_reasoning(query: str, examples: List[Dict[str, Any]]) -> str:
    """Process query with reasoning process for more accurate analysis type detection."""
    # Initialize model with low temperature for deterministic outputs
    llm = get_chat_model(model="anthropic/claude-3-sonnet-20240229", temperature=0.1)
    
    # Create prompt with examples and reasoning steps
    prompt_template = """Analyze this query using these steps:
    {reasoning_steps}
    
    Examples:
    {examples}
    
    Query: {query}
    
    Provide a detailed analysis:
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Prepare examples and reasoning steps
    formatted_examples = format_examples(examples)
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Process query
    result = chain.invoke({
        "reasoning_steps": REASONING_STEPS,
        "examples": formatted_examples,
        "query": query
    })
    
    return result

# UPDATED: Parse response from LLM
def parse_response(response: str, original_query: str) -> AnalysisResult:
    """Parse LLM response and create structured AnalysisResult."""
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
                # Try alternative pattern without quotes
                company_pattern = r'Company\s+([A-Za-z0-9\s\-]+)'
                company_matches = re.findall(company_pattern, entity_text)
                companies = [match.strip() for match in company_matches if match.strip()]
        
        # Fallback: Try to find companies directly in query
        if not companies:
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
            # If not found in the structured output, detect based on response content
            analysis_type = detect_analysis_type(original_query, response)
        
        # Create structured result
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type=analysis_type,
            query=original_query,
            is_company_analysis=bool(companies),
            confidence=0.8 if companies and type_determination else 0.6
        )
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        # Fallback to simpler detection method
        return ErrorHandler.handle_parsing_error(e, original_query)

# NEW: Error handler class
class ErrorHandler:
    """Class for handling various errors in analysis process."""
    
    @staticmethod
    def handle_parsing_error(error: Exception, query: str) -> AnalysisResult:
        """Handle error when parsing LLM output."""
        logger.warning(f"Error parsing LLM output: {str(error)}")
        
        # Fallback detection
        lower_query = query.lower()
        if any(kw in lower_query for kw in ["risk", "compliance", "sanctions", "riziko", "sankce"]):
            analysis_type = "risk_comparison"
        elif any(kw in lower_query for kw in ["supplier", "supply", "dodavatel", "dodávky"]):
            analysis_type = "supplier_analysis"
        else:
            analysis_type = "general"
        
        # Basic entity extraction
        company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
        companies = re.findall(company_pattern, query)
        companies = [c.strip() for c in companies if len(c.strip()) > 2]
        
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type=analysis_type,
            query=query,
            is_company_analysis=bool(companies),
            confidence=0.5  # Medium confidence for fallback
        )
    
    @staticmethod
    def handle_llm_error(error: Exception, query: str) -> AnalysisResult:
        """Handle error when interacting with LLM."""
        logger.error(f"Error in LLM interaction: {str(error)}")
        
        # Very basic fallback analysis
        company_pattern = r'[A-Z][A-Za-z0-9\s\-]+'
        companies = re.findall(company_pattern, query)
        companies = [c.strip() for c in companies if len(c.strip()) > 2]
        
        return AnalysisResult(
            companies=companies,
            company=companies[0] if companies else "",
            analysis_type="general",  # Default to general analysis
            query=query,
            is_company_analysis=bool(companies),
            confidence=0.4  # Lower confidence for error fallback
        )

# UPDATED: Main analyze_query function with LCEL chain
async def analyze_query(
    user_input: str, 
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = None, 
    mcp_connector: Any = None
) -> AnalysisResult:
    """Analyze user query and identify companies and analysis type."""
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
            
        llm = get_chat_model(model=model_name)
        
        # Combine examples based on query content
        examples = []
        lower_query = user_input.lower()
        
        if any(kw in lower_query for kw in ["risk", "compliance", "sanctions", "riziko", "sankce"]):
            examples.extend(RISK_EXAMPLES[:2])
        if any(kw in lower_query for kw in ["supplier", "supply", "dodavatel", "dodávky"]):
            examples.extend(SUPPLIER_EXAMPLES[:2])
        
        # Always include at least one example of each type
        if not any(ex["analysis_type"] == "risk_comparison" for ex in examples):
            examples.append(RISK_EXAMPLES[0])
        if not any(ex["analysis_type"] == "supplier_analysis" for ex in examples):
            examples.append(SUPPLIER_EXAMPLES[0])
        if not any(ex["analysis_type"] == "general" for ex in examples):
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
        
        # Try structured output parsing first
        try:
            # Get LLM analysis response
            response = await analyzer_chain.ainvoke(user_input)
            logger.info(f"LLM analysis response: {response[:100]}...")
            
            # Parse the response into structured format
            result = parse_response(response, user_input)
            logger.info(f"Analysis result: {result}")
            return result
            
        except OutputParserException as e:
            logger.warning(f"Error parsing output: {e}")
            # Simplified prompt as fallback
            simple_prompt = ChatPromptTemplate.from_template(
                "Analyze this question and identify the company name and whether it's asking about risks, " 
                "suppliers, or general information: {question}"
            )
            response = await (simple_prompt | llm | StrOutputParser()).ainvoke({"question": user_input})
            return parse_response(response, user_input)
            
    except Exception as e:
        logger.error(f"Error in analyze_query: {str(e)}")
        logger.error(traceback.format_exc())
        # Fallback to error handler
        return ErrorHandler.handle_llm_error(e, user_input)

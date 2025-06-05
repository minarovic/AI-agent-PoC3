"""
Enhanced analyzer pro Memory Agent podle LangGraph dokumentace.
Podporuje detekci typu analýzy a extrakci názvu společnosti z dotazů.
"""

import asyncio
import json
from typing import Any, Dict, Tuple

from .tools import AsyncMockMCPConnector, MockMCPConnector

# Constants
RELATIONSHIP_SLICE_LIMIT = 100  # Limit the number of relationships to process


def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Parse user query to extract company name and analysis type.

    Args:
        query: User query about company

    Returns:
        Tuple[str, str]: (company_name, analysis_type)
    """
    # Normalize query for analysis
    query_lower = query.lower().strip()

    # Known company patterns from mock data
    company_name_mapping = {
        "mb tool": "MB TOOL",
        "bos automotive": "BOS AUTOMOTIVE",
        "adis tachov": "ADIS TACHOV",
        "flídr plast": "Flídr plast",
        "flidr plast": "Flídr plast",
    }

    # Try to find company name in query
    company_name = ""
    for company, formatted_name in company_name_mapping.items():
        if company in query_lower:
            company_name = formatted_name
            break

    # If no known company found, try to extract from simple patterns
    if not company_name:
        # Pattern: "CompanyName; analysis_type"
        if ";" in query:
            parts = query.split(";", 1)
            company_name = parts[0].strip()
        else:
            # Use the query as company name if it's short and likely a company name
            words = query.strip().split()
            if len(words) <= 3 and not any(
                word in query_lower
                for word in [
                    "what",
                    "tell",
                    "about",
                    "analyze",
                    "risk",
                    "supplier",
                    "chain",
                ]
            ):
                company_name = query.strip()

    # Determine analysis type
    analysis_type = "general"  # default

    # Risk analysis keywords
    if any(
        keyword in query_lower
        for keyword in ["risk", "rizik", "compliance", "sanction", "sankce"]
    ):
        analysis_type = "risk_comparison"

    # Supplier analysis keywords
    elif any(
        keyword in query_lower
        for keyword in [
            "supplier",
            "dodavatel",
            "chain",
            "řetězec",
            "vztah",
            "relationship",
        ]
    ):
        analysis_type = "supplier_analysis"

    # Explicit type specification
    elif "risk_comparison" in query_lower:
        analysis_type = "risk_comparison"
    elif "supplier_analysis" in query_lower:
        analysis_type = "supplier_analysis"

    return company_name, analysis_type


def get_analysis_prompt(analysis_type: str) -> str:
    """
    Get specialized prompt for analysis type.

    Args:
        analysis_type: Type of analysis (risk_comparison, supplier_analysis, general)

    Returns:
        str: Specialized prompt for the analysis type
    """
    prompts = {
        "risk_comparison": """
Analyzuj rizikové faktory pro společnost {company_name}.

Externí data:
{external_data}

Interní data:
{internal_data}

Vztahy:
{relationships_data}

Zaměř se na sankce, compliance problémy a rizikové faktory.
Poskytni strukturovanou analýzu rizik včetně:
1. Identifikované rizikové faktory
2. Hodnocení závažnosti rizik
3. Doporučení pro mitigaci rizik
""",
        "supplier_analysis": """
Analyzuj dodavatelské vztahy pro společnost {company_name}.

Externí data:
{external_data}

Interní data:
{internal_data}

Vztahy:
{relationships_data}

Zaměř se na dodavatele a dodavatelský řetězec.
Poskytni strukturovanou analýzu dodavatelského řetězce včetně:
1. Klíčoví dodavatelé a odběratelé
2. Tier klasifikace (Tier 1, Tier 2, Tier 3)
3. Analýza dodavatelských vztahů
4. Hodnocení stability dodavatelského řetězce
""",
        "general": """
Analyzuj následující informace o společnosti {company_name}.

Externí data:
{external_data}

Interní data:
{internal_data}

Vztahy:
{relationships_data}

Poskytni vyváženou a strukturovanou analýzu včetně:
1. Základní informace o společnosti
2. Finanční situace a výkonnost
3. Klíčové obchodní vztahy
4. Celkové hodnocení společnosti
""",
    }

    return prompts.get(analysis_type, prompts["general"])


def format_analysis_data(
    company_data: Dict[str, Any],
    internal_data: Dict[str, Any],
    relationships_data: list,
) -> Dict[str, str]:
    """
    Format data for use in analysis prompts.

    Args:
        company_data: Company data from MockMCPConnector
        internal_data: Internal company data
        relationships_data: Company relationships data

    Returns:
        Dict[str, str]: Formatted data for prompts
    """
    # Format external data
    external_data = "Základní informace:\n"
    if company_data:
        external_data += f"- Název: {company_data.get('label', 'N/A')}\n"
        external_data += f"- ID: {company_data.get('id', 'N/A')}\n"
        external_data += (
            f"- Země: {', '.join(company_data.get('countries', ['N/A']))}\n"
        )

        if company_data.get("addresses"):
            external_data += (
                f"- Adresa: {company_data['addresses'][0].get('full', 'N/A')}\n"
            )

        if company_data.get("identifiers"):
            external_data += "- Identifikátory:\n"
            for identifier in company_data["identifiers"]:
                external_data += f"  * {identifier.get('type', 'N/A')}: {identifier.get('value', 'N/A')}\n"

    # Format internal data
    internal_formatted = "Interní informace:\n"
    if internal_data and internal_data.get("message") != "Financial data not available":
        for key, value in internal_data.items():
            internal_formatted += f"- {key}: {value}\n"
    else:
        internal_formatted += "- Nejsou k dispozici detailní interní data\n"

    # Format relationships
    relationships_formatted = "Obchodní vztahy:\n"
    if relationships_data:
        for rel in relationships_data[
            :RELATIONSHIP_SLICE_LIMIT
        ]:  # Limit to first RELATIONSHIP_SLICE_LIMIT relationships
            rel_type = rel.get("type", "Neznámý vztah")
            source = rel.get("source_name", rel.get("source_id", "N/A"))
            target = rel.get("target_name", rel.get("target_id", "N/A"))
            relationships_formatted += f"- {rel_type}: {source} -> {target}\n"
    else:
        relationships_formatted += "- Nejsou k dispozici data o vztazích\n"

    return {
        "external_data": external_data,
        "internal_data": internal_formatted,
        "relationships_data": relationships_formatted,
    }


async def analyze_company_async(query: str) -> str:
    """
    Asynchronní verze analyze_company pro použití v async kontextech.
    Analyze company data and return structured information.
    Enhanced to support analysis type detection and company name parsing.

    Args:
        query: User query about company

    Returns:
        JSON string with company analysis results
    """
    try:
        # Parse query to extract company name and analysis type
        company_name, analysis_type = analyze_company_query(query)

        if not company_name:
            return json.dumps(
                {
                    "error": "Could not extract company name from query",
                    "query_type": "company",
                    "analysis_type": analysis_type,
                    "analysis_complete": False,
                    "query": query,
                    "suggestion": "Please specify a company name or use format: 'Company Name; analysis_type'",
                }
            )

        # Inicializace async mock MCP connectoru
        connector = AsyncMockMCPConnector()

        # Načtení dat pomocí async metod
        company_data = await connector.get_company_by_name(query)

        # Získání ID společnosti pro další dotazy
        company_id = company_data.get("id") if company_data else None

        internal_data = {}
        relationships_data = []

        if company_id:
            try:
                internal_data = await connector.get_company_financials(company_id)
            except Exception:
                internal_data = {"message": "Financial data not available"}

            try:
                relationships_data = await connector.get_company_relationships(
                    company_id
                )
            except Exception:
                relationships_data = []

        # Format data for analysis
        formatted_data = format_analysis_data(
            company_data, internal_data, relationships_data
        )

        # Get specialized prompt based on analysis type
        prompt_template = get_analysis_prompt(analysis_type)

        # Generate analysis prompt
        analysis_prompt = prompt_template.format(
            company_name=company_name, **formatted_data
        )

        # Strukturované vrácení dat
        result = {
            "query_type": "company",
            "analysis_type": analysis_type,
            "company_name": company_name,
            "company_data": company_data,
            "internal_data": internal_data,
            "relationships_data": relationships_data,
            "analysis_prompt": analysis_prompt,
            "formatted_data": formatted_data,
            "analysis_complete": True,
            "query": query,
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


def analyze_company(query: str) -> str:
    """
    Synchronní wrapper pro analyze_company_async.
    Analyze company data and return structured information.
    Enhanced to support analysis type detection and company name parsing.

    Args:
        query: User query about company

    Returns:
        JSON string with company analysis results
    """
    try:
        # Pokusíme se spustit async verzi
        try:
            # Pokud již běží event loop, použijeme to_thread
            loop = asyncio.get_running_loop()
            # Spustíme async verzi v thread poolu
            future = asyncio.run_coroutine_threadsafe(
                analyze_company_async(query), loop
            )
            return future.result(timeout=30)  # 30s timeout
        except RuntimeError:
            # Pokud neběží event loop, spustíme nový
            return asyncio.run(analyze_company_async(query))
    except Exception:
        # Fallback na synchronní verzi při chybě
        try:
            # Parse query to extract company name and analysis type
            company_name, analysis_type = analyze_company_query(query)

            if not company_name:
                return json.dumps(
                    {
                        "error": "Could not extract company name from query",
                        "query_type": "company",
                        "analysis_type": analysis_type,
                        "analysis_complete": False,
                        "query": query,
                        "suggestion": "Please specify a company name or use format: 'Company Name; analysis_type'",
                    }
                )

            # Inicializace synchronní mock MCP connectoru
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

            # Format data for analysis
            formatted_data = format_analysis_data(
                company_data, internal_data, relationships_data
            )

            # Get specialized prompt based on analysis type
            prompt_template = get_analysis_prompt(analysis_type)

            # Generate analysis prompt
            analysis_prompt = prompt_template.format(
                company_name=company_name, **formatted_data
            )

            # Strukturované vrácení dat
            result = {
                "query_type": "company",
                "analysis_type": analysis_type,
                "company_name": company_name,
                "company_data": company_data,
                "internal_data": internal_data,
                "relationships_data": relationships_data,
                "analysis_prompt": analysis_prompt,
                "formatted_data": formatted_data,
                "analysis_complete": True,
                "query": query,
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

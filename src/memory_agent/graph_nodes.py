"""
Graph nodes pro integraci MockMCPConnector s LangGraph workflow.

Tento modul obsahuje implementaci uzlů grafu pro StateGraph, které využívají
MockMCPConnector pro získávání dat pro různé typy analýz.
"""

from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
import logging
import traceback

from memory_agent.tools import (
    MockMCPConnector, 
    CompanyQueryParams, 
    EntityNotFoundError,
    DataFormatError,
    ConnectionError,
    MockMCPConnectorError
)

from memory_agent.state import State
from memory_agent.analyzer import analyze_query_sync
from memory_agent import utils

# Import prompt registry
from memory_agent.prompts import (
    PromptRegistry,
    PromptDataFormatter,
    PromptChainBuilder,
    format_state_for_prompt
)

# Nastavení loggeru
logger = logging.getLogger("memory_agent.graph_nodes")

# Uzly grafu pro LangGraph

def determine_analysis_type(state: State) -> State:
    """
    Rozšířená funkce pro určení typu analýzy z dotazu.
    
    Podporované typy analýz:
    - risk_comparison: Analýza rizik a compliance
    - supplier_analysis: Analýza dodavatelských vztahů
    - general: Obecné informace o společnosti
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s určeným typem analýzy
    """
    # Výchozí typ analýzy
    analysis_type = "general"
    
    # Získání dotazu
    query = state.current_query.lower() if state.current_query else ""
    
    # Využití funkce z analyzer.py místo duplikace kódu
    try:
        from memory_agent.analyzer import detect_analysis_type
        analysis_type = detect_analysis_type(query)
        logger.info(f"Analýza typu pomocí analyze.py: {analysis_type}")
    except Exception as e:
        # Záložní řešení pokud import selže
        logger.warning(f"Nelze použít analyzer.detect_analysis_type: {str(e)}")
        
        # Rozšířená detekce klíčových slov
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
        
        if any(kw in query for kw in risk_keywords):
            analysis_type = "risk_comparison"
        elif any(kw in query for kw in supplier_keywords):
            analysis_type = "supplier_analysis"
    
    # Ověření, že typ analýzy je jeden z podporovaných
    if analysis_type not in ["general", "risk_comparison", "supplier_analysis"]:
        logger.warning(f"Detekován nepodporovaný typ analýzy: {analysis_type}, používám 'general'")
        analysis_type = "general"
    
    logger.info(f"Dotaz '{query[:30]}...' určen jako typ analýzy: {analysis_type}")
    return {"analysis_type": analysis_type}

def route_query(state: State) -> State:
    """
    Zjednodušená verze funkce pro analýzu vstupního dotazu.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s určeným typem dotazu
    """
    if state.current_query is None and state.messages:
        # Extrahujeme dotaz z poslední zprávy
        last_message = state.messages[-1]
        state.current_query = last_message.content
    
    if not state.current_query:
        logger.error("Nebyl nalezen žádný dotaz k analýze")
        return {"query_type": "error", "error_state": {"error": "Nebyl nalezen žádný dotaz k analýze"}}
    
    # Standardní analýza pomocí analyze_query_sync
    query_type = analyze_query_sync(state.current_query)
    logger.info(f"Dotaz '{state.current_query[:30]}...' klasifikován jako typ: {query_type}")
    
    # Určení typu analýzy
    updated_state = determine_analysis_type(state)
    analysis_type = updated_state.get("analysis_type", "general")
    
    return {
        "query_type": query_type,
        "analysis_type": analysis_type
    }

def prepare_company_query(state: State) -> State:
    """
    Zjednodušená funkce pro přípravu dotazu na společnost.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s parametry dotazu a základními daty společnosti
    """
    logger.info(f"Připravuji dotaz pro společnost: {state.current_query}")
    
    # Rozpoznání názvu společnosti z dotazu
    query = state.current_query if state.current_query else ""
    company_name = "Unknown"
    analysis_type = getattr(state, "analysis_type", "general")  # Získání typu analýzy ze state
    
    # Pokud máme výsledek analýzy a společnosti, použijeme ho
    if hasattr(state, "analysis_result") and state.analysis_result:
        if "company_name" in state.analysis_result:
            company_name = state.analysis_result["company_name"]
    
    # Přímé využití již existující funkce z analyzer.py
    if company_name == "Unknown" and query:
        try:
            # Import analyzér z modulu analyzer
            from memory_agent.analyzer import analyze_company_query
            
            # Analyzujeme dotaz pomocí zjednodušené funkce
            company, detected_analysis_type = analyze_company_query(query)
            if company and company != "Unknown Company":
                company_name = company
                logger.info(f"Analyzér rozpoznal společnost: {company_name}")
                
                # Pokud nemáme typ analýzy, použijeme detekovaný
                if analysis_type == "general" and detected_analysis_type != "general":
                    analysis_type = detected_analysis_type
                    logger.info(f"Aktualizace typu analýzy na: {analysis_type}")
        except Exception as e:
            logger.error(f"Chyba při analýze dotazu: {str(e)}")
            # Pro PoC použijeme defaultní hodnoty, pokud analýza selže
            if "MB TOOL" in query:
                company_name = "MB TOOL"
            elif "ŠKODA AUTO" in query:
                company_name = "ŠKODA AUTO"
            elif "ADIS TACHOV" in query:
                company_name = "ADIS TACHOV"
            elif "Flídr plast" in query:
                company_name = "Flídr plast"
    
    # Uložení výsledku dotazu na společnost
    state.company_query = {
        "query": query,
        "company_name": company_name
    }
    
    # Iniciální načtení dat o společnosti
    try:
        # Vytvoření MCP konektoru pro získání dat
        from memory_agent.tools import MockMCPConnector
        mcp_connector = MockMCPConnector()
        
        logger.info(f"Získávám základní data pro společnost: {company_name}")
        
        # Zde načteme základní data společnosti podle názvu
        company_data = None
        try:
            # Nejprve zkusíme načíst podle názvu
            company_data = mcp_connector.get_company_by_name(company_name)
            logger.info(f"Úspěšně načtena data o společnosti podle názvu: {company_name}")
        except Exception as e:
            logger.warning(f"Nelze načíst data podle názvu: {str(e)}")
            # Záložní řešení - vyhledání společnosti
            try:
                from memory_agent.tools import CompanyQueryParams
                search_results = mcp_connector.search_companies(CompanyQueryParams(name=company_name))
                if search_results and len(search_results) > 0:
                    company_data = search_results[0]
                    logger.info(f"Nalezena společnost vyhledáváním: {company_data.get('label', company_name)}")
            except Exception as search_error:
                logger.error(f"Nelze vyhledat společnost: {str(search_error)}")
        
        # Pokud nemáme data, vytvoříme minimální strukturu
        if not company_data:
            logger.warning(f"Nepodařilo se načíst data o společnosti {company_name}, vytvářím prázdnou strukturu")
            company_data = {
                "label": company_name,
                "id": company_name.lower().replace(" ", "_"),
                "basic_info": {
                    "name": company_name,
                    "id": company_name.lower().replace(" ", "_")
                }
            }
        
        # Zajištění základního formátu dat
        if "basic_info" not in company_data:
            company_data["basic_info"] = {
                "name": company_data.get("label", company_name),
                "id": company_data.get("id", company_name.lower().replace(" ", "_"))
            }
        
        # Ukládáme pouze základní data do state (bez MCP konektoru, který není serializovatelný)
        return {
            "company_name": company_name,
            "analysis_type": analysis_type,
            "company_data": company_data
            # NEUKLÁDAT mcp_connector do state - není serializovatelný pro checkpointy
        }
    except Exception as e:
        logger.error(f"Chyba při získávání dat společnosti: {str(e)}")
        return {
            "company_name": company_name,
            "analysis_type": analysis_type,
            "error_state": {"error": f"Chyba při získávání dat: {str(e)}", "error_type": "data_access_error"}
        }

def analyze_company_data(state: State) -> State:
    """
    Provede analýzu dat společnosti podle určeného typu analýzy.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s výsledky analýzy
    """
    # Získání typu analýzy z state (výchozí hodnota "general")
    analysis_type = getattr(state, "analysis_type", "general")
    logger.info(f"Analyzuji data společnosti pro typ analýzy: {analysis_type}")
    
    company_name = state.company_data.get("basic_info", {}).get("name", "Unknown Company")
    company_id = state.company_data.get("basic_info", {}).get("id", "unknown_id")
    
    # Inicializace základní struktury výsledku analýzy
    analysis_result = {
        "company_name": company_name,
        "company_id": company_id,
        "analysis_type": analysis_type,
        "timestamp": utils.get_current_timestamp(),
    }
    
    # Specializovaná analýza podle typu
    if analysis_type == "general":
        # Pro general analýzu využíváme search_info a financials
        search_info = state.company_data.get("search_info", {})
        financials = state.company_data.get("financials", {})
        
        # Základní informace o společnosti
        basic_info = {
            "name": company_name,
            "id": company_id
        }
        
        # Rozšíření o data ze search_info
        if search_info and search_info != {}:
            if "countries" in search_info:
                basic_info["countries"] = search_info.get("countries", [])
            if "addresses" in search_info:
                basic_info["addresses"] = search_info.get("addresses", [])
            if "identifiers" in search_info:
                basic_info["identifiers"] = search_info.get("identifiers", [])
            if "meta" in search_info:
                basic_info["meta"] = search_info.get("meta", {})
        
        # Finanční informace a aktivity
        financial_overview = {}
        if financials and financials != {}:
            if "supplier_since" in financials:
                financial_overview["supplier_since"] = financials.get("supplier_since", "")
            if "quality_rating" in financials:
                financial_overview["quality_rating"] = financials.get("quality_rating", "")
            if "compliance_status" in financials:
                financial_overview["compliance_status"] = financials.get("compliance_status", "")
            if "identified_activities" in financials:
                financial_overview["activities"] = financials.get("identified_activities", [])
            if "geographic_presence" in financials:
                financial_overview["geographic_presence"] = financials.get("geographic_presence", [])
        
        # Sestavení analýzy pro general typ
        analysis_result.update({
            "summary": f"Obecná analýza společnosti {company_name}",
            "basic_info": basic_info,
            "financial_overview": financial_overview,
            "key_findings": [
                f"Společnost {company_name} je aktivní v odvětví {'automotive' if 'industry' in financials else 'neznámém'}",
                f"Primární lokace: {', '.join(basic_info.get('countries', ['neznámá']))}"
            ],
        })
        
    elif analysis_type == "risk_comparison":
        # Pro risk analýzu využíváme detail společnosti a rizikové faktory
        company_detail = state.company_data.get("basic_info", {})
        risk_factors_data = getattr(state, "risk_factors_data", {})
        
        # Extrakce rizikových faktorů z dostupných zdrojů
        risk_factors = []
        risk_score = None
        
        # Nejprve zkusíme rizikové faktory z risk_factors_data získaného pomocí get_risk_factors_data
        if risk_factors_data:
            if "all_risk_factors" in risk_factors_data:
                risk_factors = risk_factors_data.get("all_risk_factors", [])
            if "risk_score" in risk_factors_data:
                risk_score = risk_factors_data.get("risk_score")
        
        # Pokud nejsou žádné rizikové faktory z risk_factors_data, zkusíme je extrahovat z company_detail
        if not risk_factors and "risk" in company_detail:
            risk_section = company_detail.get("risk", {})
            
            # Extrakce rizikového skóre
            if "risk_score" in risk_section and not risk_score:
                risk_score = risk_section.get("risk_score")
            
            # Zpracování rizikových faktorů
            for key, value in risk_section.items():
                if key == "risk_score":
                    continue
                
                if isinstance(value, bool) and value:
                    risk_factors.append({
                        "factor": key,
                        "category": "general",
                        "level": "identified"
                    })
                elif isinstance(value, dict) and "level" in value:
                    level = value.get("level")
                    category = key
                    if "factors" in value and isinstance(value["factors"], list):
                        for factor in value["factors"]:
                            risk_factors.append({
                                "factor": factor,
                                "category": category,
                                "level": level
                            })
        
        # Sestavení analýzy pro risk_comparison typ
        analysis_result.update({
            "summary": f"Analýza rizik pro společnost {company_name}",
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "key_findings": [
                f"Rizikové skóre: {risk_score if risk_score else 'Nedostupné'}",
                f"Identifikováno {len(risk_factors)} rizikových faktorů"
            ],
        })
        
    elif analysis_type == "supplier_analysis":
        # Pro supplier analýzu využíváme vztahy a supply chain
        relationships_data = getattr(state, "relationships_data", {}).get(company_id, [])
        supply_chain_data = getattr(state, "supply_chain_data", {}).get(company_id, [])
        
        # Extrakce dodavatelů ze vztahů
        suppliers = []
        if isinstance(relationships_data, list):
            for relation in relationships_data:
                # Kontrola, zda jde o vztah typu "has_supplier" a zda společnost je zdrojem
                if relation.get("type") == "has_supplier" and relation.get("source", {}).get("id") == company_id:
                    target = relation.get("target", {})
                    metadata = relation.get("metadata", {})
                    suppliers.append({
                        "name": target.get("label", "Unknown Supplier"),
                        "id": target.get("id", ""),
                        "tier": metadata.get("tier", "Unknown"),
                        "category": metadata.get("category", "Unknown")
                    })
        
        # Extrakce dodavatelů z supply chain dat
        supply_chain_suppliers = []
        if isinstance(supply_chain_data, list):
            for item in supply_chain_data:
                supplier_info = item.get("target", {})
                supplier_name = supplier_info.get("label", "")
                supplier_id = supplier_info.get("id", "")
                
                # Jen pokud máme alespoň název nebo ID
                if supplier_name or supplier_id:
                    # Kontrola, zda tento dodavatel už není v seznamu
                    if not any(s.get("id") == supplier_id for s in supply_chain_suppliers if supplier_id):
                        supply_chain_suppliers.append({
                            "name": supplier_name,
                            "id": supplier_id,
                            "tier": item.get("tier", "Unknown"),
                            "risk_factors": item.get("risk_factors", [])
                        })
        
        # Sestavení analýzy pro supplier_analysis typ
        analysis_result.update({
            "summary": f"Analýza dodavatelského řetězce pro společnost {company_name}",
            "suppliers": suppliers,
            "supply_chain": supply_chain_suppliers,
            "key_findings": [
                f"Identifikováno {len(suppliers)} přímých dodavatelů",
                f"Analýza dodavatelského řetězce obsahuje {len(supply_chain_suppliers)} dodavatelů",
                f"Zahrnuto {sum(1 for s in supply_chain_suppliers if s.get('risk_factors'))} dodavatelů s identifikovanými riziky" if supply_chain_suppliers else "Žádná rizika v dodavatelském řetězci nebyla identifikována"
            ],
            "data_quality": "high" if supply_chain_suppliers else "medium"
        })
    
    else:
        # Obecná analýza pro neznámý typ
        analysis_result.update({
            "summary": f"Analýza společnosti {company_name}",
            "key_findings": [
                "Neznámý typ analýzy, poskytnuty pouze základní informace",
                f"Společnost ID: {company_id}"
            ],
            "data_quality": "low"
        })
    
    return {"analysis_result": analysis_result}

def retrieve_additional_company_data(state: State) -> State:
    """
    Funkce pro získání dodatečných dat pro analýzu podle typu analýzy.
    Podporuje různé typy analýz (general, risk_comparison, supplier_analysis)
    a načítá odpovídající data z mock zdrojů.
    
    Args:
        state: Aktuální stav workflow
        
    Returns:
        Aktualizovaný stav s doplňujícími daty podle typu analýzy
    """
    try:
        # Získání základních údajů ze state
        company_name = getattr(state, "company_name", None)
        analysis_type = getattr(state, "analysis_type", "general")
        company_data = getattr(state, "company_data", {})
        
        # Pokud nemáme company_data, zkontrolujeme, zda máme alespoň jméno společnosti
        if not company_data:
            if not company_name:
                logger.error("Nelze získat další data - chybí jak company_data, tak company_name")
                return {"error_state": {"error": "Missing company data and name", "error_type": "invalid_data"}}
            
            # Vytvoříme minimální strukturu company_data
            company_data = {
                "basic_info": {
                    "name": company_name,
                    "id": company_name.lower().replace(" ", "_")
                }
            }
        
        # Získání ID společnosti z company_data
        company_id = company_data.get("basic_info", {}).get("id")
        if not company_id and company_name:
            # Pokud nemáme ID, ale máme jméno, vytvoříme ID z názvu
            company_id = company_name.lower().replace(" ", "_")
            if "basic_info" not in company_data:
                company_data["basic_info"] = {}
            company_data["basic_info"]["id"] = company_id
            logger.warning(f"Používám náhradní ID odvozené z názvu: {company_id}")
        
        if not company_id:
            logger.error("Nelze získat další data - chybí ID společnosti")
            return {"error_state": {"error": "Missing company ID", "error_type": "invalid_data"}}
        
        logger.info(f"Získávám doplňující data pro společnost ID: {company_id}, typ analýzy: {analysis_type}")
        
        # Vždy vytvoříme novou instanci MockMCPConnector - neukládáme ji do stavu
        from memory_agent.tools import MockMCPConnector
        logger.info("Vytvářím novou instanci MockMCPConnector")
        mcp_connector = MockMCPConnector()
        
        # Inicializace návratových dat
        financial_data = {}
        search_info = {}
        relationships_data = {}
        supply_chain_data = {}
        risk_factors_data = {}
        
        # Načítání dat podle typu analýzy
        try:
            logger.info(f"Načítání dat pro typ analýzy: {analysis_type}")
            
            # Pro všechny typy analýz načteme základní finanční data
            try:
                financial_data = mcp_connector.get_company_financials(company_id)
                logger.info("✅ Úspěšně načtena finanční data")
            except Exception as fin_error:
                logger.warning(f"⚠️ Nepodařilo se načíst finanční data: {str(fin_error)}")
                financial_data = {}
            
            # Načteme dodatečná data podle typu analýzy
            if analysis_type == "general":
                try:
                    search_info = mcp_connector.get_company_search_data(company_id)
                    logger.info("✅ Úspěšně načtena search data pro general analýzu")
                except Exception as search_error:
                    logger.warning(f"⚠️ Nepodařilo se načíst search data: {str(search_error)}")
                    search_info = {}
                
            elif analysis_type == "risk_comparison":
                try:
                    risk_factors_data = mcp_connector.get_risk_factors_data(company_id)
                    logger.info("✅ Úspěšně načtena risk data pro risk_comparison analýzu")
                except Exception as risk_error:
                    logger.warning(f"⚠️ Nepodařilo se načíst risk data: {str(risk_error)}")
                    risk_factors_data = {
                        "company_id": company_id,
                        "risk_score": None,
                        "all_risk_factors": []
                    }
                
            elif analysis_type == "supplier_analysis":
                try:
                    relationships = mcp_connector.get_company_relationships(company_id)
                    relationships_data = {company_id: relationships}
                    logger.info("✅ Úspěšně načtena data o vztazích pro supplier_analysis analýzu")
                except Exception as rel_error:
                    logger.warning(f"⚠️ Nepodařilo se načíst data o vztazích: {str(rel_error)}")
                    relationships_data = {company_id: []}
                
                try:
                    supply_chain = mcp_connector.get_supply_chain_data(company_id)
                    supply_chain_data = {company_id: supply_chain}
                    logger.info("✅ Úspěšně načtena data o supply chain pro supplier_analysis analýzu")
                except Exception as sc_error:
                    logger.warning(f"⚠️ Nepodařilo se načíst data o supply chain: {str(sc_error)}")
                    supply_chain_data = {company_id: []}
        
        except Exception as e:
            logger.error(f"Chyba při načítání dat: {str(e)}")
            # Pro PoC nebudeme řešit detailní chyby, ale zkusíme pokračovat s tím, co máme
        
        # Zkopírujeme existující company_data aby nedošlo k přepsání už načtených dat
        updated_company_data = dict(company_data)
        
        # Zachování původní basic_info
        if "basic_info" not in updated_company_data and company_data.get("basic_info"):
            updated_company_data["basic_info"] = company_data["basic_info"]
        
        # Doplnění dat podle typu analýzy
        if analysis_type == "general":
            updated_company_data["financials"] = financial_data
            updated_company_data["search_info"] = search_info
            
            # Zajištění, že máme všechny potřebné struktury dat
            if "basic_info" not in updated_company_data or not updated_company_data["basic_info"]:
                updated_company_data["basic_info"] = {
                    "name": company_name if company_name else "Unknown Company",
                    "id": company_id
                }
        
        elif analysis_type == "risk_comparison":
            updated_company_data["financials"] = financial_data
            
            # Pro risk analýzu potřebujeme také základní data společnosti
            if not updated_company_data.get("search_info"):
                try:
                    search_info = mcp_connector.get_company_search_data(company_id)
                    updated_company_data["search_info"] = search_info
                except Exception:
                    updated_company_data["search_info"] = {}
        
        elif analysis_type == "supplier_analysis":
            updated_company_data["financials"] = financial_data
            
            # Pro supplier analýzu můžeme potřebovat i základní data
            if not updated_company_data.get("search_info"):
                try:
                    search_info = mcp_connector.get_company_search_data(company_id)
                    updated_company_data["search_info"] = search_info
                except Exception:
                    updated_company_data["search_info"] = {}
        
        # Sestavení výsledku - neukládáme mcp_connector do stavu
        result = {
            "company_data": updated_company_data
            # NEUKLÁDAT mcp_connector do state - není serializovatelný pro checkpointy
        }
        
        # Přidání specializovaných dat podle typu analýzy
        if analysis_type == "risk_comparison":
            result["risk_factors_data"] = risk_factors_data
        elif analysis_type == "supplier_analysis":
            result["relationships_data"] = relationships_data
            result["supply_chain_data"] = supply_chain_data
        
        return result
    
    except Exception as e:
        logger.error(f"Chyba při získávání dat: {e}")
        logger.error(traceback.format_exc())
        return {"error_state": {"error": f"Data retrieval error: {str(e)}", "error_type": "data_access_error"}}

# Záložní řešení s regex vzory pokud LLM selhal
    if company_name == "Unknown":
        # Vzory pro nalezení názvu společnosti v dotazu
        patterns = [
            r"about\s+([A-Z][A-Za-z0-9\s\-]+)",  # "Tell me about MB TOOL"
            r"pro\s+([A-Za-z0-9\s\-]+)",    # "Analýza rizik pro MB TOOL"
            r"společnost\s+([A-Za-z0-9\s\-]+)"   # "Informace o společnosti MB TOOL"
        ]
        
        # Pokusíme se najít shodu s každým vzorem
        for pattern in patterns:
            import re
            
            match = re.search(pattern, query, re.IGNORECASE)
            if match and len(match.groups()) > 0:
                company_name = match.group(1).strip()
                logger.info(f"Regex analyzér rozpoznal společnost: {company_name}")
                break
    
    # Uložení výsledku dotazu na společnost
    state.company_query = {
        "query": query,
        "company_name": company_name
    }
    
    return {"company_name": company_name}

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

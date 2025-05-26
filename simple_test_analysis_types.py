#!/usr/bin/env python
"""
Jednoduchý test skript pro ověření podpory typů analýz.

Tento skript testuje pouze základní funkce bez rozsáhlých závislostí.
"""

import os
import sys
import json
import re
import glob
import logging
from typing import Dict, Any, List, Optional, Tuple

# Nastavení logování
logging.basicConfig(level=logging.INFO, 
                   format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("simple_test")

# Definice známých společností pro rychlé vyhledání
KNOWN_COMPANIES = {
    "MB TOOL": "risk_comparison",
    "ŠKODA AUTO": "general",
    "ADIS TACHOV": "risk_comparison", 
    "Flídr plast": "supplier_analysis",
    "BOS AUTOMOTIVE": "supplier_analysis",
    "BOS": "supplier_analysis",
    "FLIDR": "supplier_analysis",
    "Adis": "risk_comparison",
    "Škoda": "general"
}

def detect_analysis_type(query: str) -> str:
    """
    Detekce typu analýzy na základě klíčových slov v dotazu.
    
    Args:
        query: Text uživatelského dotazu
        
    Returns:
        str: Zjištěný typ analýzy
    """
    query = query.lower()
    
    # Klíčová slova pro detekci typu "risk_comparison"
    risk_keywords = [
        "risk", "rizik", "rizic", "compliance", "sanctions", "sankce", 
        "bezpečnost", "security", "regulace", "regulation", "embargo"
    ]
    
    # Klíčová slova pro detekci typu "supplier_analysis"
    supplier_keywords = [
        "supplier", "dodavatel", "supply chain", "vztahy", "dodávky", 
        "tier", "odběratel", "vendor", "nákup"
    ]
    
    if any(kw in query for kw in risk_keywords):
        logger.info(f"Detekován typ analýzy \"risk_comparison\" pro dotaz: {query[:30]}...")
        return "risk_comparison"
    elif any(kw in query for kw in supplier_keywords):
        logger.info(f"Detekován typ analýzy \"supplier_analysis\" pro dotaz: {query[:30]}...")
        return "supplier_analysis"
    else:
        logger.info(f"Detekován výchozí typ analýzy \"general\" pro dotaz: {query[:30]}...")
        return "general"

def analyze_company_query(query: str) -> Tuple[str, str]:
    """
    Jednoduchá funkce pro extrakci názvu společnosti a typu analýzy z dotazu.
    
    Args:
        query: Uživatelský dotaz k analýze
        
    Returns:
        Tuple of (název_společnosti, typ_analýzy)
    """
    # Kontrola známých společností
    for company, analysis_type in KNOWN_COMPANIES.items():
        if company in query:
            logger.info(f"Nalezena známá společnost: {company}, typ analýzy: {analysis_type}")
            return company, analysis_type
    
    # Jednoduchá extrakce pomocí regex - hledáme velká písmena následovaná textem
    company_pattern = r"[A-Z][A-Za-z0-9\s\-]+"
    matches = re.findall(company_pattern, query)
    
    if matches:
        company = matches[0].strip()
        logger.info(f"Extrahován název společnosti pomocí regex: {company}")
    else:
        company = "Unknown Company"
        logger.warning("Nepodařilo se extrahovat název společnosti z dotazu")
    
    # Detekce typu analýzy
    analysis_type = detect_analysis_type(query)
    
    return company, analysis_type

def test_analysis_types():
    """Test detekce typů analýz a extrakce společností."""
    logger.info("=== Test detekce typů analýz a extrakce společností ===")
    
    test_queries = [
        # Dotazy pro risk_comparison
        "Jaká jsou rizika pro MB TOOL?",
        "Compliance status for ADIS TACHOV",
        "Má BOS AUTOMOTIVE nějaké sankce?",
        
        # Dotazy pro supplier_analysis
        "Kdo jsou dodavatelé pro Flídr plast?",
        "Supply chain for BOS",
        "Ukaž mi tier 2 dodavatele pro ŠKODA AUTO",
        
        # Dotazy pro general
        "Co je to MB TOOL?",
        "Informace o společnosti ADIS TACHOV",
        "Tell me about BOS AUTOMOTIVE"
    ]
    
    for query in test_queries:
        logger.info(f"
Analýza dotazu: \"{query}\"")
        
        # Detekce typu analýzy
        analysis_type = detect_analysis_type(query)
        logger.info(f"- Detekovaný typ analýzy: {analysis_type}")
        
        # Extrakce společnosti a typu
        company, company_analysis = analyze_company_query(query)
        logger.info(f"- Extrahovaná společnost: {company}")
        logger.info(f"- Přiřazený typ analýzy: {company_analysis}")
        
        logger.info("-" * 40)

def main():
    """Hlavní funkce pro spuštění testů."""
    logger.info("🔍 Začínám testovat funkce pro analýzu typů")
    
    # Test detekce typů analýz
    test_analysis_types()
    
    logger.info("
✅ Všechny testy dokončeny")

if __name__ == "__main__":
    main()

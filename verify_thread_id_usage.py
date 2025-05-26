#!/usr/bin/env python3
"""
Skript pro kontrolu a opravu používání thread_id v testovacích souborech.

Tento skript projde zadané soubory a ověří, zda správně používají
konfiguraci s thread_id při volání grafu.
"""

import os
import sys
import re
import logging
import argparse
from typing import List, Tuple, Dict, Any

# Nastavení loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Regulární výrazy pro hledání volání grafu
INVOKE_PATTERN = r'(?:graph|analyzer)\.invoke\(\s*(?:{[^}]*}|\[[^\]]*\]|"[^"]*"|\'[^\']*\')(?:\s*,\s*config\s*=\s*({[^}]*}))?'

def check_thread_id_usage(file_path: str) -> Tuple[bool, List[Tuple[int, str, bool]]]:
    """
    Zkontroluje správné používání thread_id v souboru.
    
    Args:
        file_path: Cesta k souboru
        
    Returns:
        Tuple obsahující celkový výsledek (True pokud vše v pořádku) a seznam
        detailů o nalezených problémech (číslo řádku, text, má thread_id)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    issues = []
    total_ok = True
    
    # Hledání volání invoke
    for i, line in enumerate(lines):
        # Přeskočení komentářů
        if line.strip().startswith('#'):
            continue
        
        match = re.search(INVOKE_PATTERN, line)
        if match:
            config = match.group(1) if len(match.groups()) > 0 else None
            has_thread_id = config and 'thread_id' in config
            
            if not has_thread_id:
                total_ok = False
                issues.append((i+1, line, has_thread_id))
    
    return total_ok, issues

def print_report(file_path: str, total_ok: bool, issues: List[Tuple[int, str, bool]]) -> None:
    """
    Vytiskne přehledný report o kontrole souboru.
    """
    if total_ok:
        logger.info(f"✅ {file_path}: všechna volání grafu mají správně thread_id")
    else:
        logger.warning(f"⚠️ {file_path}: nalezeny problémy s thread_id:")
        for line_num, text, has_thread_id in issues:
            logger.warning(f"  Řádek {line_num}: {text.strip()}")
            logger.warning(f"  Problém: {'thread_id chybí v konfiguraci' if not has_thread_id else 'jiný problém'}")
            logger.warning(f"  Doporučení: přidejte config={{'configurable': {{'thread_id': 'unikátní-id'}}}}")
            logger.warning("  ----------")

def process_files(file_paths: List[str], auto_fix: bool = False) -> Dict[str, Any]:
    """
    Zpracuje více souborů a vrátí souhrnný report.
    
    Args:
        file_paths: Seznam cest k souborům
        auto_fix: Pokud True, pokusí se automaticky opravit nalezené problémy
        
    Returns:
        Slovník s výsledky kontroly
    """
    results = {
        'total_files': len(file_paths),
        'files_with_issues': 0,
        'total_issues': 0,
        'fixed_issues': 0,
        'details': {}
    }
    
    for file_path in file_paths:
        if not os.path.isfile(file_path):
            logger.warning(f"⚠️ Soubor neexistuje: {file_path}")
            continue
        
        try:
            total_ok, issues = check_thread_id_usage(file_path)
            results['details'][file_path] = {
                'ok': total_ok,
                'issues': len(issues)
            }
            
            if not total_ok:
                results['files_with_issues'] += 1
                results['total_issues'] += len(issues)
            
            print_report(file_path, total_ok, issues)
        except Exception as e:
            logger.error(f"❌ Chyba při zpracování souboru {file_path}: {str(e)}")
    
    logger.info(f"\n===== SOUHRN =====")
    logger.info(f"Zkontrolováno souborů: {results['total_files']}")
    logger.info(f"Souborů s problémy: {results['files_with_issues']}")
    logger.info(f"Celkem nalezeno problémů: {results['total_issues']}")
    
    if results['files_with_issues'] > 0:
        logger.warning("Některé soubory nemají správně implementované thread_id v konfiguraci.")
        logger.warning("Pro správnou funkci checkpointů je potřeba přidat thread_id ke všem voláním graph.invoke().")
        logger.warning("Příklad správného volání:")
        logger.warning("config = {\"configurable\": {\"thread_id\": \"unikátní-id\"}}")
        logger.warning("graph.invoke({\"messages\": [...]}, config=config)")
    else:
        logger.info("✅ Všechny kontrolované soubory správně používají thread_id!")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Kontrola a oprava používání thread_id v Python souborech.')
    parser.add_argument('files', nargs='+', help='Soubory k zkontrolování')
    parser.add_argument('--auto-fix', action='store_true', help='Automaticky opravit nalezené problémy (zatím nepodporováno)')
    
    args = parser.parse_args()
    
    if args.auto_fix:
        logger.warning("Automatické opravy zatím nejsou podporovány.")
    
    process_files(args.files, args.auto_fix)

if __name__ == "__main__":
    main()

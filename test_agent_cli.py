#!/usr/bin/env python
"""
Jednoduchý testovací skript pro AI-agent-Ntier.

Tento skript umožňuje testovat agenta lokálně pomocí jednoduchého CLI rozhraní.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List
import requests

def setup_argument_parser() -> argparse.ArgumentParser:
    """Nastaví parser argumentů příkazové řádky."""
    parser = argparse.ArgumentParser(description="Testovací CLI pro AI-agent-Ntier")
    parser.add_argument("--query", "-q", type=str, help="Dotaz pro analýzu")
    parser.add_argument("--thread", "-t", type=str, default="default", help="ID threadu pro persistenci")
    parser.add_argument("--server", "-s", type=str, default="http://127.0.0.1:2024", help="URL LangGraph serveru")
    return parser

def query_agent(question: str, thread_id: str = "default", server_url: str = "http://127.0.0.1:2024") -> Dict[str, Any]:
    """Odešle dotaz na agenta prostřednictvím LangGraph Platform."""
    url = f"{server_url}/agents/agent/invoke"
    
    payload = {
        "input": {
            "messages": [{"type": "human", "content": question}],
            "original_query": question
        },
        "config": {
            "configurable": {
                "thread_id": thread_id
            }
        }
    }
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60
        )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP chyba: {err}")
        print(f"Odpověď serveru: {response.text}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Chyba připojení k serveru {server_url}.")
        print("Je server spuštěný? Zkontrolujte, zda běží ./run_langgraph_dev.sh")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Timeout - server neodpovídá v očekávaném čase.")
        sys.exit(1)
    except Exception as e:
        print(f"Neočekávaná chyba: {e}")
        sys.exit(1)

def display_result(result: Dict[str, Any]) -> None:
    """Zobrazí výsledek odpovědi agenta v čitelném formátu."""
    if "output" in result and "messages" in result["output"]:
        # Nalezení odpovědi od agenta
        for message in result["output"]["messages"]:
            if message.get("type") == "ai":
                print("\n" + "=" * 80)
                print("ODPOVĚĎ AGENTA:\n")
                print(message["content"])
                print("=" * 80 + "\n")
                return
        
        # Pokud nebyla nalezena zpráva typu "ai"
        print("\nOdpověď neobsahuje zprávu od agenta.")
    else:
        print("\nNeplatný formát odpovědi od serveru:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

def main() -> None:
    """Hlavní funkce skriptu."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Pokud není zadán dotaz, požádáme o něj interaktivně
    if not args.query:
        print("Zadejte dotaz pro analýzu (nebo 'exit' pro ukončení):")
        while True:
            query = input("> ")
            if query.lower() in ("exit", "quit", "konec"):
                break
                
            result = query_agent(query, args.thread, args.server)
            display_result(result)
            print("\nZadejte další dotaz (nebo 'exit' pro ukončení):")
    else:
        # Jednorázové zpracování dotazu
        result = query_agent(args.query, args.thread, args.server)
        display_result(result)

if __name__ == "__main__":
    main()

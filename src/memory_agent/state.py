"""
Define the shared state management for Memory Agent workflow.

Tento modul obsahuje State třídu, která slouží jako centrální systém
správy stavu pro Memory Agent. Využívá moderní vzory správy stavu LangGraph
včetně struktur podobných TypedDict s implementací dataclass a specializovaných
reducerů stavu prostřednictvím Annotated typů.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.messages import AnyMessage

try:
    from langgraph.graph import add_messages
except ImportError:
    # Použití mock implementace, pokud langgraph není dostupný
    from memory_agent.mock_langgraph import add_messages
from typing_extensions import Annotated

# Import pro MockMCPConnector

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Import AnalysisResult odstraněn, používáme Dict[str, Any] s reducery


def merge_dict_values(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sloučí hodnoty slovníků pro aktualizaci stavu.

    Tato reducer funkce kombinuje dva slovníky, zachovává hodnoty z obou,
    když nejsou v konfliktu, a používá hodnoty z pravé strany, když jsou.

    Args:
        left: Původní slovník ve stavu
        right: Nový slovník, který má být sloučen do stavu

    Returns:
        Dict[str, Any]: Aktualizovaný sloučený slovník
    """
    if not right:
        return left

    # Převod dict-like objektů na standardní dict před zpracováním
    # Toto opravuje chybu serializace s proto.marshal.collections.maps.MapComposite
    if left is not None and hasattr(left, "items") and not isinstance(left, dict):
        logger.warning(
            f"Převádím objekt typu {type(left)} na dict pro zajištění serializovatelnosti"
        )
        left = dict(left)
    
    if right is not None and hasattr(right, "items") and not isinstance(right, dict):
        logger.warning(
            f"Převádím objekt typu {type(right)} na dict pro zajištění serializovatelnosti"
        )
        right = dict(right)

    # Bezpečné kopírování: řeší problém s objekty, které nemají metodu copy()
    if left is None:
        result = {}
    else:
        try:
            result = left.copy()
        except AttributeError:
            # Pokud objekt nemá metodu copy(), vytvoříme nový slovník
            result = {}
            logger.warning(
                f"Objekt typu {type(left)} nemá metodu copy(), vytvářím nový slovník"
            )

    result.update(right)
    return result


def ensure_serializable(obj: Any) -> Any:
    """
    Zajistí, že objekt je serializovatelný do JSON.
    
    Převádí dict-like objekty (včetně MapComposite) na standardní dict,
    aby se předešlo chybám serializace na LangGraph Platform.
    
    Args:
        obj: Objekt k ověření a případné konverzi
        
    Returns:
        Serializovatelný objekt
    """
    if obj is None:
        return obj
    
    # Převod dict-like objektů na dict
    if hasattr(obj, "items") and not isinstance(obj, dict):
        logger.info(f"Převádím dict-like objekt typu {type(obj)} na dict")
        return dict(obj)
    
    # Rekurzivní zpracování pro slovníky
    if isinstance(obj, dict):
        return {key: ensure_serializable(value) for key, value in obj.items()}
    
    # Rekurzivní zpracování pro seznamy
    if isinstance(obj, list):
        return [ensure_serializable(item) for item in obj]
    
    # Rekurzivní zpracování pro tuple (převést na list)
    if isinstance(obj, tuple):
        return [ensure_serializable(item) for item in obj]
    
    # Ostatní typy vrátit beze změny
    return obj


# BLOKOVÁNO(B1): Implementace stavového grafu čeká na dokončení unit testů pro tools.py (A4)
@dataclass(kw_only=True)
class State:
    """
    Hlavní stav grafu pro workflow Memory Agent.

    Tato třída definuje celou strukturu správy stavu pro Memory Agent,
    která zpracovává historii konverzace, výsledky analýz, data společností a chybové stavy.
    Každé pole používá vhodné typové anotace a reducery k zajištění správné
    správy stavu v průběhu workflow LangGraph.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    """
    Zprávy v konverzaci.

    Toto pole používá reducer add_messages z LangGraph k správnému
    připojení nových zpráv k historii konverzace při zachování
    jejich správného pořadí a vztahů. Reducer zpracovává různé
    typy zpráv (uživatel, asistent, nástroj) a zajišťuje jejich správné formátování.
    """

    company_analysis: Annotated[Dict[str, Any], merge_dict_values] = field(
        default_factory=dict
    )
    """
    Výsledek analýzy společností z uživatelského dotazu.

    Obsahuje výsledky analýzy entit společností extrahovaných z uživatelských dotazů,
    včetně identifikovaných názvů společností, asociací a případných disambiguací.
    Používá reducer merge_dict_values pro akumulaci informací z různých zdrojů analýzy.
    """

    # Nové atributy pro rozšířenou funkcionalitu
    company_data: Annotated[Dict[str, Any], merge_dict_values] = field(
        default_factory=dict
    )
    """
    Strukturovaná data o společnostech získaná z různých zdrojů.

    Obsahuje detailní informace o společnostech včetně identifikátorů,
    metadat a informací o zdroji. Používá reducer merge_dict_values
    pro správné kombinování informací z více zdrojů nebo analytických kroků.
    """

    internal_data: Annotated[Dict[str, Any], merge_dict_values] = field(
        default_factory=dict
    )
    """
    Interní data používaná workflow, která nejsou přímo součástí výstupu.

    Zahrnuje informace pro interní správu stavu, dočasné výsledky výpočtů
    a další data potřebná během provádění workflow, ale nezahrnutá do konečných výstupů.
    """

    relationships_data: Annotated[
        Dict[str, List[Dict[str, Any]]], merge_dict_values
    ] = field(default_factory=dict)
    """
    Data o vztazích mezi entitami identifikovanými ve workflow.

    Mapuje identifikátory entit na seznamy dat o vztazích, což umožňuje workflow
    sledovat komplexní sítě vztahů mezi společnostmi a dalšími entitami.
    """

    error_state: Dict[str, Any] = field(default_factory=dict)
    """
    Informace o chybách, když workflow narazí na problémy.

    Obsahuje detailní informace o chybách včetně typu chyby, zprávy,
    komponenty, která chybu vygenerovala, a případných pokusů o zotavení.
    """

    output: Dict[str, Any] = field(default_factory=dict)
    """
    Finální zpracovaný výstup workflow.

    Obsahuje strukturovaná výstupní data připravená k prezentaci uživateli,
    včetně zpracovaných informací o společnostech, dat o vztazích a případně
    vygenerovaných postřehů nebo doporučení.
    """

    mcp_connector_config: Optional[Any] = None
    """
    Konfigurace pro MockMCPConnector.

    Místo přímé instance používáme serializovatelnou konfiguraci.
    To umožňuje správné generování JSON schématu pro LangGraph Platform.
    """

    mcp_connector: Annotated[Any, merge_dict_values] = field(default=None)
    """
    Instance MockMCPConnector pro přístup k datům.

    Tato instance je dostupná přímo jako atribut state objektu.
    Při deploymentu na LangGraph Platform je inicializována v uzlech grafu.
    """

    def get_mcp_connector(self):
        """
        Vrátí instanci MockMCPConnector z konfigurace.

        Nejprve zkontroluje, zda již existuje mcp_connector atribut,
        a pokud ne, vytvoří novou instanci a uloží ji do mcp_connector.

        Returns:
            MockMCPConnector: Instance konektoru pro přístup k datům
        """
        # Nejprve zkontrolovat, zda už máme instanci konektoru
        if self.mcp_connector is not None:
            return self.mcp_connector

        # Pokud ne, vytvořit novou instanci
        from memory_agent.schema import MockMCPConnectorConfig
        from memory_agent.tools import MockMCPConnector

        if self.mcp_connector_config is None:
            self.mcp_connector_config = MockMCPConnectorConfig()

        if isinstance(self.mcp_connector_config, dict):
            config = MockMCPConnectorConfig(**self.mcp_connector_config)
        else:
            config = self.mcp_connector_config

        # Vytvořit instanci a uložit ji přímo do atributu mcp_connector
        self.mcp_connector = MockMCPConnector(data_path=config.data_path)
        return self.mcp_connector

    # Podpora pro konfigurace
    config: Optional[Any] = None
    """Konfigurace pro běh workflow."""

    # Podpora pro aktuální dotaz
    current_query: Optional[str] = None
    """Aktuální dotaz uživatele zpracovávaný workflow."""

    # Podpora pro analýzu
    analysis_result: Annotated[Dict[str, Any], merge_dict_values] = field(
        default_factory=dict
    )
    """Výsledek analýzy uživatelského dotazu."""

    # State rozšíření pro LangGraph Platform
    query_type: Optional[str] = None
    """Typ dotazu identifikovaný během analýzy."""

    analysis_type: Optional[str] = None
    """Typ analýzy identifikovaný z uživatelského dotazu (general, risk_comparison, supplier_analysis)."""

    company_name: Optional[str] = None
    """Název společnosti extrahovaný z uživatelského dotazu."""


# AgentState pro přímou integraci s LangGraph Platform
AgentState = State


__all__ = ["State", "AgentState", "merge_dict_values", "ensure_serializable"]

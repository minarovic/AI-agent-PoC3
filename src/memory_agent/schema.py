"""
Schéma a datové modely pro Memory Agent.

Tento modul obsahuje Pydantic modely pro strukturované vstupy a výstupy,
které jsou používány v aplikaci a pro generování JSON schémat pro LangGraph Platform.
"""

from typing import Dict, List, Optional, Any, Literal, Union, Tuple
import os
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

# Definice typů analýz
AnalysisType = Literal["risk_comparison", "supplier_analysis", "general"]

# Validní typy analýz
VALID_ANALYSIS_TYPES = ["risk_comparison", "supplier_analysis", "general"]


class CompanyQueryParams(BaseModel):
    """Parametry pro dotazy na firmy."""
    name: Optional[str] = Field(None, description="Název společnosti")
    id: Optional[str] = Field(None, description="ID společnosti")
    country: Optional[str] = Field(None, description="Země, kde společnost sídlí")
    industry: Optional[List[str]] = Field(None, description="Seznam průmyslových odvětví")


class MockMCPConnectorConfig(BaseModel):
    """
    Konfigurace pro MockMCPConnector.
    
    Tento model definuje konfigurační parametry pro přístup k mock datům
    a zajišťuje serializovatelnost do JSON schématu pro LangGraph Platform.
    """
    data_path: str = Field(
        default=str(Path(__file__).parent.parent.parent / "mock_data"),
        description="Cesta k adresáři s mock daty"
    )
    
    # Povolit další atributy pro zpětnou kompatibilitu
    model_config = ConfigDict(extra="allow")


class CompanyData(BaseModel):
    """Data společnosti vrácená z MCP Connectoru."""
    id: str = Field(..., description="Jedinečný identifikátor společnosti")
    name: str = Field(..., description="Název společnosti")
    type: str = Field("company", description="Typ entity")
    industry: Optional[str] = Field(None, description="Průmyslové odvětví")
    country: Optional[str] = Field(None, description="Země sídla")
    risk_score: Optional[str] = Field(None, description="Skóre rizika")
    risk_factors: Optional[Dict[str, Any]] = Field(None, description="Faktory rizika")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Další metadata")
    
    # Povolit další atributy pro zpětnou kompatibilitu
    model_config = ConfigDict(extra="allow")


class PersonData(BaseModel):
    """
    Data o osobě.
    
    Tento model reprezentuje strukturované informace o osobě
    z mock databáze.
    """
    id: Optional[str] = Field(
        None,
        description="Jedinečný identifikátor osoby"
    )
    name: Optional[str] = Field(
        None,
        description="Jméno osoby"
    )
    type: Optional[str] = Field(
        "person",
        description="Typ entity (obvykle 'person')"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Další metadata o osobě"
    )
    
    model_config = ConfigDict(extra="allow")


class RelationshipData(BaseModel):
    """
    Data o vztahu mezi entitami.
    
    Tento model reprezentuje strukturované informace o vztahu
    mezi dvěma entitami z mock databáze.
    """
    source_id: Optional[str] = Field(
        None,
        description="ID zdrojové entity"
    )
    target_id: Optional[str] = Field(
        None,
        description="ID cílové entity"
    )
    relationship_type: Optional[str] = Field(
        None,
        description="Typ vztahu mezi entitami"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Další metadata o vztahu"
    )
    
    model_config = ConfigDict(extra="allow")


# DTO objekty pro výstupy analýz

class AnalysisResult(BaseModel):
    """
    Výsledek analýzy uživatelského vstupu.
    
    Tento model reprezentuje strukturovaný výsledek analýzy
    uživatelského dotazu s identifikací společností a typu analýzy.
    """
    companies: List[str] = Field(
        description="Seznam identifikovaných společností"
    )
    company: str = Field(
        description="Primární společnost (první v seznamu)"
    )
    analysis_type: AnalysisType = Field(
        description="Typ analýzy k provedení"
    )
    query: str = Field(
        description="Původní uživatelský dotaz"
    )

    model_config = ConfigDict(extra="allow")

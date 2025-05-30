"""
Schémata pro serializovatelné objekty v Memory Agent.

Tento modul obsahuje modely použité pro serializaci
objektů, které jsou součástí stavového grafu LangGraph.
"""

from typing import Dict, Any, List, Optional

class MockMCPConnectorConfig:
    """
    Konfigurace pro MockMCPConnector.
    
    Tento model je serializovatelný a lze jej použít
    pro ukládání konfigurace MockMCPConnector v JSON serializovatelném
    formátu v rámci State objektu.
    """
    def __init__(self, data_path: str = "./mock_data"):
        """
        Inicializace konfigurace.
        
        Args:
            data_path: Cesta k adresáři s mock daty
        """
        self.data_path = data_path
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Převede konfiguraci na slovník.
        
        Returns:
            Slovník s konfigurací
        """
        return {"data_path": self.data_path}
"""
Definice systémových a uživatelských promptů pro LLM.

Tento modul obsahuje registry promptů a pomocné funkce pro generování
a správu promptů pro různé části workflow.
"""

from typing import Dict, Any, Optional
import logging

from memory_agent.state import State

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Systémový prompt pro Memory Agent
SYSTEM_PROMPT = """Jsi AI asistent Memory Agent, specializovaný na analýzu vztahů mezi společnostmi, osobami a organizacemi.

Při zpracování dotazů dodržuj tyto pokyny:
1. Poskytuj stručné, věcné a faktické odpovědi založené na dostupných datech.
2. Pokud nemáš informace k zodpovězení dotazu, řekni to jasně a nepokoušej se hádat.
3. Zaměř se na analýzu dat a klíčové postřehy.
4. Udržuj strukturované a organizované odpovědi s vhodným použitím odrážek a sekcí.

Tvým cílem je poskytnout jasnou, přesnou a užitečnou analýzu na základě dostupných dat."""


# Třída pro registry promptů
class PromptRegistry:
    """Registr promptů pro různé části workflow."""

    _prompts: Dict[str, str] = {
        "system_prompt": SYSTEM_PROMPT,  # Add system prompt to registry
        "company_analysis": """Proveď analýzu společnosti na základě dostupných dat.
        
        Společnost: {company_name}
        
        Dostupná data:
        {company_data}
        
        Finanční data:
        {financial_data}
        
        Vztahy:
        {relationships}
        
        Poskytni stručnou, ale informativní analýzu, která zahrnuje:
        1. Základní informace o společnosti
        2. Klíčové finanční ukazatele a trendy
        3. Významné vztahy a propojení
        4. Potenciální rizika nebo příležitosti""",
        "person_analysis": """Proveď analýzu osoby na základě dostupných dat.
        
        Osoba: {person_name}
        
        Dostupná data:
        {person_data}
        
        Vztahy:
        {relationships}
        
        Poskytni stručnou, ale informativní analýzu, která zahrnuje:
        1. Základní informace o osobě
        2. Klíčové role a pozice
        3. Významné vztahy a propojení
        4. Potenciální oblasti zájmu""",
        "relationship_analysis": """Proveď analýzu vztahů mezi entitami na základě dostupných dat.
        
        Entity: {entity_names}
        
        Dostupná data:
        {entities_data}
        
        Vztahy:
        {relationships}
        
        Poskytni stručnou, ale informativní analýzu, která zahrnuje:
        1. Typy identifikovaných vztahů
        2. Sílu a významnost vztahů
        3. Časový vývoj vztahů (pokud je k dispozici)
        4. Potenciální implikace a důsledky vztahů""",
        "error_handling": """Omlouvám se, při zpracování Vašeho dotazu došlo k chybě.
        
        Typ chyby: {error_type}
        
        Detaily: {error_message}
        
        Doporučení:
        {recommendations}
        
        Zkuste prosím:
        1. Přeformulovat svůj dotaz
        2. Poskytnout více specifických informací
        3. Rozdělit složitý dotaz na více jednodušších""",
    }

    @classmethod
    def get_prompt(cls, prompt_id: str) -> Optional[str]:
        """
        Získá prompt podle ID.

        Args:
            prompt_id: Identifikátor promptu

        Returns:
            Optional[str]: Text promptu nebo None, pokud prompt neexistuje
        """
        if prompt_id in cls._prompts:
            return cls._prompts[prompt_id]

        logger.warning(f"Prompt s ID '{prompt_id}' nebyl nalezen")
        return None

    @classmethod
    def add_prompt(cls, prompt_id: str, prompt_text: str) -> None:
        """
        Přidá nový prompt do registru.

        Args:
            prompt_id: Identifikátor promptu
            prompt_text: Text promptu
        """
        cls._prompts[prompt_id] = prompt_text
        logger.info(f"Přidán nový prompt s ID '{prompt_id}'")

    @classmethod
    def update_prompt(cls, prompt_id: str, prompt_text: str) -> bool:
        """
        Aktualizuje existující prompt.

        Args:
            prompt_id: Identifikátor promptu
            prompt_text: Nový text promptu

        Returns:
            bool: True pokud byl prompt aktualizován, False pokud neexistuje
        """
        if prompt_id in cls._prompts:
            cls._prompts[prompt_id] = prompt_text
            logger.info(f"Aktualizován prompt s ID '{prompt_id}'")
            return True

        logger.warning(f"Nelze aktualizovat - prompt s ID '{prompt_id}' neexistuje")
        return False


# Třída pro formátování dat pro prompty
class PromptDataFormatter:
    """Formátuje data ze stavu pro použití v promptech."""

    @staticmethod
    def format_company_data(company_data: Dict[str, Any]) -> str:
        """
        Formátuje data o společnosti pro použití v promptu.

        Args:
            company_data: Data společnosti

        Returns:
            str: Formátovaná data
        """
        if not company_data:
            return "Nejsou k dispozici žádná data o společnosti."

        result = []

        # Základní informace
        basic_info = company_data.get("basic_info", {})
        if basic_info:
            result.append("## Základní informace")
            result.append(f"Název: {basic_info.get('name', 'N/A')}")
            result.append(f"ID: {basic_info.get('id', 'N/A')}")
            result.append(f"Země: {basic_info.get('country', 'N/A')}")
            result.append(f"Odvětví: {basic_info.get('industry', 'N/A')}")
            result.append("")

        # Finanční data
        financials = company_data.get("financials", {})
        if financials:
            result.append("## Finanční údaje")
            result.append(f"Příjmy: {financials.get('revenue', 'N/A')}")
            result.append(f"Zisk: {financials.get('profit', 'N/A')}")
            result.append(f"Rok: {financials.get('year', 'N/A')}")
            result.append("")

        return "\n".join(result)

    @staticmethod
    def format_relationships(relationships_data: Dict[str, Any]) -> str:
        """
        Formátuje data o vztazích pro použití v promptu.

        Args:
            relationships_data: Data o vztazích

        Returns:
            str: Formátovaná data
        """
        if not relationships_data:
            return "Nejsou k dispozici žádná data o vztazích."

        result = ["## Vztahy"]

        for entity_id, relationships in relationships_data.items():
            result.append(f"### Entity ID: {entity_id}")

            if not relationships:
                result.append("Žádné vztahy nenalezeny.")
                continue

            for rel in relationships:
                rel_type = rel.get("type", "Neznámý typ")
                source = rel.get("source_name", rel.get("source_id", "Neznámý zdroj"))
                target = rel.get("target_name", rel.get("target_id", "Neznámý cíl"))
                strength = rel.get("strength", "N/A")

                result.append(f"- {rel_type}: {source} -> {target} (Síla: {strength})")

            result.append("")

        return "\n".join(result)


# Třída pro skládání řetězců promptů
class PromptChainBuilder:
    """Vytváří řetězce promptů pro zpracování workflow."""

    @classmethod
    def build_company_analysis_prompt(cls, state: State) -> str:
        """
        Vytvoří prompt pro analýzu společnosti.

        Args:
            state: Aktuální stav workflow

        Returns:
            str: Sestavený prompt
        """
        # Získání základního promptu
        base_prompt = PromptRegistry.get_prompt("company_analysis")
        if not base_prompt:
            logger.error("Nelze najít prompt pro analýzu společnosti")
            return "Nelze provést analýzu společnosti - chybí šablona promptu."

        # Formátování dat
        company_name = state.company_data.get("basic_info", {}).get(
            "name", "Neznámá společnost"
        )
        company_data_formatted = PromptDataFormatter.format_company_data(
            state.company_data
        )

        # Získání dat o vztazích
        company_id = state.company_data.get("basic_info", {}).get("id")
        relationships_formatted = ""
        if company_id and company_id in state.relationships_data:
            relationships_formatted = PromptDataFormatter.format_relationships(
                {company_id: state.relationships_data[company_id]}
            )

        # Sestavení promptu
        return base_prompt.format(
            company_name=company_name,
            company_data=company_data_formatted,
            financial_data="Nejsou k dispozici",  # Placeholder - ve skutečné implementaci by zde byla data
            relationships=relationships_formatted,
        )


# Pomocná funkce pro formátování stavu pro prompty
def format_state_for_prompt(state: State) -> Dict[str, Any]:
    """
    Formátuje stav pro použití v promptech.

    Args:
        state: Aktuální stav workflow

    Returns:
        Dict[str, Any]: Formátovaná data ze stavu
    """
    return {
        "company_data": state.company_data,
        "relationships": state.relationships_data,
        "query": state.current_query,
        "error": state.error_state,
    }

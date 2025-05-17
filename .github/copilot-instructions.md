# Souhrn změn v instrukcích pro Copilot Agenta

## Klíčové změny a nové prvky

### 1. Zaměření na nasazení
Hlavní zaměření instrukcí bylo přeorientováno na nasazení projektu AI-agent-Ntier na GitHub a následně na LangGraph Platform, což odpovídá aktuální prioritě projektu.

### 2. Implementace CoT a MCP metodiky
Do instrukcí byla explicitně zahrnuta metodika Chain of Thought (CoT) prompting a Multi-Chain Prompting (MCP) sequential thinking pro strukturované a systematické řešení problémů. Tato metodika pomůže Copilot Agentovi:
- Jasně strukturovat své myšlení a návrhy
- Systematicky analyzovat problémy 
- Dokumentovat svůj myšlenkový postup
- Poskytovat ucelenější a propracovanější řešení

### 3. Minimalizace práce s citlivými údaji
Byl přidán důraz na minimalizaci práce s API klíči a citlivými údaji, s jasným pokynem pracovat pouze s tím, co je nezbytně nutné. Tyto změny zahrnují:
- Jasný zákaz zahrnování skutečných API klíčů do kódu
- Preference pro používání proměnných prostředí a GitHub Secrets
- Odkaz na existující bezpečnostní checklist

### 4. Self-checkpointing
Přidána sekce o automatické dokumentaci práce (self-checkpointing) pro případy, kdy Copilot Agent řeší složitější úkoly:
- Standardizovaný formát checkpointu
- Jasné rozčlenění na dokončené, probíhající a plánované kroky
- Zachování kontextu pro případ jeho ztráty

### 5. Strukturované kroky pro nasazení
Instrukce nově obsahují konkrétní kroky pro:
- Nasazení na GitHub s důrazem na správnou konfiguraci CI/CD
- Nasazení na LangGraph Platform s detaily ke konfiguraci langgraph.json
- Řešení potenciálních problémů během nasazení

### 6. Odkazy na klíčové soubory projektu
Do instrukcí byly přidány odkazy na důležité soubory projektu, které by měl Copilot Agent využívat jako referenci:
- CI/CD workflow v .github/workflows/
- Deployment skripty
- Konfigurační soubory
- Dokumentaci bezpečnostních postupů

## Očekávané výhody nových instrukcí

1. **Jasnější prioritizace**: Copilot Agent bude mít lepší představu o tom, na co se má prioritně zaměřit.

2. **Systematičtější přístup**: Díky CoT a MCP metodice bude agent poskytovat strukturovanější a propracovanější odpovědi.

3. **Lepší dokumentace práce**: Self-checkpointing zajistí kontinuitu i při potenciální ztrátě kontextu.

4. **Vyšší bezpečnost**: Minimalizace práce s citlivými údaji sníží riziko bezpečnostních incidentů.

5. **Efektivnější nasazení**: Jasné kroky pro nasazení na obě platformy usnadní a zefektivní tento proces.


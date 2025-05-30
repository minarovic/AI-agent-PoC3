## [2025-05-18] - Postup sloučení repozitářů AI-agent-PoC3 a AI-agent-Ntier

### Identifikovaný problém:
- Existují dva oddělené repozitáře se stejným kódem: AI-agent-PoC3 a AI-agent-Ntier
- LangGraph Platform používá repozitář AI-agent-PoC3, který neobsahuje nejnovější opravy
- Chyba `TypeError: 'State' object is not subscriptable` přetrvává v produkčním prostředí
- Repozitáře byly vytvořeny dočasně kvůli problémům se schématem

### Analýza příčiny:
- Verze repozitáře `AI-agent-PoC3`, která běží na platformě, používá nesprávný přístup k objektu `State` v lambda funkci: `lambda x: x["state"].query_type`
- V aktuálním repozitáři `AI-agent-Ntier` již byla tato chyba opravena na: `lambda x: x.query_type`
- Opravená verze však nebyla nasazena, protože se pracovalo ve dvou oddělených repozitářích

### Navrhované řešení:
- [x] Vytvořit skript pro sloučení repozitářů do jednoho
- [x] Zajistit prioritní zachování oprav, zejména správné lambda funkce v graph.py
- [x] Aktualizovat konfiguraci v langgraph.json pro správné nasazení
- [x] Připravit dokumentaci průběhu sloučení a důležitých změn
- [ ] Nasadit sloučený repozitář na LangGraph Platform
- [ ] Verifikovat, že chyba již nenastává

### Implementace:
1. Vytvořen skript `merge_repositories.sh` s následujícími funkcemi:
   - Zálohování obou repozitářů před sloučením
   - Přidání AI-agent-PoC3 jako remote repozitáře
   - Vytvoření nové větve pro sloučení
   - Provedení merge s prioritním zachováním opravených verzí souborů
   - Aktualizace konfigurace v langgraph.json
   - Přidání záznamu o merge do dokumentace

2. Implementace kontroly klíčových souborů:
   - Kontrola souboru graph.py, zda obsahuje správnou lambda funkci
   - Příprava automatického obnovení důležitých souborů v případě nechtěné přepsání během merge
   - Vizualizace postupu v PlantUML diagramu

3. Konfigurace pro správné nasazení:
   - Aktualizace langgraph.json na používání správných cest v AI-agent-Ntier
   - Zajištění konzistence mezi lokálním vývojem a produkčním prostředím

### Postup použití merge skriptu:
1. Zajistěte, že máte přístup k oběma repozitářům
2. Spusťte skript v repozitáři AI-agent-Ntier:
   ```bash
   chmod +x merge_repositories.sh
   ./merge_repositories.sh
   ```
3. Zadejte cestu k repozitáři AI-agent-PoC3 dle výzvy
4. Řešte případné konflikty dle pokynů v průběhu skriptu
5. Po dokončení zkontrolujte, commit a nasaďte změny

### Verifikace:
- Po sloučení repozitářů a nasazení proveďte test v produkčním prostředí
- Ověřte, že chyba `TypeError: 'State' object is not subscriptable` již nenastává
- Zkontrolujte logovací soubory pro potvrzení úspěšného nasazení

### Další kroky po sloučení:
1. Aktualizujte všechny CI/CD skripty, aby používaly pouze sloučený repozitář
2. Upravte dokumentaci projektu, aby reflektovala nové struktura repozitáře
3. Zvažte archivaci původního repozitáře AI-agent-PoC3 po úspěšném nasazení

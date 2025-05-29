# Propojení GitHub s LangGraph Platform

Tento návod popisuje kroky potřebné k propojení GitHub repozitáře s LangGraph Platform pro automatické nasazování aplikace.

## Přístup k administraci LangGraph Platform

1. Přihlaste se ke svému účtu na [LangGraph Platform](https://platform.langgraph.com)
2. Navigujte na stránku "Settings" (Nastavení) v administračním rozhraní
3. Vyhledejte sekci "GitHub Integration" nebo "Source Control"

## Propojení GitHub repozitáře

### Krok 1: Autorizace LangGraph Platform

1. Klikněte na tlačítko "Connect to GitHub" nebo podobné
2. Budete přesměrováni na GitHub, kde budete muset autorizovat přístup pro LangGraph Platform
3. Vyberte repozitář `AI-agent-Ntier` ze seznamu dostupných repozitářů
4. Potvrďte výběr a udělte potřebná oprávnění

### Krok 2: Konfigurace webhooků

1. Po úspěšné autorizaci bude GitHub automaticky nastaven pro webhooky
2. Ověřte, že webhook byl správně nakonfigurován v nastavení GitHub repozitáře
   - Navigujte na GitHub repozitář > Settings > Webhooks
   - Měl by existovat webhook pro LangGraph Platform URL

### Krok 3: Nastavení proměnných prostředí

1. V administraci LangGraph Platform přejděte do sekce "Environment Variables"
2. Nastavte následující proměnné prostředí:
   - `OPENAI_API_KEY`: Váš OpenAI API klíč
   - `LANGSMITH_API_KEY`: Váš LangSmith API klíč
   - `LANGSMITH_PROJECT`: "AI-agent-Ntier" nebo jiný název projektu
3. Uložte nastavení

## Konfigurace automatického nasazení

### Krok 1: Nastavení branch pro deployment

1. V sekci "Deployment Settings" vyberte větev `main` jako zdroj pro nasazení
2. Volitelně můžete nastavit další větve pro staging prostředí

### Krok 2: Konfigurace build procesu

1. LangGraph Platform automaticky detekuje konfiguraci z `langgraph.json`
2. Není třeba žádná další konfigurace, pokud je `langgraph.json` správně nastaven
3. V případě potřeby můžete přidat specifické build příkazy do nastavení

## Testování integrace

1. Proveďte malou změnu v kódu a push do `main` větve
2. Sledujte log nasazení v administračním rozhraní LangGraph Platform
3. Ověřte, že aplikace byla úspěšně nasazena
4. Otestujte funkčnost aplikace pomocí dostupných API endpointů

## Řešení problémů

### Problémy s autorizací

- Ujistěte se, že máte správná oprávnění pro GitHub repozitář
- Zkuste odpojit a znovu připojit GitHub integraci

### Chyby při buildu

- Zkontrolujte build logy v administračním rozhraní
- Ujistěte se, že `langgraph.json` je správně nakonfigurován
- Ověřte, že všechny závislosti jsou správně definovány v `requirements.txt`

### Problémy s webhooky

- Zkontrolujte nastavení webhooků v GitHub repozitáři
- Ujistěte se, že webhooky jsou aktivní a mají správnou URL
- Zkontrolujte logy webhooků pro případné chyby

## Doporučené postupy

1. **Pravidelné kontroly**: Pravidelně kontrolujte stav integrace a logy nasazení
2. **Testovací větev**: Udržujte testovací větev pro ověření změn před deploymentem do produkce
3. **Monitoring**: Nastavte monitoring nasazené aplikace pro včasnou detekci problémů
4. **Zálohování**: Pravidelně zálohujte konfiguraci a data aplikace

---

**DŮLEŽITÉ**: Nikdy neukládejte citlivé informace jako API klíče přímo do GitHub repozitáře. Vždy používejte proměnné prostředí v administraci LangGraph Platform.

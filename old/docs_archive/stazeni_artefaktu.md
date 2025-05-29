# Instrukce pro stažení artefaktu z GitHub Actions

Aby bylo možné dokončit nasazení, je potřeba nejprve stáhnout artefakt `langgraph-package.tar.gz` z GitHub Actions. Následující kroky vás provedou procesem:

## 1. Přístup k GitHub Actions workflow

1. Otevřete webový prohlížeč a přejděte na GitHub repositář:
   ```
   https://github.com/minarovic/AI-agent-PoC3
   ```

2. Klikněte na záložku "Actions" v horní části stránky

3. V seznamu workflow běhů najděte nejnovější úspěšný běh odpovídající commitu "Fix: Přidání chybějící závislosti langchain_community" (měl by mít zelené zatržítko)

4. Klikněte na tento workflow běh pro zobrazení detailů

## 2. Stažení artefaktu

1. Na stránce detailu workflow běhu přejděte dolů do sekce "Artifacts"

2. Klikněte na "langgraph-package" pro stažení artefaktu

3. Soubor bude stažen jako `langgraph-package.zip` (nebo `.tar.gz`) do vašeho adresáře Downloads

## 3. Příprava artefaktu

Po stažení artefaktu pokračujte podle manuálu pro nasazení:

```bash
# Přejděte do pracovního adresáře
cd ~/langgraph-deploy

# Rozbalte stažený artefakt (upravte název souboru podle skutečného formátu)
# Pro .zip:
unzip ~/Downloads/langgraph-package.zip -d ./
# Pro .tar.gz:
tar -xzvf ~/Downloads/langgraph-package.tar.gz

# Ověřte obsah
ls -la artifacts/
```

## 4. Další postup

Po rozbalení artefaktu pokračujte podle sekce "2. Nasazení přes LangGraph Platform UI" v dokumentu `manual_artifact_deployment.md`.

**Poznámka:** Artefakt musí být úspěšně vygenerován v GitHub Actions workflow, aby mohl být stažen. Pokud není k dispozici, zkontrolujte, zda workflow proběhl úspěšně bez chyb.

# Nasazení konkrétního commitu c7a25bb na LangGraph Platform

Tento dokument popisuje proces nasazení specifického commitu c7a25bb na LangGraph Platform.

## Důvod nasazení commitu c7a25bb

Commit c7a25bb obsahuje optimalizované workflow s podporou typů analýz, které požadujeme nasadit na LangGraph Platform. Tento konkrétní commit je stabilní verzí a je určen pro produkční nasazení.

## Postup pomocí skriptu set_commit_c7a25bb.sh

Pro snadné nasazení tohoto konkrétního commitu byl vytvořen speciální skript, který automatizuje celý proces:

1. **Spusťte skript pro nastavení commitu:**
   ```bash
   ./set_commit_c7a25bb.sh
   ```

2. **Skript provede následující operace:**
   - Zkontroluje existenci commitu c7a25bb
   - Vytvoří novou větev production-c7a25bb z tohoto commitu
   - Ověří, že jste na správném commitu
   - Zobrazí seznam produkčních souborů, které budou nahrány
   - Nabídne možnost ihned provést force push na GitHub

3. **Potvrďte force push do hlavní větve:**
   Když skript zobrazí výzvu, odpovězte "y" pro okamžité nahrání na GitHub, nebo "n" pro ruční provedení později

4. **Sledujte stav nasazení na LangGraph Platform**

## Ruční postup (pokud nechcete použít skript)

Pokud preferujete ruční postup, můžete provést tyto kroky:

1. **Přepněte na commit c7a25bb a vytvořte novou větev:**
   ```bash
   git checkout c7a25bb
   git checkout -b production-c7a25bb
   ```

2. **Ověřte, že jste na správném commitu:**
   ```bash
   git rev-parse --short HEAD  # Měl by zobrazit c7a25bb
   ```

3. **Proveďte force push do hlavní větve:**
   ```bash
   git push -f origin production-c7a25bb:main
   ```

4. **Sledujte stav nasazení na LangGraph Platform**

## Po nasazení

Po úspěšném nasazení commitu c7a25bb na LangGraph Platform se můžete vrátit k vaší běžné vývojové větvi:

```bash
git checkout main  # nebo jiná vývojová větev
```

## Opětovné nasazení v budoucnosti

Pokud budete v budoucnu potřebovat znovu nasadit tento konkrétní commit, stačí přepnout na větev `production-c7a25bb` (pokud existuje) a provést force push:

```bash
git checkout production-c7a25bb
git push -f origin production-c7a25bb:main
```

Nebo můžete znovu spustit skript `set_commit_c7a25bb.sh`.

## Důležité upozornění

Použití `force push` přepíše historii hlavní větve na GitHubu. Provádějte tuto operaci pouze tehdy, když jste si jisti, že je to potřeba.

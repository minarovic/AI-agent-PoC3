# Návrat ke commitu 154cb5d

Pro rychlý návrat k commitu 154cb5d můžete použít vytvořený skript:

```bash
./vraceni_commitu_154cb5d.sh
```

Nebo můžete použít přímo Git příkazy:

## Varianta 1: Jednoduchý checkout (detached HEAD)
```bash
# Uloží případné neuložené změny
git diff > zmeny-$(date +%Y%m%d-%H%M%S).patch

# Přepne na commit 154cb5d
git checkout 154cb5d
```

## Varianta 2: Vytvoření nové větve z commitu 154cb5d
```bash
# Vytvoří novou větev z commitu 154cb5d
git checkout -b vetev-z-154cb5d 154cb5d
```

## Varianta 3: Vytvoření nového commitu, který vrátí stav na 154cb5d
```bash
# Vytvoří nový commit, který vrátí stav na 154cb5d
git revert --no-commit c7a25bb..HEAD
git commit -m "Návrat ke stavu commitu 154cb5d"
```

## Varianta 4: Hard reset (POZOR: Přepíše historii!)
```bash
# POZOR: Následující příkaz smaže všechny commity po 154cb5d!
# Použijte pouze pokud jste si jisti, že tyto commity nechcete zachovat
git reset --hard 154cb5d
```

Po provedení návratu ke commitu 154cb5d se nacházíte v odpojeném stavu HEAD. Pokud budete chtít pokračovat v práci, vytvořte novou větev:
```bash
git checkout -b nova-vetev
```

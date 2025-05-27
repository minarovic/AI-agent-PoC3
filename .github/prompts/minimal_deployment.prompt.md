# Minimální nasazení na LangGraph Platform

## Instrukce pro Copilot

### STOP - Než začneš cokoliv dělat
1. Přečti `deploy_logs/current_status.md`
2. Zkontroluj, co je již hotovo
3. Dělej POUZE další krok v seznamu

### Aktuální krok
Podívej se do `current_status.md` na sekci "Aktuální úkoly" a dělej pouze první nehotový úkol.

### Pravidla
1. **Jedna změna = jeden commit**
2. **Žádné testování během vývoje**
3. **Žádné extra funkce**
4. **Po commitu STOP a čekej na instrukce**

### Workflow
1. Implementuj minimální změnu
2. Commit a push
3. Čekej na výsledky GitHub Actions
4. Pokud selhalo - oprav POUZE tu chybu
5. Pokud prošlo - čekej na další instrukci

### Příklad postupu
```bash
# 1. Oprav jednu věc
vim langgraph.json

# 2. Commit
git add langgraph.json
git commit -m "Fix graph reference in langgraph.json"
git push origin deployment-fix

# 3. STOP - čekej na výsledky
```
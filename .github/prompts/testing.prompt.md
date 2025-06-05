
# AI-agent-Ntier: Testovací strategie

## 🎯 JEDINÝ CÍL TESTOVÁNÍ
**Identifikovat a opravit pouze BLOKUJÍCÍ CHYBY pro nasazení na LangGraph Platform**

## 🚨 KRITICKÉ POUČENÍ Z PRAXE
1. **GitHub Actions ≠ LangGraph Platform**
   - GitHub Actions testují SYNTAX a IMPORT
   - LangGraph Platform testuje RUNTIME BEHAVIOR
   - String syntax `"openai:gpt-4"` projde syntax check, ale může selhat při runtime

2. **API klíče a testování**
   - Mock klíče (`sk-mock-key-for-testing`) OpenAI knihovna detekuje a odmítá
   - Používej GitHub Secrets pro SKUTEČNÉ API klíče v CI/CD
   - Kontroluj formát klíčů (prefix: `sk-`, `sk-ant-`, `ls-`)

3. **Dependencies a instalace**
   - setup.py MUSÍ existovat pro `pip install -e .`
   - requirements-dev.txt MUSÍ existovat pokud je v workflow
   - String syntax NENÍ náhrada za dependencies

## ✅ TESTOVACÍ WORKFLOW
```
1. Přečti poslední chybový log
2. Identifikuj TYPE chyby: Syntax/Import vs Runtime
3. Zkontroluj zda je BLOKUJÍCÍ pro deployment
4. Oprav JEN blokující chyby, ignoruj test failures
5. Commit a sleduj GitHub Actions
```

## 🧰 ŘEŠENÍ ČASTÝCH CHYB

### ModuleNotFoundError
- **Typ:** Import error, BLOKUJÍCÍ
- **Příčina:** Chybějící balíček v requirements.txt NEBO nepoužívaný import
- **Řešení:** Přidat do requirements.txt NEBO odstranit import
- **Pattern Recognition:** Iterace 21, 30, 67

### "No such file or directory"
- **Typ:** File not found, BLOKUJÍCÍ  
- **Příčina:** Workflow očekává soubor, který neexistuje
- **Řešení:** Vytvořit minimální verzi souboru (setup.py, requirements-dev.txt)
- **Pattern Recognition:** Iterace 70, 71

### OPENAI_API_KEY errors
- **Typ:** Runtime error, NON-BLOKUJÍCÍ
- **Příčina:** OpenAI library odmítá mock klíče
- **Řešení:** Nastavit skutečné API klíče v GitHub Secrets a ignorovat test failures
- **Pattern Recognition:** Iterace 68

### ImportError: Unable to import langchain_openai
- **Typ:** Runtime error, BLOKUJÍCÍ
- **Příčina:** Chybějící langchain-openai v requirements.txt 
- **Řešení:** Přidat `langchain-openai>=0.3.18` do requirements.txt
- **Pattern Recognition:** Iterace 67

## 🔍 DIAGNOSTIKA
Použij speciální test script pro validaci API klíčů:
```python
import os
import sys

def validate_api_keys():
    """Validate critical API keys for LangGraph Platform."""
    critical_keys = {
        "OPENAI_API_KEY": {"required": True, "prefix": "sk-"},
        "ANTHROPIC_API_KEY": {"required": True, "prefix": "sk-ant-"},
        "LANGSMITH_API_KEY": {"required": False, "prefix": "ls-"},
    }

    all_critical_valid = True
    
    print("🚨 CRITICAL KEYS (required for deployment):")
    for key, config in critical_keys.items():
        if not config["required"]:
            continue
            
        value = os.environ.get(key, "")
        prefix_ok = value.startswith(config["prefix"])
        
        if value and prefix_ok:
            print(f"✅ {key}: PROPERLY SET (prefix: {config['prefix']})")
        elif value and not prefix_ok:
            print(f"❌ {key}: WRONG FORMAT (expected prefix: {config['prefix']})")
            all_critical_valid = False
        else:
            print(f"❌ {key}: NOT SET")
            all_critical_valid = False
    
    # Final results
    if all_critical_valid:
        print("\n✅ ALL CRITICAL API KEYS ARE PROPERLY CONFIGURED!")
        print("🚀 Ready for LangGraph Platform deployment!")
        return 0
    else:
        print("\n❌ SOME CRITICAL API KEYS ARE MISSING OR MISCONFIGURED")
        print("⚠️ Deployment will likely fail")
        return 1

if __name__ == "__main__":
    sys.exit(validate_api_keys())
```

## ❌ ANTI-PATTERNS v TESTOVÁNÍ
- **NEMĚNIT kód podle selhávajících testů** - testy jsou podřízené produkčnímu kódu
- **NEIGNOROVAT blokující chyby** - ModuleNotFoundError = opravit, test failures = ignorovat
- **NEMAZAT důležité dokumentační soubory** - Používat .gitignore místo mazání
- **NESIMULOVAT dependency-free řešení** - String syntax stále potřebuje dependencies
- **NETVRDIT, že oprava funguje bez důkazu** - počkat na GitHub Actions report

## 📊 PRIORITIZACE TESTOVÁNÍ
1. **NEJVYŠŠÍ: Deploy blocking** - Chyby blokující GitHub Actions workflow
2. **STŘEDNÍ: Validation errors** - Import/syntax chyby v produkčním kódu
3. **NÍZKÁ: Test failures** - Selhávající unit testy
4. **IGNOROVAT: Code style** - Lint warnings, style issues

## 📋 TESTOVACÍ CHECKLIST
- [ ] requirements.txt obsahuje všechny produkční závislosti?
- [ ] requirements-dev.txt existuje pro development dependencies?
- [ ] setup.py existuje a je minimální?
- [ ] langgraph.json používá Python import syntax?
- [ ] GitHub Secrets obsahují správné API klíče?
- [ ] Jsou odstraněny všechny nepoužívané importy?

## 🔄 TESTOVACÍ CYKLUS
```
1. PŘEČTI předchozí iterace
2. IDENTIFIKUJ typ chyby (syntax/runtime)
3. OPRAV pouze blokující chyby
4. COMMIT a PUSH
5. ČEKEJ na GitHub Actions
6. ZHODNOŤ výsledky
7. ZAPIŠ lesson learned
```
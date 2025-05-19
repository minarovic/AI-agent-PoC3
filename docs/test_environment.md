# Test Environment Setup Guide

## Nastavení testovacího prostředí pro AI-agent-Ntier

### Rychlé nastavení

Pro automatické nastavení testovacího prostředí použijte připravený skript:

```bash
chmod +x setup_test_env.sh
./setup_test_env.sh
```

Skript zajistí:
- Kontrolu verze Pythonu
- Vytvoření virtuálního prostředí
- Instalaci všech závislostí
- Vytvoření `.env` souboru z šablony

### Manuální nastavení

1. **Vytvoření virtuálního prostředí:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Pro Linux/macOS
   venv\Scripts\activate     # Pro Windows
   ```

2. **Instalace závislostí:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Pro vývojáře a testování
   ```

3. **Konfigurace prostředí:**
   ```bash
   cp .env.example .env
   # Upravte .env soubor a doplňte vlastní API klíče
   ```

### Spuštění testů

Pro spuštění všech testů:
```bash
pytest
```

Pro spuštění specifického testu:
```bash
pytest test_analyzer_direct.py
```

S pokrytím kódu:
```bash
pytest --cov=src
```

### Docker prostředí

Pro vývojové a testovací prostředí v Dockeru:
```bash
docker-compose -f docker-compose.dev.yml up test
```

Pro spuštění aplikace v Dockeru:
```bash
docker-compose -f docker-compose.dev.yml up app
```

### Typy testovacích módů

V `.env` souboru můžete nastavit různé typy testovacích módů:
- `TEST_MODE=mock` - Používá mockované API odpovědi (výchozí)
- `TEST_MODE=live` - Volá skutečná API (vyžaduje platné API klíče)
- `TEST_MODE=hybrid` - Kombinuje obojí podle typu testu

### Kontinuální integrace

Projekt obsahuje konfiguraci pro GitHub Actions, která automaticky spouští testy při každém push nebo PR. Viz `.github/workflows/test.yml`.

#!/usr/bin/env bash

# Skript pro verifikaci a testování opravy checkpointů
# Postupně otestuje všechny součásti řešení

set -e

echo "============================================="
echo "Verifikace opravy problému s checkpointy"
echo "============================================="

# 1. Spuštění testovacího skriptu checkpoint_fix.py
echo -e "\n--- Spouštím test opravy checkpointů ---"
echo "Test ověří, zda byl problém s MockMCPConnector vyřešen"
python test_checkpoint_fix.py

if [ $? -eq 0 ]; then
    echo "✅ Test opravy checkpointů úspěšný!"
else
    echo "❌ Test opravy checkpointů selhal!"
    exit 1
fi

# 2. Kontrola používání thread_id v testovacích souborech
echo -e "\n--- Kontroluji používání thread_id v testovacích souborech ---"
python verify_thread_id_usage.py test_*.py

# 3. Spuštění původního testu checkpointů
echo -e "\n--- Spouštím původní test checkpointů ---"
echo "Test ověří, zda byla zachována základní funkčnost checkpointů"
python test_checkpoints.py

if [ $? -eq 0 ]; then
    echo "✅ Původní test checkpointů úspěšný!"
else
    echo "❌ Původní test checkpointů selhal!"
    echo "⚠️ Zkontrolujte, zda nebyla poškozena základní funkcionalita"
    exit 1
fi

echo -e "\n============================================="
echo "✅ Všechny testy úspěšně dokončeny!"
echo "Oprava problému s checkpointy byla úspěšná."
echo "============================================="

#!/bin/bash
# Skrypt testowy - uruchamia dwóch klientów jednocześnie

echo "=== Test z dwoma klientami ==="
echo "Uruchamiam klienta 1 (Polska) i klienta 2 (Niemcy) równocześnie..."
echo ""

python3 klient.py Polska &
PID1=$!

python3 klient.py Niemcy &
PID2=$!

# Czekaj na zakończenie obu klientów
wait $PID1
wait $PID2

echo ""
echo "=== Test zakończony ==="


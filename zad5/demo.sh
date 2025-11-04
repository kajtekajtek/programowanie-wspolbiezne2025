#!/bin/bash
# Skrypt demonstracyjny - pokazuje jak uruchomić kompletny test

echo "==================================================================="
echo "  DEMO - System IPC z serwerem geograficznym"
echo "==================================================================="
echo ""
echo "Ten skrypt pokaże Ci jak uruchomić kompletny test systemu."
echo ""
echo "UWAGA: Ten skrypt zakłada, że będziesz uruchamiać polecenia ręcznie."
echo ""
echo "==================================================================="
echo "KROK 1: Sprawdzanie wymagań"
echo "==================================================================="
echo ""

# Sprawdź czy moduł sysv_ipc jest zainstalowany
if python3 -c "import sysv_ipc" 2>/dev/null; then
    echo "✓ Moduł sysv_ipc jest zainstalowany"
else
    echo "✗ Moduł sysv_ipc NIE jest zainstalowany"
    echo ""
    echo "Zainstaluj go poleceniem:"
    echo "  pip install sysv_ipc"
    echo ""
    exit 1
fi

echo ""
echo "==================================================================="
echo "KROK 2: Instrukcje uruchomienia"
echo "==================================================================="
echo ""
echo "Aby przetestować system, wykonaj następujące kroki:"
echo ""
echo "1. W PIERWSZYM TERMINALU uruchom serwer:"
echo "   $ python3 serwer.py"
echo ""
echo "2. W DRUGIM TERMINALU uruchom klienta:"
echo "   $ python3 klient.py Polska"
echo ""
echo "3. Aby przetestować równoczesną pracę dwóch klientów:"
echo "   $ python3 klient.py Polska & python3 klient.py Niemcy & wait"
echo "   LUB:"
echo "   $ bash test.sh"
echo ""
echo "4. Aby zatrzymać serwer (w TRZECIM TERMINALU):"
echo "   $ python3 stop_serwer.py"
echo "   LUB naciśnij Ctrl+C w terminalu z serwerem"
echo ""
echo "==================================================================="
echo "KROK 3: Dostępne kraje"
echo "==================================================================="
echo ""
echo "Serwer zna stolice następujących krajów:"
echo "  - Polska, Niemcy, Francja, Wielka Brytania, Hiszpania"
echo "  - Włochy, Portugalia, Czechy, Austria, Węgry"
echo "  - Grecja, Norwegia, Szwecja, Dania, Finlandia"
echo ""
echo "Dla nieznanych krajów odpowiada 'Nie wiem'"
echo ""
echo "==================================================================="
echo ""
echo "Czy chcesz uruchomić automatyczny test (wymaga 3 terminali)? (t/n)"
read -r odpowiedz

if [[ "$odpowiedz" == "t" || "$odpowiedz" == "T" ]]; then
    echo ""
    echo "Niestety automatyczny test wymaga użycia tmux lub screen."
    echo "Uruchom serwer i klientów ręcznie zgodnie z instrukcjami powyżej."
    echo ""
else
    echo ""
    echo "OK. Uruchom serwer i klientów ręcznie zgodnie z instrukcjami."
    echo ""
fi


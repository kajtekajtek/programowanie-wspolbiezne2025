# Zadanie 5 - Kolejki komunikatów IPC

Implementacja serwera geograficznego i klientów wykorzystujących kolejki komunikatów IPC (System V).

## Wymagania

Zainstaluj moduł `sysv_ipc`:

```bash
pip install sysv_ipc
```

## Pliki

- `serwer.py` - serwer poradnika geograficznego
- `klient.py` - klient wysyłający zapytania
- `stop_serwer.py` - specjalny klient do zatrzymania serwera
- `test.sh` - skrypt testowy uruchamiający 2 klientów jednocześnie

## Jak uruchomić

### 1. Uruchom serwer (w osobnym terminalu):

```bash
python3 serwer.py
```

Serwer utworzy dwie kolejki IPC (wejściową i wyjściową) i będzie czekał na zapytania.

### 2. Uruchom klienta (w innym terminalu):

```bash
python3 klient.py Polska
```

Klient wyśle 15 zapytań o stolicę Polski w odstępach 1 sekundowych, a następnie odbierze wszystkie odpowiedzi.

### 3. Test z dwoma klientami jednocześnie:

```bash
python3 klient.py Polska &
python3 klient.py Niemcy &
wait
```

Lub użyj skryptu testowego:

```bash
bash test.sh
```

### 4. Zatrzymanie serwera:

#### Sposób 1: Polecenie STOP
```bash
python3 stop_serwer.py
```

#### Sposób 2: Sygnał SIGINT (Ctrl+C)
W terminalu z serwerem naciśnij `Ctrl+C`

#### Sposób 3: Sygnał SIGTERM
```bash
pkill -TERM -f serwer.py
```

Wszystkie sposoby powodują prawidłowe usunięcie kolejek IPC.

## Dostępne kraje

Serwer zna stolice następujących krajów (wielkość liter nie ma znaczenia):
- Polska
- Niemcy
- Francja
- Wielka Brytania
- Hiszpania
- Włochy
- Portugalia
- Czechy
- Austria
- Węgry
- Grecja
- Norwegia
- Szwecja
- Dania
- Finlandia

Dla nieznanych krajów serwer odpowiada "Nie wiem".

## Jak to działa

1. **Serwer**:
   - Tworzy dwie kolejki IPC (klucze: 1234, 5678)
   - Odbiera zapytania z kolejki wejściowej (dowolnego typu)
   - Czeka 2 sekundy przed odpowiedzią (symulacja przetwarzania)
   - Wysyła odpowiedź do kolejki wyjściowej z PID klienta jako typem komunikatu
   - Obsługuje polecenie "stop" i sygnały (SIGINT, SIGTERM)
   - Usuwa kolejki przed zakończeniem

2. **Klient**:
   - Używa swojego PID jako typu komunikatu
   - Wysyła 15 zapytań w odstępach 1 sekundowych
   - Następnie odbiera wszystkie 15 odpowiedzi
   - Dzięki użyciu PID jako typu, każdy klient odbiera tylko swoje odpowiedzi

3. **Test obciążeniowy**:
   - Uruchomienie 2 klientów jednocześnie powoduje przeplatanie się zapytań w kolejce
   - Opóźnienie 2s w serwerze powoduje gromadzenie się wielu zapytań
   - Mimo to każdy klient otrzymuje swoje odpowiedzi dzięki mechanizmowi typów komunikatów

## Czyszczenie ręczne (w razie problemów)

Jeśli kolejki nie zostały usunięte, możesz je usunąć ręcznie:

```bash
# Wyświetl istniejące kolejki
ipcs -q

# Usuń kolejki po ID
ipcrm -q <id_kolejki>
```

## Struktura komunikacji

```
         Kolejka wejściowa (1234)
              ↓
    [Klient 1] → [Serwer] → [Klient 1]
    [Klient 2] → [Serwer] → [Klient 2]
              ↑
         Kolejka wyjściowa (5678)
```

- Klienci wysyłają do wspólnej kolejki wejściowej z własnym PID jako typem
- Serwer odbiera komunikaty dowolnego typu (type=0)
- Serwer wysyła odpowiedzi do wspólnej kolejki wyjściowej z PID klienta jako typem
- Klienci odbierają tylko komunikaty ze swoim PID (type=pid)


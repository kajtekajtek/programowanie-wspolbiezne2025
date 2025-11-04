# Instrukcja uruchomienia i testowania - Zadanie 5

## Przygotowanie środowiska

### 1. Instalacja wymaganych pakietów

```bash
pip install sysv_ipc
```

lub:

```bash
pip install -r requirements.txt
```

### 2. Weryfikacja instalacji

```bash
python3 -c "import sysv_ipc; print('OK')"
```

## Scenariusz testowy

### Terminal 1: Uruchomienie serwera

```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad5
python3 serwer.py
```

Powinieneś zobaczyć:
```
[SERWER] Uruchamiam serwer (PID: XXXXX)
[SERWER] Kolejka wejściowa utworzona (klucz: 1234)
[SERWER] Kolejka wyjściowa utworzona (klucz: 5678)
[SERWER] Czekam na zapytania (wyślij 'stop' aby zakończyć)...
[SERWER] Lub użyj Ctrl+C do zakończenia
```

### Terminal 2: Test z jednym klientem

```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad5
python3 klient.py Polska
```

Oczekiwany wynik:
- Klient wyśle 15 zapytań w odstępach 1 sekundy
- Następnie odbierze 15 odpowiedzi "Warszawa"

### Terminal 2: Test z dwoma klientami równocześnie

```bash
python3 klient.py Polska & python3 klient.py Niemcy & wait
```

lub użyj przygotowanego skryptu:

```bash
bash test.sh
```

Oczekiwany wynik:
- Oba klienty wysyłają zapytania jednocześnie
- Zapytania przeplatają się w kolejce serwera
- Każdy klient otrzymuje tylko swoje odpowiedzi (dzięki PID jako typowi komunikatu)

### Terminal 3: Zatrzymanie serwera

#### Sposób 1: Polecenie STOP (zalecane)

```bash
python3 stop_serwer.py
```

#### Sposób 2: Ctrl+C w terminalu serwera

#### Sposób 3: Sygnał SIGTERM

```bash
pkill -TERM -f serwer.py
```

Wszystkie metody powodują prawidłowe usunięcie kolejek IPC.

## Weryfikacja działania

### Co powinieneś zaobserwować:

1. **W terminalu serwera:**
   - Komunikaty o otrzymaniu zapytań
   - Komunikaty o wysłaniu odpowiedzi
   - Każde zapytanie przetwarzane z opóźnieniem 2 sekund

2. **W terminalu klienta:**
   - 15 komunikatów o wysłaniu zapytania
   - 15 komunikatów z odpowiedziami

3. **Przy dwóch klientach równocześnie:**
   - Przeplatanie się komunikatów w serwerze
   - Każdy klient otrzymuje swoje odpowiedzi
   - Brak pomyłek w dostarczaniu odpowiedzi

### Przykładowy output klienta:

```
[KLIENT 12345] Uruchamiam klienta
[KLIENT 12345] Zapytanie: 'Polska'
[KLIENT 12345] Wysyłam 15 zapytań...

[KLIENT 12345] Wysłano zapytanie 1/15
[KLIENT 12345] Wysłano zapytanie 2/15
...
[KLIENT 12345] Wysłano zapytanie 15/15

[KLIENT 12345] Wszystkie zapytania wysłane. Czekam na odpowiedzi...

[KLIENT 12345] Odpowiedź 1/15: Polska -> Warszawa
[KLIENT 12345] Odpowiedź 2/15: Polska -> Warszawa
...
[KLIENT 12345] Odpowiedź 15/15: Polska -> Warszawa

[KLIENT 12345] Wszystkie odpowiedzi odebrane. Kończę.
```

## Testowanie różnych krajów

Serwer zna stolice 15 krajów:

```bash
# Kraje, które serwer zna:
python3 klient.py Polska       # → Warszawa
python3 klient.py Niemcy       # → Berlin
python3 klient.py Francja      # → Paryż
python3 klient.py Włochy       # → Rzym
python3 klient.py Hiszpania    # → Madryt

# Nieznany kraj:
python3 klient.py Australia    # → Nie wiem
```

Wielkość liter nie ma znaczenia (wszystko konwertowane do małych liter).

## Rozwiązywanie problemów

### Problem: "Kolejki już istnieją"

Jeśli serwer nie został prawidłowo zatrzymany:

```bash
# Wyświetl istniejące kolejki
ipcs -q

# Usuń kolejki ręcznie (zastąp ID rzeczywistym ID z ipcs)
ipcrm -q <id_kolejki_1>
ipcrm -q <id_kolejki_2>
```

### Problem: "Kolejki nie istnieją"

Uruchom najpierw serwer przed uruchomieniem klientów.

### Problem: Klient "zawiesza się"

Upewnij się, że serwer działa. Klient czeka na odpowiedzi od serwera.

## Architektura rozwiązania

### Kluczowe elementy implementacji:

1. **Dwie kolejki IPC:**
   - Kolejka wejściowa (klucz: 1234) - zapytania od klientów
   - Kolejka wyjściowa (klucz: 5678) - odpowiedzi od serwera

2. **Typ komunikatu = PID klienta:**
   - Pozwala na rozróżnienie odpowiedzi dla różnych klientów
   - Klient odbiera tylko komunikaty ze swoim PID

3. **Serwer:**
   - Odbiera komunikaty dowolnego typu (type=0)
   - Opóźnienie 2 sekundy przed odpowiedzią
   - Obsługa sygnałów i polecenia "stop"
   - Automatyczne czyszczenie kolejek

4. **Klient:**
   - 15 zapytań w odstępach 1 sekundy (faza wysyłania)
   - Odbieranie wszystkich 15 odpowiedzi (faza odbierania)
   - Umożliwia testowanie obciążenia serwera

## Punktacja zadania

✓ **Punkt 1 (8 punktów):** Dwie kolejki IPC, komunikacja klient-serwer, PID jako typ, test obciążeniowy

✓ **Punkt 2 (2 punkty):** Zatrzymanie serwera z usunięciem kolejek (polecenie "stop" + sygnały)

## Pliki w projekcie

- `serwer.py` - główny program serwera
- `klient.py` - program klienta
- `stop_serwer.py` - klient do zatrzymania serwera
- `test.sh` - skrypt testowy (2 klientów równocześnie)
- `demo.sh` - interaktywny skrypt demonstracyjny
- `requirements.txt` - zależności Python
- `README.md` - dokumentacja projektu
- `INSTRUKCJA.md` - ten plik


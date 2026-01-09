# Gra w Statki - Aplikacja Sieciowa

## Opis

Sieciowa gra w statki (Battleship) dla dwóch graczy z graficznym interfejsem użytkownika.
Aplikacja wykorzystuje architekturę klient-serwer z komunikacją przez gniazda TCP/IP.

## Wymagania

- Python 3.8+
- Tkinter (zazwyczaj wbudowane w Python)

## Uruchomienie

### 1. Uruchom serwer

```bash
cd zad11
python server.py
```

Opcjonalne parametry:
- `-H / --host` - adres nasłuchiwania (domyślnie: 0.0.0.0)
- `-p / --port` - port (domyślnie: 5000)

Przykład:
```bash
python server.py -H 192.168.1.100 -p 8080
```

### 2. Uruchom klientów (w osobnych terminalach)

```bash
python client.py
```

W interfejsie graficznym:
1. Wpisz adres serwera (np. `localhost` dla testów lokalnych)
2. Wpisz port (np. `5000`)
3. Kliknij "Połącz"

## Zasady gry

### Flota
Każdy gracz posiada:
- 4 jednomasztowce (1 pole)
- 3 dwumasztowce (2 pola)
- 2 trzymasztowce (3 pola)
- 1 czteromasztowiec (4 pola)

### Rozgrywka
1. Statki są rozmieszczane losowo na początku gry
2. Gracze strzelają naprzemiennie (przy trafieniu gracz kontynuuje)
3. Strzał oddaje się klikając na planszę strzałów
4. Wygrywa gracz, który pierwszy zatopi wszystkie statki przeciwnika

### Legenda planszy
- 🟦 Niebieski - woda (nieodkryte pole)
- 🚢 Stalowy - statek (widoczny tylko na własnej planszy)
- 💥 Czerwony - trafienie
- ⚫ Szary - pudło
- ☠️ Fioletowy - zatopiony statek

## Struktura projektu

```
zad11/
├── server.py      # Serwer gry
├── client.py      # Klient z GUI
├── protocol.py    # Protokół komunikacji
├── game_logic.py  # Logika gry
└── README.md      # Dokumentacja
```

## Architektura

### Komunikacja sieciowa
- Protokół: TCP/IP
- Format wiadomości: JSON z nagłówkiem długości (8 bajtów)
- Port domyślny: 5000

### Typy wiadomości
| Typ | Kierunek | Opis |
|-----|----------|------|
| CONNECT | C→S | Żądanie połączenia |
| CONNECTED | S→C | Potwierdzenie + ID gracza |
| GAME_START | S→C | Rozpoczęcie gry |
| SHOOT | C→S | Strzał gracza |
| SHOT_RESULT | S→C | Wynik strzału |
| OPPONENT_SHOT | S→C | Informacja o strzale przeciwnika |
| GAME_OVER | S→C | Koniec gry |
| PLAY_AGAIN | C→S | Żądanie rematchu |

### Synchronizacja
- Serwer zarządza stanem gry i koordynuje tury
- Każdy klient obsługiwany w osobnym wątku
- Blokada (lock) chroni dostęp do współdzielonego stanu gry
- Interfejs GUI działa w głównym wątku, komunikacja sieciowa w osobnym

## Obsługa błędów

- **Serwer niedostępny**: Komunikat o błędzie połączenia
- **Rozłączenie przeciwnika**: Powiadomienie i możliwość oczekiwania na nowego gracza
- **Strzał w zajęte pole**: Komunikat o błędzie, można strzelać ponownie
- **Zamknięcie okna**: Bezpieczne rozłączenie z serwerem

## Autor

Zadanie 11 - Programowanie Współbieżne 2025

# Zadanie 11

## Opis ogólny

Celem zadania jest zaimplementowanie gry sieciowej dla dwóch osób przy zachowaniu zasad programowania współbieżnego. Rozwiązanie musi umożliwiać rozgrywkę użytkownikom działającym na osobnych komputerach (lub w osobnych procesach na jednej maszynie z wykorzystaniem gniazd).

## 1. Zasady Gry (Specyfikacja Wariantu)

Gra polega na rywalizacji dwóch graczy na kwadratowych planszach o rozmiarze .

### Przygotowanie planszy

- **Widok:** Każdy gracz widzi dwie plansze: swoją (z własnymi statkami) oraz planszę strzałów (widok pola przeciwnika).
- **Rozmieszczenie statków:** Statki można ustawiać w pionie lub poziomie. Nie mogą się one stykać bokami ani rogami.
- **Flota:** Każdy gracz dysponuje następującymi jednostkami:

    - 4 x jednomasztowiec 
    - 3 x dwumasztowiec 
    - 2 x trzymasztowiec 
    - 1 x czteromasztowiec 

- **Ustawianie:** Generowanie losowych pozycji statków.

### Przebieg rozgrywki

- **Start:** Grę rozpoczyna losowo wybrany gracz, otrzymując stosowny komunikat.
- **Tura:** Gdy jeden gracz wykonuje ruch, drugi musi mieć zablokowaną możliwość wykonywania jakichkolwiek akcji.
- **Strzał:** Oddawany poprzez kliknięcie pola na planszy strzałów.
- **Aktualizacja:** Po strzale stan planszy musi zaktualizować się natychmiast u obu graczy (informacja o trafieniu/pudle).
- **Wygrana:** Wygrywa osoba, która jako pierwsza zatopi wszystkie statki przeciwnika. Gra kończy się komunikatem o wyniku i opcją ponownej rozgrywki.

## 2. Wymagania Techniczne i Komunikacja

Podstawą zadania jest samodzielna organizacja komunikacji sieciowej.

* **Mechanizm komunikacji:** Należy wykorzystać **gniazda (sockets)**.
* **Architektura:** Model serwer-klient.
* **Ograniczenia:** Nie wolno używać gotowych frameworków komunikacyjnych. Komunikacja powinna być zorganizowana samodzielnie.
* **Sieć:** Program powinien być gotowy do działania w sieci, choć testowanie może odbywać się lokalnie (localhost). Rozwiązania ograniczające się wyłącznie do mechanizmów wewnątrzmaszynowych (np. kolejki komunikatów systemu operacyjnego) będą oceniane niżej.

## 3. Kryteria Oceny

| Kryterium | Waga | Opis |
| --- | --- | --- |
| **Interfejs Graficzny (GUI)** | **25%** | Przejrzysta wizualizacja stanu gry. Można użyć uproszczonego interfejsu tekstowego, ale obniża to punktację w tej kategorii. |
| **Koordynacja procesów/wątków** | **50%** | Prawidłowa synchronizacja działań graczy, obsługa komunikacji sieciowej w tle, brak blokowania interfejsu. |
| **Logika i przebieg gry** | **25%** | Poprawna implementacja algorytmu gry, sprawdzanie warunków trafienia, zatopienia i końca gry. |

---

## 4. Dokumentacja (Plik PDF)

Do zadania należy dołączyć dokumentację zawierającą:

* Imię i nazwisko autora oraz pełne sformułowanie zadania (opis wariantu "Statki").
* Krótkie wyjaśnienie **schematu komunikacji** oraz struktury przesyłanych komunikatów (co zawierają pakiety danych).
* Krótki opis użytkowania programu wraz z wykazem obsługiwanych sytuacji błędnych.

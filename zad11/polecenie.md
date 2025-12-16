# Zadanie 11

## Opis zadania

Warianty zadania będą indywidualnie rozsyłane, inny wariant dla każdej osoby (na adres jaki jest w portalu edukacyjnym).

- Punktacja: 30 punktów. 
- Czas: do końca semestru 
- (Próg zaliczenia laboratorium jest na podstawie sumarycznej ilości punktów za wszystkie zadania, czyli zadanie 11 nie jest bardziej obowiązkowe niż inne zadania.) Przykład zadania https://inf.ug.edu.pl/~pmp/Z/Wspolb22/projektP23.pdf ale każda osoba dostanie swój wariant.

### Interfejs

Jak widać, zadanie obejmuje między innymi interfejs graficzny. Można zastąpić interfejs graficzny uproszczonym interfejsem tekstowym, a nawet zamiast pracochłonnej planszy graficznej przesyłać graczom tylko informacje tekstowe umożliwiające np. ręczne rysowanie stanu gry na kartce. Takie uproszczenia spowoduje jednak zmniejszenie punktacji z tej części zadania.

### Komunikacja

Podstawową sprawą jest zorganizowanie komunikacji. Powinna ona umożliwiać toczenie gry przez użytkowników działających na osobnych komputerach. To sugeruje komunikację za pomocą gniazd. Może być serwer gry i klienci-gracze obsługiwani przez niego, lub prościej, bezpośrednia komunikacja między graczami. Można przyjąć, że testujemy wszystko lokalnie (localhost), czyli wszystko jednak na jednej maszynie ale z wizją na uogólnienie do komunikacji przez sieć. Rozwiązania używające komunikacji ograniczonej do jednej maszyny (kolejki itp.) będą mniej punktowane. Można używać języków i bibliotek ułatwiających rozwiązanie, zwłaszcza stronę graficzną. Komunikacja powinna być jednak zorganizowana samodzielnie a nie przez użycie jakiegoś gotowego frameworka.

## Punktacja

- interfejs graficzny [25%], 
- prawidłowa koordynacja procesów/wątków [50%], 
- Poprawnie zaimplementowany przebieg gry (przestrzeganie wymagań gry) [25%] 

## Dokumentacja (w pliku pdf)

- imię i nazwisko autora/autorki i sformułowanie zadania (czyli to co w opisie przydzielonego wariantu) 
- krótkie wyjaśnienie schematu komunikacji, jaka jest zawartość przesyłanych komunikatów 
- krótki opis użytkowania programu (w tym wykaz ewentualnych sytuacji błędnych obsługiwanych przez program); 

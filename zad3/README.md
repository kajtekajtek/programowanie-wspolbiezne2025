# Zadanie 3 - Liczenie słów z dyrektywami \input

## Opis

Program w Pythonie, który liczy wystąpienia słowa w tekście rozproszonym po wielu plikach połączonych dyrektywami `\input{filename}`.

## Wymagania

Program spełnia następujące wymagania:
- Obsługuje dyrektywy `\input{filename}` występujące w plikach
- Dyrektywy mogą być zagnieżdżone (pliki włączane mogą zawierać kolejne dyrektywy)
- Każda dyrektywa `\input` jest przetwarzana w oddzielnym, rozgałęzionym procesie (`os.fork()`)
- Proces rodzicielski czeka na procesy potomne (`os.waitpid()`) dopiero po przejrzeniu całego swojego pliku
- Informacja o liczbie wystąpień słowa jest przekazywana przez kod wyjścia procesu (mechanizm exit-wait)
- Program nie tworzy tymczasowego pliku z całym tekstem, tylko przetwarza pliki w locie

## Użycie

```bash
python program.py <nazwa_pliku> <słowo>
```

### Parametry:
- `<nazwa_pliku>` - ścieżka do pliku z początkiem tekstu
- `<słowo>` - słowo do zliczenia (wyszukiwanie jest case-insensitive)

## Przykład

Dla przykładowych plików z wiersza "Lokomotywa" Tuwima:

```bash
python program.py plikA.txt "i"
```

Wynik:
```
Słowo 'i' wystąpiło 4 razy.
```

## Struktura przykładowych plików testowych

### Przykład 1: Lokomotywa (plikA.txt, plikB.txt, plikC.txt, plikD.txt)
Pliki zawierające fragmenty wiersza "Lokomotywa" Juliana Tuwima z zagnieżdżonymi dyrektywami `\input`.

### Przykład 2: Testy głębokiego zagnieżdżenia (test_main.txt, test_sub*.txt)
Pliki testowe demonstrujące wielopoziomowe zagnieżdżenie dyrektyw `\input`.

## Implementacja

Program wykorzystuje:
- `os.fork()` - do tworzenia procesów potomnych dla każdej dyrektywy `\input`
- `os.waitpid()` - do oczekiwania na zakończenie procesów potomnych
- `os._exit()` - do zakończenia procesów potomnych z kodem wyjścia zawierającym liczbę wystąpień
- `re.match()` - do wykrywania dyrektyw `\input{filename}`
- `re.findall()` - do ekstrakcji słów z tekstu

### Algorytm:
1. Proces czyta plik linia po linii
2. Dla każdej linii:
   - Jeśli to dyrektywa `\input{filename}` - tworzy proces potomny
   - Jeśli to zwykły tekst - liczy wystąpienia słowa
3. Po przejrzeniu całego pliku, proces oczekuje na wszystkie procesy potomne
4. Sumuje wyniki z procesów potomnych (z kodów wyjścia)
5. Zwraca łączną liczbę wystąpień

### Ograniczenia:
- Kody wyjścia procesów są ograniczone do zakresu 0-255, więc program używa `count % 256`
- Dyrektywy `\input` muszą występować jako osobne linie w tekście
- Program zakłada, że dyrektywy nie tworzą cykli

## Testy

Program został przetestowany z:
- Pojedynczymi dyrektywami `\input`
- Zagnieżdżonymi dyrektywami (3+ poziomy)
- Różnymi słowami i wielkościami liter
- Wielokrotnymi dyrektywami w jednym pliku


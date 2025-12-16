# Zadanie 10 - Liczby pierwsze Germain

## Opis

Program znajduje liczby pierwsze Germain w zadanym przedziale liczbowym. **Liczba pierwsza Germain** to taka liczba pierwsza `p`, że `2p+1` też jest liczbą pierwszą.

Program implementuje dwie wersje:
- **Sekwencyjną** - klasyczne przetwarzanie sekwencyjne
- **Równoległą** - wykorzystującą `multiprocessing.Pool` do równoległego przetwarzania

## Algorytm

1. **Tworzenie listy małych liczb pierwszych**: Najpierw tworzona jest lista liczb pierwszych mniejszych lub równych pierwiastkowi kwadratowemu z maksymalnej wartości do sprawdzenia (czyli `sqrt(2*r+1)`, gdzie `r` to prawy koniec przedziału).

2. **Znajdowanie liczb pierwszych w zakresie**: Wyszukiwane są liczby pierwsze w zadanym przedziale `[l, r]`, sprawdzając podzielność tylko przez liczby pierwsze wyznaczone w pierwszym kroku.

3. **Sprawdzanie warunku Germain**: Dla każdej znalezionej liczby pierwszej `p` sprawdzane jest, czy `2p+1` też jest liczbą pierwszą.

## Wersja równoległa

Wersja równoległa wykorzystuje `multiprocessing.Pool` do podziału zakresu `[l, r]` na chunki, które są przetwarzane równolegle przez różne procesy. Każdy proces:
- Znajduje liczby pierwsze w swoim zakresie
- Sprawdza warunek Germain dla znalezionych liczb
- Zwraca listę liczb pierwszych Germain ze swojego zakresu

Wyniki z wszystkich procesów są następnie łączone i sortowane.

## Użycie

```bash
python3 germain_primes.py
```

Program automatycznie:
1. Wykonuje test weryfikacyjny na małym zakresie `[2, 100]`
2. Przeprowadza testy wydajności na dużym zakresie `[1000000, 2000000]`
3. Porównuje wydajność wersji sekwencyjnej z wersjami równoległymi (2, 4, 8 procesów oraz automatyczna liczba procesów)

## Wyniki przykładowe

Na zakresie `[1000000, 2000000]`:

- **Sekwencyjnie**: ~1.89 sekund
- **2 procesy**: ~0.98 sekund (przyśpieszenie ~1.93x)
- **4 procesy**: ~0.50 sekund (przyśpieszenie ~3.75x)
- **8 procesów**: ~0.35 sekund (przyśpieszenie ~5.34x)
- **12 procesów**: ~0.30 sekund (przyśpieszenie ~6.27x)

## Implementacja

Program wykorzystuje:
- `multiprocessing.Pool` - do zarządzania pulą procesów
- `pool.map()` - do równoległego przetwarzania chunków zakresu
- Wspólną listę małych liczb pierwszych przekazywaną do każdego procesu (kopiowana przy forkowaniu)

## Przykłady liczb pierwszych Germain

W zakresie `[2, 100]`: `[2, 3, 5, 11, 23, 29, 41, 53, 83, 89]`

- `p = 2`: `2*2+1 = 5` ✓ (5 jest pierwsze)
- `p = 3`: `2*3+1 = 7` ✓ (7 jest pierwsze)
- `p = 5`: `2*5+1 = 11` ✓ (11 jest pierwsze)
- `p = 7`: `2*7+1 = 15` ✗ (15 nie jest pierwsze)


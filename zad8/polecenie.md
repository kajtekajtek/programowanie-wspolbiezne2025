# Zadanie 8.  

W bardzo dużej liście L znajduja się liczby całkowite z przedziału od 0 do N-1 (N jest nieduże np. N==20). Chcemy zbadać ilość wystąpień każdej liczby z zakresu 0,1,2, … N-1 w całej liście L, czyli utworzyć listę liczników licz o rozmiarze N. w której będzie tak, że

```
licz[i] == ilość wystąpień liczby i w liście L
```

Na przykład, jeżeli N==3 a lista L == [2,0,1,2,1,1,1] to

licz[0] == 1

licz[1] == 4

licz[2] == 2

Napisać wielowątkowy program, który tworzy taką listę liczników według poniższego schematu: 
- pozwala rozbić zadanie (iteracyjnie lub rekurencyjnie) na pewną ilość wątków, każdy obsługujący pewien fragment listy L. Ilość wątków ma być regulowana w programie. (punktacja: 10 punktów)

Uwaga1:  W przypadku równoczesnego operowaniu na wspólnych zmiennych przez wątki należy pamiętać o wzajemnym wykluczaniu poprzez użycie blokady (Lock), ale też należy zadbać o to, aby jak najmniejszy fragment obliczeń był wykonywany na zasadzie wzajemnego wykluczania.


# Zadanie 9.  
Sekwencyjny program `pierwsze.py` 

```Python
# wyszukanie liczb pierwszych z zakresu od l do r

l=2
r=20

def pierwsza(k):
# sprawdzenie, czy k jest pierwsza
 for i in range (2,k-1):
   if i*i>k:
     return True
   if k%i == 0:
     return False
 return True

pierwsze = []
for i in range (l,r+1):
  if pierwsza(i):
    pierwsze.append(i)

print(pierwsze)
```

tworzy listę  liczb pierwszych występujących w zadanym przedziale liczbowym. 

Napisać wielowątkowy  program realizujący to samo obliczenie czyli tworzący listę liczb pierwszych z zadanego przedziału. 
- Ilość tworzonych wątków powinna być regulowana w programie.
- Rozbicie na wątki współbieżne polega na tym, że przedział, w którym szukamy liczb pierwszych dzielimy na tyle podprzedziałów ile mamy wątków i każdy wątek obsługuje swój podprzedział. 
- Dodatkowe wymaganie techniczne: użyć bariery (Barrier) do zasygnalizowania przez wątki że już zakończyły swoje obliczenia (Wskazówka: przykład użycia bariery). 

```Python
# Przykład użycia bariery
import threading
import time

def f(arg,name,s,bar):
    for i in range(arg):
        print(name,'i=',i)
        time.sleep(s)
    print ("koniec pracy "+name)
    bar.wait()
    print ("koniec czekania "+name)

b = threading.Barrier(3)
t1 = threading.Thread(target = f, args = (5,'t1',1,b))
t2 = threading.Thread(target = f, args = (2,'t2',0.7,b))
t1.start()
t2.start()
print ("koniec pracy ")
b.wait()
# t1.join()
# t2.join()
print ("koniec czekania")
```

- Można by osiągnąć ten efekt używając funkcji join(), ale wypróbujmy inny mechanizm.
- Uwaga: pamiętać o wzajemnym wykluczaniu w przypadku operowaniu na wspólnych zmiennych przez wątki.

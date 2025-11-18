# Zadanie 6. 

## Zasady gry
Wykorzystując  mechanizmy IPC: pamięć współdzieloną i synchronizację procesów za pomocą semaforów, zaprogramować poniżej opisaną grę inspirowaną **grą w trzy karty**.

- Jest dwóch graczy uruchamiających swoje programy w osobnych oknach: Gracz 1 i Gracz 2. 
- Są dwa obszary pamięci współdzielonej PW1 i PW2.  
- Gracz 1 to ten, który włączył swój program jako pierwszy. 

Są 3 tury gry, każda tura przebiega następująco:
1. Gracz 1 ustala pozycję wygrywającej karty: 1, 2 lub 3 (wpisywane z klawiatury) i zapisuje ja do pamięci współdzielonej PW1.
2. Gracz 2 (nie znając wyboru Gracza 1)  próbuje odgadnąć pozycję wygrywającej karty czyli typuje jedną spośród pozycji: 1, 2, lub 3 (wpisywane z klawiatury) po czym zapisuje ja do pamięci współdzielonej PW2.
3. Gracz 1 odczytuje z pamięci PW2 wybór Gracza 2
4. Gracz 2 odczytuje z pamięci PW1  wybór Gracza 1. 
5. Jeżeli obydwaj gracze wybrali te same pozycje to wygrywa Gracz 2, jeżeli pozycje są różne to wygrywa Gracz 1. U każdego z graczy powinna pojawić się w jego oknie informacja, jakie pozycje zostały wybrane i czy dany Gracz wygrał, czy przegrał aktualną turę gry i jaki jest wynik sumaryczny. Po trzech opisanych wyżej turach gry gra się kończy (pamięci współdzielone i semafory powinny zostać usunięte).

- Synchronizacja procesów powinna zapewnić, że odczyty z pamięci współdzielonych (punkty 3 i 4) nastąpią dopiero po wcześniejszych zapisach (punkty 1 i 2). 
- Ponadto przejście do następnej tury, czyli ponowne wykonanie punktów 1 i 2 powinno nastąpić dopiero po zakończeniu punktów 3 i 4 z poprzedniej tury. To powinno być zapewnione przy wykorzystaniu semaforów, ale bez aktywnego czekania. (Można np. wymusić wykonanie punktów 1, 2, 3, 4 w tej właśnie kolejności, ale może są i bardziej elastyczne rozwiązania?)

Można się wzorować na sposobie synchronizacji dwóch komunikujących się programów  

- kom1.py
```Python
import sysv_ipc

klucz = 11
NULL_CHAR = '\0'

sem1 = sysv_ipc.Semaphore(klucz, sysv_ipc.IPC_CREX,0o700,0)
sem2 = sysv_ipc.Semaphore(klucz+1, sysv_ipc.IPC_CREX,0o700,1)
mem = sysv_ipc.SharedMemory(klucz, sysv_ipc.IPC_CREX)

def pisz(mem, s):
    s += NULL_CHAR
    s = s.encode()
    mem.write(s)

def czytaj(mem):
    s = mem.read()
    s = s.decode()
    i = s.find(NULL_CHAR)
    if i != -1:
        s = s[:i]
    return s

s = ''
pisz(mem,s)

for i in range(0, 3):
    print(s)
    sem1.acquire()
    s=czytaj(mem)
    s=s+'a'
    pisz(mem,s)
    sem2.release()

print(s)

sysv_ipc.remove_shared_memory(mem.id)
sysv_ipc.remove_semaphore(sem1.id)
sysv_ipc.remove_semaphore(sem2.id)
# moĹźna  alternatywnie mem.remove() i  sem1.remove() i sem2.remove() 
```

- kom2.py 
```Python
import sysv_ipc

klucz = 11
NULL_CHAR = '\0'

sem1 = sysv_ipc.Semaphore(klucz)
sem2 = sysv_ipc.Semaphore(klucz+1)
mem = sysv_ipc.SharedMemory(klucz)

def pisz(mem, s):
    s += NULL_CHAR
    s = s.encode()
    mem.write(s)

def czytaj(mem):
    s = mem.read()
    s = s.decode()
    i = s.find(NULL_CHAR)
    if i != -1:
        s = s[:i]
    return s

s = ''

for i in range(0, 3):
    print(s)
    sem2.acquire()
    s=czytaj(mem)
    s=s+'b'
    pisz(mem,s)
    sem1.release()

print(s)
```

podanych jako przykłady z wykładu  

- Kolejnym wymaganiem jest, żeby  zrobić jeden (uniwersalny) program dla obu graczy - wstępną rywalizację o  bycie Graczem 1 wygrywa ten proces, który jako pierwszy utworzy któryś z semaforów albo pamięć współdzieloną. W programie wyscig.py  jest przykład ilustrujący jak to można zrobić przy użyciu flagi sysv_ipc.IPC_CREX.

```Python
import sysv_ipc
import time

klucz = 11

try:
    sem = sysv_ipc.Semaphore(klucz, sysv_ipc.IPC_CREX,0o700,1)
    # robiÄ tu inne rzeczy, ktĂłre ma zrobiÄ tylko proces ktĂłry wygraĹ wyscig
    pierwszy = True    
except sysv_ipc.ExistentialError:
    # drugi proces juĹź utworzyĹ semafor
    sem = sysv_ipc.Semaphore(klucz)
    pierwszy=False
    time.sleep(0.1)    
    # czekam chwilÄ, aĹź pierwszy proces skoĹczy to co ma zrobiÄ jako pierwszy

if pierwszy:
    print('jestem pierwszy')
    time.sleep(5)    
    sem.remove()
else:
    print('jestem drugi')
```

Wskazówki 
- IPC w Pythonie:   https://semanchuk.com/philip/sysv_ipc/
- materiały z wykładu: pamięć wspólna i semafory

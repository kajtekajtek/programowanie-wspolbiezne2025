# Zadanie 10

W tym zadaniu ważne są dwa elementy:
- zbadanie przyśpieszenia, jakie możemy uzyskać przez zrównoleglenie obliczeń - w Pythonie ze względu na GIL użyjemy wieloprocesowości (moduł multithreading) zamiast bardziej naturalnej wielowatkowosci 
- użycie narzędzi nieco automatyzujących zrównoleglanie obliczeń - w Pythonie będzie to pula procesów (multiprocessing.Pool) 

Punktem wyjścia jest sekwencyjny program `pierwszePlus.py` który
tworzy listę liczb pierwszych występujących w zadanym przedziale liczbowym. Program ten działa tak, że
- najpierw tworzy listę liczb pierwszych mniejszych lub równych pierwiastkowi kwadratowemu z prawego końca przedziału 
- następnie wyszukuje liczby pierwsze z zadanego przedziału sprawdzając podzielność tylko przez liczby pierwsze wyznaczone w pierwszym kroku 

Ten właśnie program jest punktem wyjścia do innego obliczenia: wyznaczyć listę liczb pierwszych Germain. 
- **Liczba pierwsza Germain** to taka liczba pierwsza p, że 2p+1 też jest licza pierwszą. 

Powyższe obliczenie mamy wykonać na dwa sposoby i porównać
uzyskane czasy na dużym przedziale liczbowym:
- zwyczajnie sekwencyjnie oraz
- z wykorzystaniem równoległości

W Pythonie można uzyskać przyśpieszenie nie przez wielowątkowe
obliczenie (ze względu na Global Interpreter Lock), ale przez
obliczenie wieloprocesowe wykorzystując moduł multiprocessing a w nim klasę Pool i funkcję imap (lub map lub starmap itp.), przy pomocy których możemy rozbić drugi krok obliczenia na kilka podzadań wykonywanych przez równoległe procesy. Należy wykonać pomiary czasu (na dużych danych) sprawdzające, czy uzyskano przyśpieszenie i dla jakiej ilości równoległych podzadań. Powinno pojawić się przyspieszenie.

Pewnym problemem do rozwiązania będzie wpisywanie na jedną
wspólną listę liczb pierwszych Germain uzyskanych w utworzonych
równoległych procesach. Można to zrobić na kilka sposobów:
- Można  wykorzystać fakt, że funkcje map, imap itd. klasy Pool mogą przekazać wynik w zwracanej wartości (to najprostsze rozwiazanie, chociaż niekoniecznie najefektywniejsze). 
- Można alternatywnie wykorzystać mechanizmy pamięci wspólnej modułu multiprocessing: 
	- najefektywniejsze czasowo będzie prawdopodobnie Array plus ewentualnie Value, 
	- ale można też spróbować użyć kolejek multiprocessing.Queue 
	- lub mechanizmu Manager. 
	- Użycie wspólnej pamięci multiprocessing.Array jest o tyle trudne, że trzeba z góry określić rozmiar tak tworzonej współdzielonej tablicy. Na szczęście znane jest ograniczenie na ilość liczb pierwszych w przedziale od 1 do x: jest ich nie więcej niż 6/5*x/(ln x) procesach   

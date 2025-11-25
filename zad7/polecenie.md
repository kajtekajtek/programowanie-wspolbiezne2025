# Zadanie 7.  

## Polecenie

Utworzyć aplikację typu klient-serwer opartą na komunikacji  przez gniazda datagramowe (UDP) w domenie internetowej . Aplikacja realizuje grę  papier kamień nożyce. Gra toczy się w rundach. Każdy gracz  dokonuje wyboru (papier, kamień lub nożyce) i przez swojego klienta wysyła swój wybór do  serwera. Serwer ustala wynik kto wygrał i przesyła klientowi każdego z graczy informację o wyborze drugiego gracza. 

Dokładniejsza specyfikacja jest następująca. Jest dwóch graczy i serwer. Gracz działa tak, że w pętli przesyła swój wybór i czeka na odpowiedź serwera, którą uzyska, gdy drugi gracz też prześle do serwera swój wybór. Każdy gracz zlicza swoje punkty z kolejnych rund i wyświetla je w swoim oknie po każdej rundzie. Serwer w swoim oknie też wyświetla na bieżąco punkty obu graczy. Gdy któryś gracz chce skończyć grę, przesyła do serwera informację "koniec" (czy jakiś inny komunikat końca) jako swój wybór i jego klient przestaje działać. Serwer po odebraniu wiadomości "koniec" od któregoś z graczy kończy rozgrywkę tych graczy (informując ich o tym), zeruje punktację i przechodzi do stanu początkowego, czekając na zgłoszenia nowej pary graczy. Uwaga, są tu 3 możliwości zakończenia rozgrywki:

- obydwaj gracze przysyłają wiadomość "koniec"
- jeden z graczy przysyła jako pierwszy wiadomość "koniec", a drugi potem przysyła swój wybór papier, kamień lub nożyce
- jeden z graczy przysyła jako pierwszy swój wybór papier, kamień lub nożyce, a drugi potem przysyła wiadomość "koniec"

Serwer i klienci graczy działają lokalnie, czyli na IP 127.0.0.1. Wymieniają komunikaty tekstowe  lub liczbowe (np. jednoliterowe lub jednocyfrowe  oznaczenia wyborów graczy). Numer portu serwera jest ustalony i znany graczom. Numery portów graczy są automatycznie tworzone w czasie tworzenia ich klientów i zapamiętywane przez serwer, który po nich rozróżnia graczy.  Gracze mogą dokonywać wyborów w różnej kolejności, ale w kolejnych rundach numery ich portów są takie same.

## Przykłady

```Python
# serwer UDP, odbiera napis, odsyĹa ten napis na wielkich literach
import socket

IP     = "127.0.0.1"
port   = 5001
bufSize  = 1024

# utworzenie gniazda UDP
UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# zwiÄzanie gniazda z IP i portem
UDPServerSocket.bind((IP, port))

print("serwer UDP dziaĹa")

# obsĹuga nadchodzÄcych datagramĂłw
while(True):
    komB,adres = UDPServerSocket.recvfrom(bufSize)
    print(komB)
    print(adres)
    # wysyĹanie odpowiedzi
    kom=komB.decode()
    odpB=kom.upper().encode()
    UDPServerSocket.sendto(odpB, adres)
```

```Python
# klient UDP, dwukrotmie  wysyĹa napis i odbiera napis 

import socket

komA = "aaaaa"
komAB = str.encode(komA)
serwerAdresPort   = ("127.0.0.1", 5001)
klientAdresPort   = ("127.0.0.1", 5002)
bufSize = 1024
# tworzy gniazdo UDP po stronie klienta
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# zwiÄzuje gniazdo z parÄ adres, port - moĹźna pominÄÄ
# UDPClientSocket.bind(klientAdresPort)

# wysyĹa do serwera przez utworzone gniazdo
UDPClientSocket.sendto(komAB, serwerAdresPort)
odp = UDPClientSocket.recvfrom(bufSize)
print(odp)
UDPClientSocket.sendto("bbb".encode(), serwerAdresPort)
odp = UDPClientSocket.recvfrom(bufSize)
print(odp)
```

```Python
# serwer UDP, odbiera int, odsyĹa wartoĹÄ zwiÄkszonÄ o 100

import socket
import struct

IP     = "127.0.0.1"
port   = 5001
bufSize  = 1024

# utworzenie gniazda UDP
UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# zwiÄzanie gniazda z IP i portem
UDPServerSocket.bind((IP, port))

print("serwer UDP dziaĹa")

# obsĹuga nadchodzÄcych datagramĂłw
while(True):
    komNP,adres = UDPServerSocket.recvfrom(bufSize)
    kom=struct.unpack('!i',komNP)
    print(kom)
    print(adres)
    # wysyĹanie odpowiedzi
    odpNP = struct.pack('!i',kom[0]+100)
    UDPServerSocket.sendto(odpNP, adres)
```

```Python
# klient UDP, dwukrotmie wysyĹa i odbiera int

import socket
import struct

komA = 1
komANP = struct.pack('!i',komA)

serwerAdresPort   = ("127.0.0.1", 5001)
klientAdresPort   = ("127.0.0.1", 5002)
bufSize = 1024
# tworzy gniazdo UDP po stronie klienta
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# zwiÄzuje gniazdo z parÄ adres, port - moĹźna pominÄÄ
#UDPClientSocket.bind(klientAdresPort)

# wysyĹa do serwera przez utworzone gniazdo
UDPClientSocket.sendto(komANP, serwerAdresPort)
odpNP = UDPClientSocket.recvfrom(bufSize)
odp = struct.unpack('!i',odpNP[0])
print(odp)
UDPClientSocket.sendto(struct.pack('!i',2), serwerAdresPort)
odpNP = UDPClientSocket.recvfrom(bufSize)
print(struct.unpack('!i',odpNP[0]))
```
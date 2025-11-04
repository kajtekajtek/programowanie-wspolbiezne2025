#!/usr/bin/env python3
import sysv_ipc
import os
import sys
import time

KLUCZ_WEJSCIE = 1234
KLUCZ_WYJSCIE = 5678

LICZBA_ZAPYTAN = 15
OPOZNIENIE_WYSLANIA = 1

def main():
    if len(sys.argv) < 2:
        print("Użycie: python3 klient.py <nazwa_kraju>")
        print("Przykład: python3 klient.py Polska")
        sys.exit(1)
    
    kraj = sys.argv[1]
    pid = os.getpid()
    
    print(f"[KLIENT {pid}] Uruchamiam klienta")
    print(f"[KLIENT {pid}] Zapytanie: '{kraj}'")
    print(f"[KLIENT {pid}] Wysyłam {LICZBA_ZAPYTAN} zapytań...\n")
    
    try:
        kolejka_wejsciowa = sysv_ipc.MessageQueue(KLUCZ_WEJSCIE)
        kolejka_wyjsciowa = sysv_ipc.MessageQueue(KLUCZ_WYJSCIE)
        
    except sysv_ipc.ExistentialError:
        print(f"[KLIENT {pid}] BŁĄD: Kolejki nie istnieją. Uruchom najpierw serwer.")
        sys.exit(1)
    except Exception as e:
        print(f"[KLIENT {pid}] BŁĄD przy otwieraniu kolejek: {e}")
        sys.exit(1)
    
    try:
        for i in range(1, LICZBA_ZAPYTAN + 1):
            kolejka_wejsciowa.send(kraj.encode('utf-8'), type=pid)
            print(f"[KLIENT {pid}] Wysłano zapytanie {i}/{LICZBA_ZAPYTAN}")
            
            if i < LICZBA_ZAPYTAN:
                time.sleep(OPOZNIENIE_WYSLANIA)
        
        print(f"\n[KLIENT {pid}] Wszystkie zapytania wysłane. Czekam na odpowiedzi...\n")
        
    except Exception as e:
        print(f"[KLIENT {pid}] BŁĄD przy wysyłaniu: {e}")
        sys.exit(1)
    
    try:
        for i in range(1, LICZBA_ZAPYTAN + 1):
            message, msg_type = kolejka_wyjsciowa.receive(type=pid)
            odpowiedz = message.decode('utf-8')
            
            print(f"[KLIENT {pid}] Odpowiedź {i}/{LICZBA_ZAPYTAN}: {kraj} -> {odpowiedz}")
        
        print(f"\n[KLIENT {pid}] Wszystkie odpowiedzi odebrane. Kończę.\n")
        
    except Exception as e:
        print(f"[KLIENT {pid}] BŁĄD przy odbieraniu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


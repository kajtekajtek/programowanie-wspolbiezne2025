#!/usr/bin/env python3
import sysv_ipc
import os
import sys

KLUCZ_WEJSCIE = 1234

def main():
    pid = os.getpid()
    
    print(f"[STOP_KLIENT {pid}] Wysyłam polecenie STOP do serwera...")
    
    try:
        kolejka_wejsciowa = sysv_ipc.MessageQueue(KLUCZ_WEJSCIE)
        
        kolejka_wejsciowa.send("stop".encode('utf-8'), type=pid)
        
        print(f"[STOP_KLIENT {pid}] Polecenie STOP wysłane.")
        print(f"[STOP_KLIENT {pid}] Serwer powinien się zamknąć i usunąć kolejki.")
        
    except sysv_ipc.ExistentialError:
        print(f"[STOP_KLIENT {pid}] BŁĄD: Kolejka nie istnieje. Serwer prawdopodobnie nie działa.")
        sys.exit(1)
    except Exception as e:
        print(f"[STOP_KLIENT {pid}] BŁĄD: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import sysv_ipc
import signal
import sys
import time
import os

KLUCZ_WEJSCIE = 1234
KLUCZ_WYJSCIE = 5678

STOLICE = {
    "polska": "Warszawa",
    "niemcy": "Berlin",
    "francja": "Paryż",
    "wielka brytania": "Londyn",
    "hiszpania": "Madryt",
    "włochy": "Rzym",
    "portugalia": "Lizbona",
    "czechy": "Praga",
    "austria": "Wiedeń",
    "węgry": "Budapeszt",
    "grecja": "Ateny",
    "norwegia": "Oslo",
    "szwecja": "Sztokholm",
    "dania": "Kopenhaga",
    "finlandia": "Helsinki",
}

kolejka_wejsciowa = None
kolejka_wyjsciowa = None

def cleanup():
    print("\n[SERWER] Usuwam kolejki i kończę działanie...")
    try:
        if kolejka_wejsciowa:
            kolejka_wejsciowa.remove()
            print("[SERWER] Kolejka wejściowa usunięta")
    except Exception as e:
        print(f"[SERWER] Błąd przy usuwaniu kolejki wejściowej: {e}")
    
    try:
        if kolejka_wyjsciowa:
            kolejka_wyjsciowa.remove()
            print("[SERWER] Kolejka wyjściowa usunięta")
    except Exception as e:
        print(f"[SERWER] Błąd przy usuwaniu kolejki wyjściowej: {e}")

def signal_handler(signum, frame):
    """Obsługa sygnałów (SIGINT, SIGTERM)"""
    print(f"\n[SERWER] Otrzymano sygnał {signum}")
    cleanup()
    sys.exit(0)

def main():
    global kolejka_wejsciowa, kolejka_wyjsciowa
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"[SERWER] Uruchamiam serwer (PID: {os.getpid()})")
    
    try:
        kolejka_wejsciowa = sysv_ipc.MessageQueue(
            KLUCZ_WEJSCIE, 
            sysv_ipc.IPC_CREAT,
            mode=0o666
        )
        print(f"[SERWER] Kolejka wejściowa utworzona (klucz: {KLUCZ_WEJSCIE})")
        
        kolejka_wyjsciowa = sysv_ipc.MessageQueue(
            KLUCZ_WYJSCIE,
            sysv_ipc.IPC_CREAT,
            mode=0o666
        )
        print(f"[SERWER] Kolejka wyjściowa utworzona (klucz: {KLUCZ_WYJSCIE})")
        
    except sysv_ipc.ExistentialError:
        print("[SERWER] BŁĄD: Kolejki już istnieją. Usuń je poleceniem 'ipcrm -q'")
        sys.exit(1)
    except Exception as e:
        print(f"[SERWER] BŁĄD przy tworzeniu kolejek: {e}")
        sys.exit(1)
    
    print("[SERWER] Czekam na zapytania (wyślij 'stop' aby zakończyć)...")
    print("[SERWER] Lub użyj Ctrl+C do zakończenia\n")
    
    try:
        while True:
            message, msg_type = kolejka_wejsciowa.receive(type=0)
            zapytanie = message.decode('utf-8').strip()
            
            print(f"[SERWER] Otrzymano zapytanie: '{zapytanie}' od procesu {msg_type}")
            
            if zapytanie.lower() == "stop":
                print("[SERWER] Otrzymano polecenie STOP")
                cleanup()
                sys.exit(0)
            
            time.sleep(2)
            
            kraj = zapytanie.lower()
            odpowiedz = STOLICE.get(kraj, "Nie wiem")
            
            print(f"[SERWER] Wysyłam odpowiedź: '{odpowiedz}' do procesu {msg_type}")
            
            kolejka_wyjsciowa.send(odpowiedz.encode('utf-8'), type=msg_type)
            
    except KeyboardInterrupt:
        print("\n[SERWER] Przerwano przez użytkownika")
        cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"[SERWER] BŁĄD: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()


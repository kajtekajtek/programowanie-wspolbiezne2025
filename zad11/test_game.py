#!/usr/bin/env python3
"""
Test automatyczny gry w statki.
Symuluje dwóch klientów bez GUI.
"""

import socket
import threading
import time
import sys

from protocol import (
    Message, MessageType, ShotResult,
    send_message, receive_message, BOARD_SIZE
)
from game_logic import CellState, Board, Game


def test_game_logic():
    """Testuje logikę gry."""
    print("=" * 50)
    print("TEST: Logika gry")
    print("=" * 50)
    
    # Test generowania planszy
    board = Board()
    assert board.generate_random_ships(), "Generowanie statków powinno się udać"
    
    # Policz statki
    ship_cells = sum(1 for row in board.grid for cell in row if cell == CellState.SHIP)
    expected_cells = 4*1 + 3*2 + 2*3 + 1*4  # 4+6+6+4 = 20
    assert ship_cells == expected_cells, f"Nieprawidłowa liczba pól statków: {ship_cells} != {expected_cells}"
    
    print(f"✓ Wygenerowano planszę z {ship_cells} polami statków")
    print(f"✓ Liczba statków: {len(board.ships)}")
    
    # Test strzałów
    hits = 0
    misses = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            result, sunk = board.receive_shot(row, col)
            if result == CellState.HIT:
                hits += 1
            else:
                misses += 1
    
    assert hits == expected_cells, f"Nieprawidłowa liczba trafień: {hits}"
    assert board.all_ships_sunk(), "Wszystkie statki powinny być zatopione"
    print(f"✓ Trafienia: {hits}, Pudła: {misses}")
    print(f"✓ Wszystkie statki zatopione: {board.all_ships_sunk()}")
    
    print("\n✓ Test logiki gry PASSED\n")
    return True


def test_protocol():
    """Testuje protokół komunikacji."""
    print("=" * 50)
    print("TEST: Protokół komunikacji")
    print("=" * 50)
    
    # Test serializacji wiadomości
    msg = Message(MessageType.SHOOT, {"row": 5, "col": 3})
    json_str = msg.to_json()
    decoded = Message.from_json(json_str)
    
    assert decoded.type == MessageType.SHOOT
    assert decoded.data["row"] == 5
    assert decoded.data["col"] == 3
    
    print(f"✓ Serializacja wiadomości: {msg.type.value}")
    print(f"✓ JSON: {json_str}")
    print(f"✓ Dekodowanie poprawne")
    
    print("\n✓ Test protokołu PASSED\n")
    return True


def test_server_connection(host='localhost', port=5000):
    """Testuje połączenie z serwerem."""
    print("=" * 50)
    print("TEST: Połączenie z serwerem")
    print("=" * 50)
    
    try:
        # Połącz pierwszego gracza
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.settimeout(5)
        sock1.connect((host, port))
        print(f"✓ Gracz 1 połączony z {host}:{port}")
        
        # Odbierz potwierdzenie połączenia
        msg1 = receive_message(sock1)
        assert msg1 is not None, "Brak odpowiedzi od serwera"
        assert msg1.type == MessageType.CONNECTED, f"Nieprawidłowy typ wiadomości: {msg1.type}"
        player1_id = msg1.data["player_id"]
        print(f"✓ Gracz 1 otrzymał ID: {player1_id}")
        
        # Połącz drugiego gracza
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.settimeout(5)
        sock2.connect((host, port))
        print(f"✓ Gracz 2 połączony z {host}:{port}")
        
        # Odbierz potwierdzenie dla gracza 2
        msg2 = receive_message(sock2)
        assert msg2 is not None, "Brak odpowiedzi od serwera"
        assert msg2.type == MessageType.CONNECTED, f"Nieprawidłowy typ wiadomości: {msg2.type}"
        player2_id = msg2.data["player_id"]
        print(f"✓ Gracz 2 otrzymał ID: {player2_id}")
        
        # Poczekaj na rozpoczęcie gry
        time.sleep(0.5)
        
        # Odbierz wiadomość o rozpoczęciu gry
        game_msg1 = receive_message(sock1)
        game_msg2 = receive_message(sock2)
        
        assert game_msg1 is not None and game_msg1.type == MessageType.GAME_START
        assert game_msg2 is not None and game_msg2.type == MessageType.GAME_START
        print(f"✓ Gra rozpoczęta!")
        
        # Sprawdź kto zaczyna
        if game_msg1.data["your_turn"]:
            print(f"✓ Gracz 1 zaczyna")
            current_sock = sock1
            waiting_sock = sock2
        else:
            print(f"✓ Gracz 2 zaczyna")
            current_sock = sock2
            waiting_sock = sock1
        
        # Wykonaj strzał
        print("\n--- Symulacja rozgrywki ---")
        send_message(current_sock, Message(MessageType.SHOOT, {"row": 0, "col": 0}))
        
        # Odbierz wynik
        result = receive_message(current_sock)
        assert result is not None, "Brak wyniku strzału"
        assert result.type == MessageType.SHOT_RESULT
        print(f"✓ Strzał w A1: {result.data['result']}")
        
        # Odbierz informację u przeciwnika
        opponent_msg = receive_message(waiting_sock)
        assert opponent_msg is not None
        assert opponent_msg.type == MessageType.OPPONENT_SHOT
        print(f"✓ Przeciwnik otrzymał informację o strzale")
        
        # Test wielu strzałów - sprawdź zmianę tury przy pudle
        print("\n--- Test zmiany tur ---")
        
        # Jeśli był to pudło, tura powinna się zmienić
        if result.data['result'] == 'miss':
            print("✓ Pudło - tura przechodzi do przeciwnika")
            # Teraz przeciwnik powinien strzelać
            send_message(waiting_sock, Message(MessageType.SHOOT, {"row": 1, "col": 1}))
            result2 = receive_message(waiting_sock)
            assert result2 is not None and result2.type == MessageType.SHOT_RESULT
            print(f"✓ Przeciwnik strzelił w B2: {result2.data['result']}")
        else:
            print("✓ Trafienie - gracz kontynuuje")
            # Gracz kontynuuje
            send_message(current_sock, Message(MessageType.SHOOT, {"row": 0, "col": 1}))
            result2 = receive_message(current_sock)
            assert result2 is not None and result2.type == MessageType.SHOT_RESULT
            print(f"✓ Kolejny strzał w B1: {result2.data['result']}")
        
        # Zamknij połączenia
        sock1.close()
        sock2.close()
        
        print("\n✓ Test połączenia z serwerem PASSED\n")
        return True
        
    except socket.timeout:
        print("✗ Timeout - serwer nie odpowiada")
        return False
    except ConnectionRefusedError:
        print("✗ Serwer nie działa na podanym porcie")
        return False
    except Exception as e:
        print(f"✗ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 50)
    print("    TESTY AUTOMATYCZNE GRY W STATKI")
    print("=" * 50 + "\n")
    
    results = []
    
    # Test logiki
    results.append(("Logika gry", test_game_logic()))
    
    # Test protokołu
    results.append(("Protokół", test_protocol()))
    
    # Test serwera (jeśli działa)
    results.append(("Serwer", test_server_connection()))
    
    # Podsumowanie
    print("=" * 50)
    print("PODSUMOWANIE")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("WSZYSTKIE TESTY PASSED ✓")
    else:
        print("NIEKTÓRE TESTY FAILED ✗")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Serwer gry w statki.
Obsługuje połączenia dwóch klientów i koordynuje rozgrywkę.
"""

import socket
import threading
import sys
import signal
from typing import Dict, Optional

from protocol import (
    Message, MessageType, ShotResult, 
    send_message, receive_message, BOARD_SIZE
)
from game_logic import Game, GameState, CellState


class BattleshipServer:
    """Serwer gry w statki."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.game = Game()
        self.running = False
        self.lock = threading.Lock()
        self.client_threads: Dict[int, threading.Thread] = {}
        
    def start(self):
        """Uruchamia serwer."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)
            self.running = True
            
            print(f"╔══════════════════════════════════════════╗")
            print(f"║    SERWER GRY W STATKI                   ║")
            print(f"╠══════════════════════════════════════════╣")
            print(f"║  Adres: {self.host}:{self.port}".ljust(43) + "║")
            print(f"║  Oczekiwanie na graczy...                ║")
            print(f"╚══════════════════════════════════════════╝")
            
            self._accept_connections()
            
        except OSError as e:
            print(f"[BŁĄD] Nie można uruchomić serwera: {e}")
            sys.exit(1)
    
    def _accept_connections(self):
        """Akceptuje połączenia od klientów."""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, address = self.server_socket.accept()
                except socket.timeout:
                    continue
                
                print(f"[INFO] Nowe połączenie z {address}")
                
                with self.lock:
                    if self.game.is_full():
                        send_message(client_socket, Message(
                            MessageType.ERROR,
                            {"message": "Gra jest pełna"}
                        ))
                        client_socket.close()
                        continue
                    
                    # Dodaj gracza do gry
                    player_id = self.game.add_player(client_socket, f"Gracz {address}")
                    
                    if player_id is None:
                        send_message(client_socket, Message(
                            MessageType.ERROR,
                            {"message": "Nie można dołączyć do gry"}
                        ))
                        client_socket.close()
                        continue
                    
                    # Wyślij potwierdzenie połączenia
                    send_message(client_socket, Message(
                        MessageType.CONNECTED,
                        {
                            "player_id": player_id,
                            "board_size": BOARD_SIZE,
                            "your_board": self.game.players[player_id].board.to_dict()
                        }
                    ))
                    
                    print(f"[INFO] Gracz {player_id} dołączył ({address})")
                    
                    # Uruchom wątek obsługi klienta
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, player_id),
                        daemon=True
                    )
                    self.client_threads[player_id] = thread
                    thread.start()
                    
                    # Sprawdź czy można rozpocząć grę
                    if self.game.is_full():
                        self._start_game()
                
            except Exception as e:
                if self.running:
                    print(f"[BŁĄD] Błąd akceptacji połączenia: {e}")
    
    def _start_game(self):
        """Rozpoczyna grę."""
        self.game.start_game()
        
        current_id = self.game.current_player_idx
        opponent_id = 1 - current_id
        
        print(f"[INFO] Gra rozpoczęta! Zaczyna Gracz {current_id}")
        
        # Powiadom obu graczy
        for player_id in range(2):
            player = self.game.players[player_id]
            if player and player.socket:
                is_your_turn = (player_id == current_id)
                
                send_message(player.socket, Message(
                    MessageType.GAME_START,
                    {
                        "your_turn": is_your_turn,
                        "your_board": player.board.to_dict(),
                        "opponent_board": self.game.get_opponent(player_id).board.to_dict(hide_ships=True)
                    }
                ))
    
    def _handle_client(self, client_socket: socket.socket, player_id: int):
        """Obsługuje komunikację z pojedynczym klientem."""
        try:
            while self.running:
                msg = receive_message(client_socket)
                
                if msg is None:
                    break
                
                self._process_message(player_id, msg)
                
        except Exception as e:
            print(f"[BŁĄD] Błąd obsługi gracza {player_id}: {e}")
        finally:
            self._handle_disconnect(player_id)
    
    def _process_message(self, player_id: int, msg: Message):
        """Przetwarza wiadomość od klienta."""
        with self.lock:
            if msg.type == MessageType.SHOOT:
                self._handle_shot(player_id, msg.data)
            
            elif msg.type == MessageType.PLAY_AGAIN:
                self._handle_play_again(player_id)
            
            elif msg.type == MessageType.DISCONNECT:
                self._handle_disconnect(player_id)
    
    def _handle_shot(self, player_id: int, data: dict):
        """Obsługuje strzał gracza."""
        row = data.get("row")
        col = data.get("col")
        
        if row is None or col is None:
            return
        
        result = self.game.process_shot(player_id, row, col)
        
        if "error" in result:
            player = self.game.players[player_id]
            if player and player.socket:
                send_message(player.socket, Message(
                    MessageType.ERROR,
                    {"message": result["error"]}
                ))
            return
        
        # Określ wynik strzału
        if result["result"] == "HIT":
            shot_result = ShotResult.SUNK.value if result["sunk"] else ShotResult.HIT.value
        else:
            shot_result = ShotResult.MISS.value
        
        # Powiadom strzelającego o wyniku
        player = self.game.players[player_id]
        if player and player.socket:
            response_data = {
                "row": row,
                "col": col,
                "result": shot_result,
                "your_turn": not result["game_over"] and result["result"] == "HIT",
                "game_over": result["game_over"],
                "you_won": result["winner"] == player_id if result["game_over"] else None
            }
            
            if result["sunk"] and result["sunk_cells"]:
                response_data["sunk_cells"] = result["sunk_cells"]
            
            send_message(player.socket, Message(MessageType.SHOT_RESULT, response_data))
        
        # Powiadom przeciwnika o strzale
        opponent = self.game.get_opponent(player_id)
        if opponent and opponent.socket:
            opponent_data = {
                "row": row,
                "col": col,
                "result": shot_result,
                "your_turn": not result["game_over"] and result["result"] != "HIT",
                "game_over": result["game_over"],
                "you_won": result["winner"] == opponent.id if result["game_over"] else None
            }
            
            if result["sunk"] and result["sunk_cells"]:
                opponent_data["sunk_cells"] = result["sunk_cells"]
            
            send_message(opponent.socket, Message(MessageType.OPPONENT_SHOT, opponent_data))
        
        if result["game_over"]:
            winner_name = f"Gracz {result['winner']}"
            print(f"[INFO] Koniec gry! Wygrał {winner_name}")
    
    def _handle_play_again(self, player_id: int):
        """Obsługuje żądanie ponownej gry."""
        player = self.game.players[player_id]
        if player:
            player.wants_rematch = True
            print(f"[INFO] Gracz {player_id} chce zagrać ponownie")
            
            # Sprawdź czy obaj gracze chcą grać
            if all(p and p.wants_rematch for p in self.game.players):
                print("[INFO] Obu gracze chcą rematchu. Resetowanie gry...")
                self.game.reset_for_rematch()
                self._start_game()
            else:
                # Powiadom gracza że czeka na przeciwnika
                send_message(player.socket, Message(
                    MessageType.WAITING,
                    {"message": "Oczekiwanie na decyzję przeciwnika..."}
                ))
    
    def _handle_disconnect(self, player_id: int):
        """Obsługuje rozłączenie gracza."""
        player = self.game.players[player_id]
        
        if player and player.socket:
            try:
                player.socket.close()
            except:
                pass
        
        self.game.remove_player(player_id)
        print(f"[INFO] Gracz {player_id} rozłączony")
        
        # Powiadom przeciwnika
        opponent = self.game.get_opponent(player_id)
        if opponent and opponent.socket:
            send_message(opponent.socket, Message(
                MessageType.OPPONENT_DISCONNECTED,
                {"message": "Przeciwnik opuścił grę"}
            ))
        
        # Reset gry
        self.game.state = GameState.WAITING
    
    def stop(self):
        """Zatrzymuje serwer."""
        print("\n[INFO] Zamykanie serwera...")
        self.running = False
        
        # Zamknij wszystkie połączenia klientów
        for player in self.game.players:
            if player and player.socket:
                try:
                    send_message(player.socket, Message(
                        MessageType.DISCONNECT,
                        {"message": "Serwer został zamknięty"}
                    ))
                    player.socket.close()
                except:
                    pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[INFO] Serwer zatrzymany")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Serwer gry w statki')
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Adres nasłuchiwania (domyślnie: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port (domyślnie: 5000)')
    
    args = parser.parse_args()
    
    server = BattleshipServer(host=args.host, port=args.port)
    
    # Obsługa sygnałów
    def signal_handler(sig, frame):
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()

"""
Protokół komunikacji dla gry w statki.
Definiuje strukturę wiadomości przesyłanych między serwerem a klientami.
"""

import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple

BOARD_SIZE = 10
HEADER_SIZE = 8  # Nagłówek określający długość wiadomości

# (liczba_statków, rozmiar_statku)
FLEET = [
    (4, 1),
    (3, 2),
    (2, 3),
    (1, 4),
]

class MessageType(Enum):
    # Połączenie
    CONNECT = "connect"
    CONNECTED = "connected"
    WAITING = "waiting"
    
    # Rozpoczęcie gry
    GAME_START = "game_start"
    YOUR_TURN = "your_turn"
    WAIT_TURN = "wait_turn"
    
    # Rozgrywka
    SHOOT = "shoot"
    SHOT_RESULT = "shot_result"
    OPPONENT_SHOT = "opponent_shot"
    
    # Status statków
    SHIP_SUNK = "ship_sunk"
    
    # Koniec gry
    GAME_OVER = "game_over"
    PLAY_AGAIN = "play_again"
    RESTART = "restart"
    
    # Błędy i rozłączenie
    ERROR = "error"
    DISCONNECT = "disconnect"
    OPPONENT_DISCONNECTED = "opponent_disconnected"


class ShotResult(Enum):
    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"


@dataclass
class Message:
    type: MessageType
    data: Optional[dict] = None
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data or {}
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        obj = json.loads(json_str)
        return cls(
            type=MessageType(obj["type"]),
            data=obj.get("data", {})
        )


def encode_message(msg: Message) -> bytes:
    """Koduje wiadomość do wysłania przez socket."""
    json_data = msg.to_json().encode('utf-8')
    header = f"{len(json_data):<{HEADER_SIZE}}".encode('utf-8')
    return header + json_data


def decode_message(data: bytes) -> Message:
    """Dekoduje wiadomość otrzymaną z socketa."""
    return Message.from_json(data.decode('utf-8'))


def receive_message(sock) -> Optional[Message]:
    """Odbiera pełną wiadomość z socketa."""
    try:
        header = sock.recv(HEADER_SIZE)
        if not header:
            return None
        
        msg_len = int(header.decode('utf-8').strip())
        data = b''
        while len(data) < msg_len:
            chunk = sock.recv(min(msg_len - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        return decode_message(data)
    except Exception as e:
        return None


def send_message(sock, msg: Message) -> bool:
    """Wysyła wiadomość przez socket."""
    try:
        sock.sendall(encode_message(msg))
        return True
    except Exception as e:
        return False

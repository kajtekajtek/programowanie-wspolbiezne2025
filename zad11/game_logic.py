"""
Logika gry w statki.
Obsługa planszy, statków, strzałów i sprawdzania warunków wygranej.
"""

import random
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

from protocol import BOARD_SIZE, FLEET


class CellState(Enum):
    EMPTY = 0      # Puste pole
    SHIP = 1       # Statek
    MISS = 2       # Pudło
    HIT = 3        # Trafienie


@dataclass
class Ship:
    """Reprezentuje pojedynczy statek."""
    cells: List[Tuple[int, int]]  # Lista pozycji (row, col)
    hits: Set[Tuple[int, int]] = field(default_factory=set)
    
    @property
    def size(self) -> int:
        return len(self.cells)
    
    @property
    def is_sunk(self) -> bool:
        return len(self.hits) == len(self.cells)
    
    def hit(self, pos: Tuple[int, int]) -> bool:
        """Rejestruje trafienie. Zwraca True jeśli pozycja należy do statku."""
        if pos in self.cells:
            self.hits.add(pos)
            return True
        return False


class Board:
    """Reprezentuje planszę gracza."""
    
    def __init__(self):
        self.grid = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.ships: List[Ship] = []
        
    def can_place_ship(self, positions: List[Tuple[int, int]]) -> bool:
        """Sprawdza czy można umieścić statek w danych pozycjach."""
        for row, col in positions:
            # Sprawdź czy pozycja jest na planszy
            if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                return False
            
            # Sprawdź czy pole jest puste (nie można stawiać na istniejącym statku)
            if self.grid[row][col] == CellState.SHIP:
                return False
            
            # Sprawdź czy wszystkie sąsiednie pola są puste (statki nie mogą się stykać)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # Pomiń samo pole (już sprawdzone wyżej)
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        # Sąsiad może być statkiem tylko jeśli jest częścią tego samego statku
                        if self.grid[nr][nc] == CellState.SHIP and (nr, nc) not in positions:
                            return False
        return True
    
    def place_ship(self, positions: List[Tuple[int, int]]) -> bool:
        """Umieszcza statek na planszy."""
        if not self.can_place_ship(positions):
            return False
        
        ship = Ship(cells=positions)
        self.ships.append(ship)
        
        for row, col in positions:
            self.grid[row][col] = CellState.SHIP
        
        return True
    
    def generate_random_ships(self) -> bool:
        """Generuje losowe rozmieszczenie statków."""
        self.grid = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.ships = []
        
        for count, size in FLEET:
            for _ in range(count):
                placed = False
                attempts = 0
                max_attempts = 1000
                
                while not placed and attempts < max_attempts:
                    attempts += 1
                    
                    # Losowy kierunek (0 = poziomo, 1 = pionowo)
                    horizontal = random.choice([True, False])
                    
                    if horizontal:
                        row = random.randint(0, BOARD_SIZE - 1)
                        col = random.randint(0, BOARD_SIZE - size)
                        positions = [(row, col + i) for i in range(size)]
                    else:
                        row = random.randint(0, BOARD_SIZE - size)
                        col = random.randint(0, BOARD_SIZE - 1)
                        positions = [(row + i, col) for i in range(size)]
                    
                    if self.place_ship(positions):
                        placed = True
                
                if not placed:
                    return False
        
        return True
    
    def receive_shot(self, row: int, col: int) -> Tuple[CellState, Optional[Ship]]:
        """
        Przetwarza otrzymany strzał.
        Zwraca (stan_pola, zatopiony_statek lub None).
        """
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return CellState.EMPTY, None
        
        current = self.grid[row][col]
        
        if current == CellState.SHIP:
            self.grid[row][col] = CellState.HIT
            
            # Znajdź statek i zarejestruj trafienie
            for ship in self.ships:
                if ship.hit((row, col)):
                    if ship.is_sunk:
                        return CellState.HIT, ship
                    return CellState.HIT, None
        
        elif current == CellState.EMPTY:
            self.grid[row][col] = CellState.MISS
            return CellState.MISS, None
        
        # Już strzelano w to pole
        return current, None
    
    def all_ships_sunk(self) -> bool:
        """Sprawdza czy wszystkie statki zostały zatopione."""
        return all(ship.is_sunk for ship in self.ships)
    
    def to_dict(self, hide_ships: bool = False) -> dict:
        """Konwertuje planszę do słownika (do przesłania przez sieć)."""
        grid_data = []
        for row in range(BOARD_SIZE):
            row_data = []
            for col in range(BOARD_SIZE):
                state = self.grid[row][col]
                if hide_ships and state == CellState.SHIP:
                    row_data.append(CellState.EMPTY.value)
                else:
                    row_data.append(state.value)
            grid_data.append(row_data)
        
        return {"grid": grid_data}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Board':
        """Tworzy planszę ze słownika."""
        board = cls()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                board.grid[row][col] = CellState(data["grid"][row][col])
        return board


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Player:
    """Reprezentuje gracza w grze."""
    id: int
    name: str
    board: Board = field(default_factory=Board)
    socket: any = None
    ready: bool = False
    wants_rematch: bool = False


class Game:
    """Zarządza stanem całej gry."""
    
    def __init__(self):
        self.players: List[Optional[Player]] = [None, None]
        self.current_player_idx: int = 0
        self.state: GameState = GameState.WAITING
        self.winner: Optional[int] = None
    
    def add_player(self, socket, name: str) -> Optional[int]:
        """Dodaje gracza do gry. Zwraca ID gracza lub None."""
        for i in range(2):
            if self.players[i] is None:
                player = Player(id=i, name=name, socket=socket)
                player.board.generate_random_ships()
                self.players[i] = player
                return i
        return None
    
    def remove_player(self, player_id: int):
        """Usuwa gracza z gry."""
        if 0 <= player_id < 2:
            self.players[player_id] = None
    
    def is_full(self) -> bool:
        """Sprawdza czy gra jest pełna (2 graczy)."""
        return all(p is not None for p in self.players)
    
    def start_game(self):
        """Rozpoczyna grę."""
        if not self.is_full():
            return False
        
        self.state = GameState.PLAYING
        self.current_player_idx = random.randint(0, 1)
        self.winner = None
        return True
    
    def get_current_player(self) -> Optional[Player]:
        """Zwraca gracza, którego tura."""
        if self.state != GameState.PLAYING:
            return None
        return self.players[self.current_player_idx]
    
    def get_opponent(self, player_id: int) -> Optional[Player]:
        """Zwraca przeciwnika danego gracza."""
        opponent_id = 1 - player_id
        return self.players[opponent_id]
    
    def process_shot(self, shooter_id: int, row: int, col: int) -> dict:
        """
        Przetwarza strzał gracza.
        Zwraca słownik z wynikiem.
        """
        if self.state != GameState.PLAYING:
            return {"error": "Gra nie jest w toku"}
        
        if shooter_id != self.current_player_idx:
            return {"error": "Nie twoja tura"}
        
        opponent = self.get_opponent(shooter_id)
        if opponent is None:
            return {"error": "Brak przeciwnika"}
        
        result, sunk_ship = opponent.board.receive_shot(row, col)
        
        response = {
            "row": row,
            "col": col,
            "result": result.name,
            "sunk": sunk_ship is not None,
            "sunk_cells": sunk_ship.cells if sunk_ship else None,
            "game_over": False,
            "winner": None
        }
        
        # Sprawdź wygraną
        if opponent.board.all_ships_sunk():
            self.state = GameState.FINISHED
            self.winner = shooter_id
            response["game_over"] = True
            response["winner"] = shooter_id
        else:
            # Zmiana tury tylko przy pudle
            if result == CellState.MISS:
                self.current_player_idx = 1 - self.current_player_idx
        
        return response
    
    def reset_for_rematch(self):
        """Resetuje grę do stanu początkowego dla rematchu."""
        for player in self.players:
            if player:
                player.board = Board()
                player.board.generate_random_ships()
                player.wants_rematch = False
        
        self.state = GameState.WAITING
        self.winner = None
        self.current_player_idx = random.randint(0, 1)

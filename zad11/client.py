#!/usr/bin/env python3
"""
Klient gry w statki z graficznym interfejsem użytkownika.
"""

import socket
import threading
import tkinter as tk
from tkinter import messagebox, font
from typing import Optional, List, Tuple
import sys

from protocol import (
    Message, MessageType, ShotResult,
    send_message, receive_message, BOARD_SIZE
)
from game_logic import CellState


# Kolory dla interfejsu - ciemny motyw morski
COLORS = {
    'bg': '#0a1628',              # Tło główne - głęboki granat
    'bg_secondary': '#152238',     # Tło drugorzędne
    'water': '#1a3a5c',           # Woda - ciemny błękit
    'water_hover': '#2a5a8c',     # Woda po najechaniu
    'ship': '#4a6fa5',            # Statek - stalowo-niebieski
    'hit': '#c62828',             # Trafienie - czerwony
    'miss': '#37474f',            # Pudło - szary
    'sunk': '#7b1fa2',            # Zatopiony - fioletowy
    'text': '#e0e0e0',            # Tekst główny
    'text_secondary': '#90a4ae',   # Tekst drugorzędny
    'accent': '#00bcd4',          # Akcent - cyjan
    'success': '#4caf50',         # Sukces - zielony
    'warning': '#ff9800',         # Ostrzeżenie - pomarańczowy
    'grid': '#263850',            # Siatka
    'your_turn': '#1b5e20',       # Twoja tura
    'enemy_turn': '#b71c1c',      # Tura przeciwnika
}

CELL_SIZE = 38
BOARD_PADDING = 25


class BattleshipClient:
    """Klient gry w statki."""
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.player_id: Optional[int] = None
        self.connected = False
        self.my_turn = False
        self.game_active = False
        
        # Stan planszy
        self.my_board = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.enemy_board = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # GUI
        self.root: Optional[tk.Tk] = None
        self.my_board_canvas: Optional[tk.Canvas] = None
        self.enemy_board_canvas: Optional[tk.Canvas] = None
        self.status_label: Optional[tk.Label] = None
        self.turn_indicator: Optional[tk.Label] = None
        self.info_label: Optional[tk.Label] = None
        
        # Wątek odbierania
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False
        
    def create_gui(self):
        """Tworzy interfejs graficzny."""
        self.root = tk.Tk()
        self.root.title("⚓ Statki - Gra Sieciowa")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(False, False)
        
        # Czcionki
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.status_font = font.Font(family="Segoe UI", size=12)
        self.small_font = font.Font(family="Segoe UI", size=10)
        
        # Główny kontener
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="⚓ STATKI ⚓",
            font=self.title_font,
            fg=COLORS['accent'],
            bg=COLORS['bg']
        )
        title_label.pack()
        
        # Wskaźnik tury
        self.turn_indicator = tk.Label(
            title_frame,
            text="Oczekiwanie na połączenie...",
            font=self.header_font,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg'],
            pady=5
        )
        self.turn_indicator.pack()
        
        # Ramka na plansze
        boards_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        boards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Moja plansza
        my_board_frame = tk.Frame(boards_frame, bg=COLORS['bg_secondary'], padx=10, pady=10)
        my_board_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        my_board_title = tk.Label(
            my_board_frame,
            text="🚢 TWOJA FLOTA",
            font=self.header_font,
            fg=COLORS['text'],
            bg=COLORS['bg_secondary']
        )
        my_board_title.pack(pady=(0, 8))
        
        self.my_board_canvas = self._create_board_canvas(my_board_frame, interactive=False)
        self.my_board_canvas.pack()
        
        # Plansza przeciwnika
        enemy_board_frame = tk.Frame(boards_frame, bg=COLORS['bg_secondary'], padx=10, pady=10)
        enemy_board_frame.pack(side=tk.LEFT)
        
        enemy_board_title = tk.Label(
            enemy_board_frame,
            text="🎯 PLANSZA STRZAŁÓW",
            font=self.header_font,
            fg=COLORS['text'],
            bg=COLORS['bg_secondary']
        )
        enemy_board_title.pack(pady=(0, 8))
        
        self.enemy_board_canvas = self._create_board_canvas(enemy_board_frame, interactive=True)
        self.enemy_board_canvas.pack()
        
        # Panel statusu
        status_frame = tk.Frame(main_frame, bg=COLORS['bg_secondary'], pady=10, padx=15)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Połącz się z serwerem, aby rozpocząć grę",
            font=self.status_font,
            fg=COLORS['text'],
            bg=COLORS['bg_secondary'],
            wraplength=600
        )
        self.status_label.pack()
        
        # Panel połączenia
        connection_frame = tk.Frame(main_frame, bg=COLORS['bg'], pady=15)
        connection_frame.pack(fill=tk.X)
        
        tk.Label(
            connection_frame,
            text="Serwer:",
            font=self.small_font,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.host_entry = tk.Entry(
            connection_frame,
            font=self.small_font,
            width=15,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            insertbackground=COLORS['text']
        )
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            connection_frame,
            text="Port:",
            font=self.small_font,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.port_entry = tk.Entry(
            connection_frame,
            font=self.small_font,
            width=6,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            insertbackground=COLORS['text']
        )
        self.port_entry.insert(0, "5000")
        self.port_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        self.connect_btn = tk.Button(
            connection_frame,
            text="🔗 Połącz",
            font=self.small_font,
            command=self._connect_clicked,
            bg=COLORS['accent'],
            fg=COLORS['bg'],
            activebackground=COLORS['success'],
            activeforeground=COLORS['text'],
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.connect_btn.pack(side=tk.LEFT)
        
        # Legenda
        legend_frame = tk.Frame(main_frame, bg=COLORS['bg'], pady=10)
        legend_frame.pack(fill=tk.X)
        
        legends = [
            ("🟦", "Woda", COLORS['water']),
            ("🚢", "Statek", COLORS['ship']),
            ("💥", "Trafienie", COLORS['hit']),
            ("⚫", "Pudło", COLORS['miss']),
            ("☠️", "Zatopiony", COLORS['sunk']),
        ]
        
        for emoji, text, color in legends:
            item = tk.Frame(legend_frame, bg=COLORS['bg'])
            item.pack(side=tk.LEFT, padx=10)
            
            tk.Label(item, text=emoji, font=self.small_font, bg=COLORS['bg']).pack(side=tk.LEFT)
            tk.Label(item, text=text, font=self.small_font, fg=color, bg=COLORS['bg']).pack(side=tk.LEFT, padx=3)
        
        # Obsługa zamknięcia okna
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Rysuj początkowe plansze
        self._draw_board(self.my_board_canvas, self.my_board, is_mine=True)
        self._draw_board(self.enemy_board_canvas, self.enemy_board, is_mine=False)
    
    def _create_board_canvas(self, parent, interactive: bool) -> tk.Canvas:
        """Tworzy canvas dla planszy."""
        width = BOARD_SIZE * CELL_SIZE + 2 * BOARD_PADDING
        height = BOARD_SIZE * CELL_SIZE + 2 * BOARD_PADDING
        
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=COLORS['bg_secondary'],
            highlightthickness=0
        )
        
        if interactive:
            canvas.bind("<Button-1>", self._on_enemy_board_click)
            canvas.bind("<Motion>", self._on_enemy_board_hover)
            canvas.bind("<Leave>", self._on_enemy_board_leave)
        
        return canvas
    
    def _draw_board(self, canvas: tk.Canvas, board: List[List[CellState]], is_mine: bool):
        """Rysuje planszę na canvasie."""
        canvas.delete("all")
        
        # Rysuj etykiety kolumn (A-J)
        for col in range(BOARD_SIZE):
            x = BOARD_PADDING + col * CELL_SIZE + CELL_SIZE // 2
            canvas.create_text(
                x, BOARD_PADDING // 2,
                text=chr(ord('A') + col),
                fill=COLORS['text_secondary'],
                font=self.small_font
            )
        
        # Rysuj etykiety wierszy (1-10)
        for row in range(BOARD_SIZE):
            y = BOARD_PADDING + row * CELL_SIZE + CELL_SIZE // 2
            canvas.create_text(
                BOARD_PADDING // 2, y,
                text=str(row + 1),
                fill=COLORS['text_secondary'],
                font=self.small_font
            )
        
        # Rysuj pola
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = BOARD_PADDING + col * CELL_SIZE
                y1 = BOARD_PADDING + row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                state = board[row][col]
                
                # Określ kolor pola
                if state == CellState.EMPTY:
                    color = COLORS['water']
                elif state == CellState.SHIP:
                    color = COLORS['ship'] if is_mine else COLORS['water']
                elif state == CellState.MISS:
                    color = COLORS['miss']
                elif state == CellState.HIT:
                    color = COLORS['hit']
                else:
                    color = COLORS['water']
                
                # Rysuj pole
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=COLORS['grid'],
                    width=1,
                    tags=f"cell_{row}_{col}"
                )
                
                # Dodaj symbol dla trafień i pudeł
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                if state == CellState.HIT:
                    canvas.create_text(cx, cy, text="💥", font=("Segoe UI Emoji", 14))
                elif state == CellState.MISS:
                    canvas.create_oval(
                        cx - 5, cy - 5, cx + 5, cy + 5,
                        fill=COLORS['text_secondary'],
                        outline=""
                    )
    
    def _get_cell_from_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Zwraca współrzędne komórki na podstawie pozycji myszy."""
        col = (x - BOARD_PADDING) // CELL_SIZE
        row = (y - BOARD_PADDING) // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None
    
    def _on_enemy_board_click(self, event):
        """Obsługuje kliknięcie na planszy przeciwnika."""
        if not self.game_active or not self.my_turn:
            return
        
        cell = self._get_cell_from_coords(event.x, event.y)
        if cell is None:
            return
        
        row, col = cell
        
        # Sprawdź czy już strzelano w to pole
        if self.enemy_board[row][col] != CellState.EMPTY:
            self._update_status("To pole było już ostrzeliwane!", COLORS['warning'])
            return
        
        # Wyślij strzał
        self._send_shot(row, col)
    
    def _on_enemy_board_hover(self, event):
        """Obsługuje najechanie na planszę przeciwnika."""
        if not self.game_active or not self.my_turn:
            return
        
        cell = self._get_cell_from_coords(event.x, event.y)
        
        # Reset wszystkich pól
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.enemy_board[row][col] == CellState.EMPTY:
                    x1 = BOARD_PADDING + col * CELL_SIZE
                    y1 = BOARD_PADDING + row * CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE
                    
                    color = COLORS['water_hover'] if cell == (row, col) else COLORS['water']
                    self.enemy_board_canvas.itemconfig(f"cell_{row}_{col}", fill=color)
        
        # Zmień kursor
        if cell and self.enemy_board[cell[0]][cell[1]] == CellState.EMPTY:
            self.enemy_board_canvas.config(cursor="crosshair")
        else:
            self.enemy_board_canvas.config(cursor="")
    
    def _on_enemy_board_leave(self, event):
        """Obsługuje opuszczenie planszy przeciwnika."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.enemy_board[row][col] == CellState.EMPTY:
                    self.enemy_board_canvas.itemconfig(f"cell_{row}_{col}", fill=COLORS['water'])
        
        self.enemy_board_canvas.config(cursor="")
    
    def _connect_clicked(self):
        """Obsługuje kliknięcie przycisku połączenia."""
        if self.connected:
            self._disconnect()
            return
        
        host = self.host_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowy numer portu")
            return
        
        self._connect(host, port)
    
    def _connect(self, host: str, port: int):
        """Łączy się z serwerem."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((host, port))
            self.socket.settimeout(None)
            
            self.connected = True
            self.running = True
            
            # Uruchom wątek odbierania
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Zaktualizuj UI
            self.connect_btn.config(text="🔌 Rozłącz", bg=COLORS['hit'])
            self.host_entry.config(state='disabled')
            self.port_entry.config(state='disabled')
            self._update_status("Połączono z serwerem. Oczekiwanie na przeciwnika...", COLORS['success'])
            self._update_turn_indicator("Oczekiwanie na drugiego gracza...", COLORS['text_secondary'])
            
        except socket.timeout:
            messagebox.showerror("Błąd", "Upłynął limit czasu połączenia")
        except ConnectionRefusedError:
            messagebox.showerror("Błąd", f"Nie można połączyć z {host}:{port}\nUpewnij się, że serwer jest uruchomiony.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd połączenia: {e}")
    
    def _disconnect(self):
        """Rozłącza się z serwerem."""
        self.running = False
        self.connected = False
        self.game_active = False
        self.my_turn = False
        
        if self.socket:
            try:
                send_message(self.socket, Message(MessageType.DISCONNECT, {}))
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Zaktualizuj UI
        self.connect_btn.config(text="🔗 Połącz", bg=COLORS['accent'])
        self.host_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self._update_status("Rozłączono z serwerem", COLORS['text_secondary'])
        self._update_turn_indicator("Oczekiwanie na połączenie...", COLORS['text_secondary'])
        
        # Reset planszy
        self.my_board = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.enemy_board = [[CellState.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self._draw_board(self.my_board_canvas, self.my_board, is_mine=True)
        self._draw_board(self.enemy_board_canvas, self.enemy_board, is_mine=False)
    
    def _receive_loop(self):
        """Pętla odbierania wiadomości od serwera."""
        while self.running and self.socket:
            try:
                msg = receive_message(self.socket)
                
                if msg is None:
                    self.root.after(0, lambda: self._handle_disconnect())
                    break
                
                # Przetwórz wiadomość w głównym wątku
                self.root.after(0, lambda m=msg: self._process_message(m))
                
            except Exception as e:
                if self.running:
                    self.root.after(0, lambda: self._handle_disconnect())
                break
    
    def _process_message(self, msg: Message):
        """Przetwarza wiadomość od serwera."""
        if msg.type == MessageType.CONNECTED:
            self.player_id = msg.data["player_id"]
            self._load_board(msg.data["your_board"], is_mine=True)
            self._update_status(f"Dołączono jako Gracz {self.player_id + 1}. Oczekiwanie na przeciwnika...", COLORS['success'])
        
        elif msg.type == MessageType.GAME_START:
            self.game_active = True
            self.my_turn = msg.data["your_turn"]
            
            self._load_board(msg.data["your_board"], is_mine=True)
            self._load_board(msg.data["opponent_board"], is_mine=False)
            
            if self.my_turn:
                self._update_turn_indicator("🎯 TWOJA TURA - Strzelaj!", COLORS['success'])
                self._update_status("Gra rozpoczęta! Kliknij na planszę strzałów, aby oddać strzał.", COLORS['success'])
            else:
                self._update_turn_indicator("⏳ TURA PRZECIWNIKA - Czekaj...", COLORS['warning'])
                self._update_status("Gra rozpoczęta! Czekaj na ruch przeciwnika.", COLORS['text'])
        
        elif msg.type == MessageType.SHOT_RESULT:
            self._handle_shot_result(msg.data, is_mine=True)
        
        elif msg.type == MessageType.OPPONENT_SHOT:
            self._handle_shot_result(msg.data, is_mine=False)
        
        elif msg.type == MessageType.WAITING:
            self._update_status(msg.data.get("message", "Oczekiwanie..."), COLORS['text_secondary'])
        
        elif msg.type == MessageType.OPPONENT_DISCONNECTED:
            self.game_active = False
            self._update_status("Przeciwnik opuścił grę!", COLORS['warning'])
            self._update_turn_indicator("Przeciwnik rozłączony", COLORS['warning'])
            messagebox.showinfo("Informacja", "Przeciwnik opuścił grę. Poczekaj na nowego gracza.")
        
        elif msg.type == MessageType.DISCONNECT:
            self._disconnect()
        
        elif msg.type == MessageType.ERROR:
            self._update_status(f"Błąd: {msg.data.get('message', 'Nieznany błąd')}", COLORS['hit'])
    
    def _handle_shot_result(self, data: dict, is_mine: bool):
        """Obsługuje wynik strzału."""
        row = data["row"]
        col = data["col"]
        result = data["result"]
        your_turn = data.get("your_turn", False)
        game_over = data.get("game_over", False)
        you_won = data.get("you_won")
        sunk_cells = data.get("sunk_cells")
        
        # Aktualizuj planszę
        if is_mine:
            # Mój strzał - aktualizuj planszę przeciwnika
            if result == ShotResult.HIT.value or result == ShotResult.SUNK.value:
                self.enemy_board[row][col] = CellState.HIT
            else:
                self.enemy_board[row][col] = CellState.MISS
            
            self._draw_board(self.enemy_board_canvas, self.enemy_board, is_mine=False)
            
            # Status
            coord = f"{chr(ord('A') + col)}{row + 1}"
            if result == ShotResult.HIT.value:
                self._update_status(f"🎯 Trafienie w {coord}!", COLORS['success'])
            elif result == ShotResult.SUNK.value:
                self._update_status(f"💥 Zatopiono statek! (pole {coord})", COLORS['accent'])
            else:
                self._update_status(f"💨 Pudło w {coord}", COLORS['text_secondary'])
        else:
            # Strzał przeciwnika - aktualizuj moją planszę
            if result == ShotResult.HIT.value or result == ShotResult.SUNK.value:
                self.my_board[row][col] = CellState.HIT
            else:
                self.my_board[row][col] = CellState.MISS
            
            self._draw_board(self.my_board_canvas, self.my_board, is_mine=True)
            
            # Status
            coord = f"{chr(ord('A') + col)}{row + 1}"
            if result == ShotResult.HIT.value:
                self._update_status(f"😱 Przeciwnik trafił w {coord}!", COLORS['warning'])
            elif result == ShotResult.SUNK.value:
                self._update_status(f"☠️ Przeciwnik zatopił twój statek! (pole {coord})", COLORS['hit'])
            else:
                self._update_status(f"😅 Przeciwnik spudłował w {coord}", COLORS['success'])
        
        # Oznacz zatopiony statek
        if sunk_cells:
            board = self.enemy_board if is_mine else self.my_board
            canvas = self.enemy_board_canvas if is_mine else self.my_board_canvas
            for cell_row, cell_col in sunk_cells:
                x1 = BOARD_PADDING + cell_col * CELL_SIZE
                y1 = BOARD_PADDING + cell_row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                canvas.itemconfig(f"cell_{cell_row}_{cell_col}", fill=COLORS['sunk'])
        
        # Sprawdź koniec gry
        if game_over:
            self.game_active = False
            if you_won:
                self._update_turn_indicator("🏆 ZWYCIĘSTWO!", COLORS['success'])
                self._show_game_over(True)
            else:
                self._update_turn_indicator("💀 PRZEGRANA", COLORS['hit'])
                self._show_game_over(False)
        else:
            # Aktualizuj turę
            self.my_turn = your_turn
            if self.my_turn:
                self._update_turn_indicator("🎯 TWOJA TURA - Strzelaj!", COLORS['success'])
            else:
                self._update_turn_indicator("⏳ TURA PRZECIWNIKA - Czekaj...", COLORS['warning'])
    
    def _show_game_over(self, won: bool):
        """Pokazuje okno końca gry."""
        title = "🏆 Zwycięstwo!" if won else "💀 Przegrana"
        message = "Gratulacje! Zatopiłeś wszystkie statki przeciwnika!" if won else "Niestety, przeciwnik zatopił wszystkie twoje statki."
        
        if messagebox.askyesno(title, f"{message}\n\nCzy chcesz zagrać ponownie?"):
            self._request_rematch()
        else:
            self._disconnect()
    
    def _request_rematch(self):
        """Wysyła żądanie ponownej gry."""
        if self.socket:
            send_message(self.socket, Message(MessageType.PLAY_AGAIN, {}))
            self._update_status("Oczekiwanie na decyzję przeciwnika...", COLORS['text_secondary'])
    
    def _send_shot(self, row: int, col: int):
        """Wysyła strzał do serwera."""
        if self.socket:
            send_message(self.socket, Message(
                MessageType.SHOOT,
                {"row": row, "col": col}
            ))
    
    def _load_board(self, board_data: dict, is_mine: bool):
        """Ładuje planszę z danych słownikowych."""
        grid = board_data["grid"]
        board = self.my_board if is_mine else self.enemy_board
        canvas = self.my_board_canvas if is_mine else self.enemy_board_canvas
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                board[row][col] = CellState(grid[row][col])
        
        self._draw_board(canvas, board, is_mine=is_mine)
    
    def _update_status(self, text: str, color: str = COLORS['text']):
        """Aktualizuje etykietę statusu."""
        if self.status_label:
            self.status_label.config(text=text, fg=color)
    
    def _update_turn_indicator(self, text: str, color: str = COLORS['text']):
        """Aktualizuje wskaźnik tury."""
        if self.turn_indicator:
            self.turn_indicator.config(text=text, fg=color)
    
    def _handle_disconnect(self):
        """Obsługuje rozłączenie z serwerem."""
        if self.connected:
            self._disconnect()
            messagebox.showwarning("Rozłączono", "Utracono połączenie z serwerem")
    
    def _on_closing(self):
        """Obsługuje zamknięcie okna."""
        self.running = False
        
        if self.socket:
            try:
                send_message(self.socket, Message(MessageType.DISCONNECT, {}))
                self.socket.close()
            except:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Uruchamia klienta."""
        self.create_gui()
        self.root.mainloop()


def main():
    client = BattleshipClient()
    client.run()


if __name__ == "__main__":
    main()

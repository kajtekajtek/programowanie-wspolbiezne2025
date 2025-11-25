import socket

IP = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024
END_MESSAGE = "e"

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"Server running on {IP}:{PORT}")
    
    while True:
        players, choices, scores = reset_game_state()
        players = wait_for_two_players(server_socket, choices)
        
        game_ended = False
        while not game_ended:
            if len(choices) < 2:
                game_ended = handle_round(server_socket, players, choices, scores)
            else:
                game_ended = process_round(server_socket, players, choices, scores)
                choices.clear()
        
        end_game(server_socket, players)

def reset_game_state():
    return {}, {}, {}

def wait_for_two_players(socket_obj, choices):
    players = {}
    while len(players) < 2:
        data, addr = socket_obj.recvfrom(BUFFER_SIZE)
        message = data.decode().strip().lower()
        player_port = addr[1]
        
        if player_port not in players:
            players[player_port] = addr
            choices[player_port] = message
            print(f"Player {len(players)} connected from port {player_port}")
    
    return players

def handle_round(socket_obj, players, choices, scores):
    while len(choices) < 2:
        data, addr = socket_obj.recvfrom(BUFFER_SIZE)
        message = data.decode().strip().lower()
        player_port = addr[1]
        
        if player_port in players:
            choices[player_port] = message
    
    return process_round(socket_obj, players, choices, scores)

def process_round(socket_obj, players, choices, scores):
    ports = list(choices.keys())
    choice1 = choices[ports[0]]
    choice2 = choices[ports[1]]
    
    if choice1 == END_MESSAGE or choice2 == END_MESSAGE:
        return True
    
    winner = determine_winner(choice1, choice2)
    
    if winner == 1:
        scores[ports[0]] = scores.get(ports[0], 0) + 1
    elif winner == 2:
        scores[ports[1]] = scores.get(ports[1], 0) + 1
    
    result1 = format_result(choice2, winner, 1)
    result2 = format_result(choice1, winner, 2)
    
    socket_obj.sendto(result1.encode(), players[ports[0]])
    socket_obj.sendto(result2.encode(), players[ports[1]])
    
    score1 = scores.get(ports[0], 0)
    score2 = scores.get(ports[1], 0)
    print(f"Scores - Player {ports[0]}: {score1}, Player {ports[1]}: {score2}")
    
    return False

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return 0
    if (choice1 == "r" and choice2 == "s") or \
       (choice1 == "p" and choice2 == "r") or \
       (choice1 == "s" and choice2 == "p"):
        return 1
    return 2

def format_result(opponent_choice, winner, player_num):
    opponent_map = {"r": "rock", "p": "paper", "s": "scissors"}
    opponent = opponent_map.get(opponent_choice, "unknown")
    
    if winner == 0:
        result = "draw"
    elif winner == player_num:
        result = "win"
    else:
        result = "loss"
    
    return f"{opponent},{result}"

def end_game(socket_obj, players):
    for addr in players.values():
        socket_obj.sendto("game_ended".encode(), addr)
    
    print("Game ended. Waiting for new players...")

if __name__ == "__main__":
    main()

import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    score = 0
    
    print("Connected to server. Starting game...")
    
    while True:
        choice = get_user_choice()
        client_socket.sendto(choice.encode(), (SERVER_IP, SERVER_PORT))
        
        if choice == "e":
            print("Ending game...")
            break
        
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        result_str = data.decode().strip()
        
        if result_str == "game_ended":
            print("Game has ended.")
            break
        
        opponent, outcome = parse_result(result_str)
        
        if outcome == "win":
            score += 1
        
        display_result(opponent, outcome, score)
    
    client_socket.close()

def get_user_choice():
    while True:
        choice = input("Enter choice (r=rock, p=paper, s=scissors, e=end): ").strip().lower()
        if choice in ["r", "p", "s", "e"]:
            return choice
        print("Invalid choice. Use r, p, s, or e.")

def parse_result(result_str):
    parts = result_str.split(",")
    if len(parts) == 2:
        return parts[0], parts[1]
    return "unknown", "unknown"

def display_result(opponent, outcome, score):
    outcome_map = {"win": "You won!", "loss": "You lost!", "draw": "It's a draw!"}
    print(f"Opponent chose: {opponent}")
    print(f"Result: {outcome_map.get(outcome, outcome)}")
    print(f"Your score: {score}")
    print()

if __name__ == "__main__":
    main()

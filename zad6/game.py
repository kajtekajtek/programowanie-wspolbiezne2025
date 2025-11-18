#!/usr/bin/env python3
import sysv_ipc
import time
import sys

KEY_BASE = 12345
NULL_CHAR = '\0'
NUM_ROUNDS = 3

KEY_MEM1 = KEY_BASE
KEY_MEM2 = KEY_BASE + 1
KEY_SEM_P1_WRITE = KEY_BASE + 2
KEY_SEM_P2_WRITE = KEY_BASE + 3
KEY_SEM_P1_READ = KEY_BASE + 4
KEY_SEM_P2_READ = KEY_BASE + 5

def main():
    print("\n" + "=" * 60)
    print("THREE CARD MONTE GAME")
    print("=" * 60)
    print("Starting game...")
    
    try:
        test_sem = sysv_ipc.Semaphore(KEY_SEM_P1_WRITE, sysv_ipc.IPC_CREX, 0o700, 0)
        is_player1 = True
        test_sem.remove()
    except sysv_ipc.ExistentialError:
        is_player1 = False
        time.sleep(0.2)
    
    if is_player1:
        player1_logic()
    else:
        player2_logic()

def player1_logic():
    print("=" * 60)
    print("You are PLAYER 1 (Card Placer)")
    print("=" * 60)
    print("Rules: Choose where to place the winning card (1, 2, or 3).")
    print("You win if Player 2 guesses wrong.\n")
    
    try:
        mem1 = sysv_ipc.SharedMemory(KEY_MEM1, sysv_ipc.IPC_CREX, size=64)
        mem2 = sysv_ipc.SharedMemory(KEY_MEM2, sysv_ipc.IPC_CREX, size=64)
        
        sem_p1_write = sysv_ipc.Semaphore(KEY_SEM_P1_WRITE, sysv_ipc.IPC_CREX, 0o700, 0)
        sem_p2_write = sysv_ipc.Semaphore(KEY_SEM_P2_WRITE, sysv_ipc.IPC_CREX, 0o700, 0)
        sem_p1_read = sysv_ipc.Semaphore(KEY_SEM_P1_READ, sysv_ipc.IPC_CREX, 0o700, 0)
        sem_p2_read = sysv_ipc.Semaphore(KEY_SEM_P2_READ, sysv_ipc.IPC_CREX, 0o700, 0)
        
        write_to_memory(mem1, 0)
        write_to_memory(mem2, 0)
        
        print("[Player 1] IPC resources created. Waiting for Player 2...\n")
        time.sleep(1)
        
    except Exception as e:
        print(f"[Player 1] Error creating resources: {e}")
        sys.exit(1)
    
    score_p1 = 0
    score_p2 = 0
   
    try:
        for round_num in range(1, NUM_ROUNDS + 1):
            print(f"\n{'='*60}")
            print(f"ROUND {round_num}")
            print(f"{'='*60}")
            
            p1_choice = get_player_choice(1, round_num)
            write_to_memory(mem1, p1_choice)
            print(f"[Player 1] You placed the winning card at position {p1_choice}")
            sem_p1_write.release()
            
            sem_p2_write.acquire()
            
            p2_choice = read_from_memory(mem2)
            print(f"[Player 1] Player 2 guessed position {p2_choice}")
            sem_p1_read.release()
            
            sem_p2_read.acquire()
            
            if p1_choice == p2_choice:
                print(f"\n[Result] Round {round_num}: Player 2 WINS! (Correct guess)")
                score_p2 += 1
            else:
                print(f"\n[Result] Round {round_num}: Player 1 WINS! (Wrong guess)")
                score_p1 += 1
            
            print(f"[Score] Player 1: {score_p1} | Player 2: {score_p2}")
        
        print("\n" + "=" * 60)
        print("GAME OVER")
        print("=" * 60)
        print(f"Final Score: Player 1: {score_p1} | Player 2: {score_p2}")
        if score_p1 > score_p2:
            print("PLAYER 1 WINS THE GAME!")
        elif score_p2 > score_p1:
            print("PLAYER 2 WINS THE GAME!")
        else:
            print("IT'S A TIE!")
        print("=" * 60)
        
        time.sleep(0.5)
        cleanup_resources(mem1, mem2, sem_p1_write, sem_p2_write, sem_p1_read, sem_p2_read)
        
    except KeyboardInterrupt:
        print("\n[Player 1] Game interrupted. Cleaning up...")
        cleanup_resources(mem1, mem2, sem_p1_write, sem_p2_write, sem_p1_read, sem_p2_read)
        sys.exit(1)


def player2_logic():
    print("=" * 60)
    print("You are PLAYER 2 (Guesser)")
    print("=" * 60)
    print("Rules: Guess where the winning card is (1, 2, or 3).")
    print("You win if you guess correctly.\n")
    
    try:
        mem1 = sysv_ipc.SharedMemory(KEY_MEM1)
        mem2 = sysv_ipc.SharedMemory(KEY_MEM2)
        sem_p1_write = sysv_ipc.Semaphore(KEY_SEM_P1_WRITE)
        sem_p2_write = sysv_ipc.Semaphore(KEY_SEM_P2_WRITE)
        sem_p1_read = sysv_ipc.Semaphore(KEY_SEM_P1_READ)
        sem_p2_read = sysv_ipc.Semaphore(KEY_SEM_P2_READ)
        
        print("[Player 2] Connected to game. Let's play!\n")
        
    except Exception as e:
        print(f"[Player 2] Error connecting to resources: {e}")
        print("[Player 2] Make sure Player 1 is running first!")
        sys.exit(1)
    
    score_p1 = 0
    score_p2 = 0
    
    try:
        for round_num in range(1, NUM_ROUNDS + 1):
            print(f"\n{'='*60}")
            print(f"ROUND {round_num}")
            print(f"{'='*60}")
            
            sem_p1_write.acquire()
            
            p2_choice = get_player_choice(2, round_num)
            write_to_memory(mem2, p2_choice)
            print(f"[Player 2] You guessed position {p2_choice}")
            sem_p2_write.release()
            
            sem_p1_read.acquire()
            
            p1_choice = read_from_memory(mem1)
            print(f"[Player 2] Player 1 placed the card at position {p1_choice}")
            sem_p2_read.release()
            
            if p1_choice == p2_choice:
                print(f"\n[Result] Round {round_num}: Player 2 WINS! (Correct guess)")
                score_p2 += 1
            else:
                print(f"\n[Result] Round {round_num}: Player 1 WINS! (Wrong guess)")
                score_p1 += 1
            
            print(f"[Score] Player 1: {score_p1} | Player 2: {score_p2}")
        
        print("\n" + "=" * 60)
        print("GAME OVER")
        print("=" * 60)
        print(f"Final Score: Player 1: {score_p1} | Player 2: {score_p2}")
        if score_p1 > score_p2:
            print("PLAYER 1 WINS THE GAME!")
        elif score_p2 > score_p1:
            print("PLAYER 2 WINS THE GAME!")
        else:
            print("IT'S A TIE!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n[Player 2] Game interrupted. Exiting...")
        sys.exit(1)

def write_to_memory(mem, value):
    s = str(value) + NULL_CHAR
    s = s.encode()
    mem.write(s)

def get_player_choice(player_num, round_num):
    while True:
        try:
            choice = input(f"[Player {player_num}] Round {round_num}: Choose position (1, 2, or 3): ")
            choice = int(choice)
            if choice in [1, 2, 3]:
                return choice
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except (ValueError, KeyboardInterrupt):
            print("\nInvalid input. Please enter a number between 1 and 3.")
        except EOFError:
            print("\nEOF received. Exiting...")
            sys.exit(1)

def read_from_memory(mem):
    s = mem.read()
    s = s.decode()
    i = s.find(NULL_CHAR)
    if i != -1:
        s = s[:i]
    return int(s) if s else 0

def cleanup_resources(mem1, mem2, sem_p1_write, sem_p2_write, sem_p1_read, sem_p2_read):
    try:
        mem1.remove()
        mem2.remove()
        sem_p1_write.remove()
        sem_p2_write.remove()
        sem_p1_read.remove()
        sem_p2_read.remove()
        print("\n[Cleanup] All IPC resources removed.")
    except Exception as e:
        print(f"\n[Cleanup] Error removing resources: {e}")

if __name__ == "__main__":
    main()


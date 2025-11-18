# Zadanie 6 - Three Card Monte Game

## Description

A two-player card guessing game implemented using System V IPC (shared memory and semaphores).

### Game Rules

- **Player 1 (Card Placer)**: Chooses where to place the winning card (position 1, 2, or 3)
- **Player 2 (Guesser)**: Tries to guess the position of the winning card
- **Scoring**: 
  - Player 2 wins if they guess correctly
  - Player 1 wins if Player 2 guesses incorrectly
- **Game Length**: 3 rounds
- **Winner**: Player with the highest score after 3 rounds

## Requirements

- Python 3
- `sysv_ipc` module

Install requirements:
```bash
pip install sysv_ipc
```

## How to Run

1. Open two terminal windows

2. In the **first terminal**, run:
```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad6
python3 game.py
```

3. In the **second terminal**, run:
```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad6
python3 game.py
```

The first process to start becomes Player 1 (Card Placer).
The second process becomes Player 2 (Guesser).

## How to Play

1. **Player 1** will be prompted first to choose a position (1, 2, or 3) for the winning card
2. **Player 2** will then be prompted to guess the position
3. Both players will see the results of the round
4. This repeats for 3 rounds
5. Final scores are displayed and IPC resources are automatically cleaned up

## Implementation Details

### IPC Resources Used

- **Shared Memory 1 (PW1)**: Stores Player 1's choice
- **Shared Memory 2 (PW2)**: Stores Player 2's choice
- **Semaphores** (4 total):
  - `sem_p1_write`: Signals Player 1 has written their choice
  - `sem_p2_write`: Signals Player 2 has written their choice
  - `sem_p1_read`: Signals Player 1 has read Player 2's choice
  - `sem_p2_read`: Signals Player 2 has read Player 1's choice

### Synchronization

The synchronization ensures:
1. Player 1 writes first, then Player 2 writes
2. Both players must write before either can read
3. Both players must read before the next round can begin
4. No busy waiting - all synchronization uses semaphore blocking

### Cleanup

The game automatically removes all IPC resources (shared memory and semaphores) when:
- The game completes normally after 3 rounds
- Player 1 receives Ctrl+C (keyboard interrupt)

## Manual Cleanup

If resources are not cleaned up properly (e.g., process crash), you can manually remove them:

```bash
# List IPC resources
ipcs

# Remove semaphores
ipcrm -s <semaphore_id>

# Remove shared memory
ipcrm -m <shared_memory_id>
```

Or use the cleanup script:
```bash
ipcs -s | grep $(whoami) | awk '{print $2}' | xargs -r ipcrm -s
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -r ipcrm -m
```

## Example Game Session

```
Player 1 Terminal:
==================
You are PLAYER 1 (Card Placer)
Round 1: Choose position (1, 2, or 3): 2
You placed the winning card at position 2
Player 2 guessed position 1
Round 1: Player 1 WINS! (Wrong guess)
Score: Player 1: 1 | Player 2: 0

Player 2 Terminal:
==================
You are PLAYER 2 (Guesser)
Round 1: Choose position (1, 2, or 3): 1
You guessed position 1
Player 1 placed the card at position 2
Round 1: Player 1 WINS! (Wrong guess)
Score: Player 1: 1 | Player 2: 0
```

## Notes

- The program uses `sysv_ipc.IPC_CREX` flag to determine which process becomes Player 1
- All code and comments are in English (no Polish in the code)
- Proper error handling for invalid inputs
- Graceful cleanup on exit


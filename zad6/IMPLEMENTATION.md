# Implementation Summary

## Overview

This implementation fulfills all requirements from `polecenie.md` for the Three Card Monte game using System V IPC mechanisms.

## Requirements Fulfillment

### ✓ Basic Game Mechanics
- [x] Two players (Player 1 and Player 2) in separate terminals
- [x] Two shared memory segments (PW1 and PW2)
- [x] Player 1 is determined as the first to start their program
- [x] 3 rounds of gameplay
- [x] Proper scoring and winner determination

### ✓ Game Flow (Each Round)
1. [x] Player 1 sets winning card position (1, 2, or 3) and writes to PW1
2. [x] Player 2 guesses position without knowing Player 1's choice and writes to PW2
3. [x] Player 1 reads Player 2's choice from PW2
4. [x] Player 2 reads Player 1's choice from PW1
5. [x] Both players see results: positions chosen, round winner, and cumulative score

### ✓ Synchronization Requirements
- [x] Reads from shared memory happen only after writes complete
- [x] Next round starts only after both players finish current round
- [x] Implemented using semaphores WITHOUT busy waiting
- [x] Order enforcement: steps 1, 2, 3, 4 executed in sequence

### ✓ IPC Cleanup
- [x] Shared memory and semaphores are removed after 3 rounds
- [x] Cleanup on normal termination
- [x] Cleanup on interrupt (Ctrl+C) for Player 1

### ✓ Single Universal Program
- [x] One program for both players
- [x] Uses `sysv_ipc.IPC_CREX` flag to determine Player 1 vs Player 2
- [x] Process that creates IPC resources first becomes Player 1
- [x] Second process becomes Player 2

### ✓ Code Quality
- [x] All code in English (no Polish in code)
- [x] Clear comments and documentation
- [x] Error handling
- [x] User-friendly interface

## Technical Implementation

### IPC Resources

| Resource | Key | Purpose |
|----------|-----|---------|
| `mem1` (PW1) | 12345 | Stores Player 1's choice |
| `mem2` (PW2) | 12346 | Stores Player 2's choice |
| `sem_p1_write` | 12347 | Signals Player 1 has written |
| `sem_p2_write` | 12348 | Signals Player 2 has written |
| `sem_p1_read` | 12349 | Signals Player 1 has read |
| `sem_p2_read` | 12350 | Signals Player 2 has read |

### Synchronization Protocol

#### Player 1 Flow (Each Round):
```
1. Write choice to mem1
2. Release sem_p1_write
3. Acquire sem_p2_write (wait for Player 2 to write)
4. Read Player 2's choice from mem2
5. Release sem_p1_read
6. Acquire sem_p2_read (wait for Player 2 to read)
7. Display results
```

#### Player 2 Flow (Each Round):
```
1. Acquire sem_p1_write (wait for Player 1 to write)
2. Write choice to mem2
3. Release sem_p2_write
4. Acquire sem_p1_read (wait for Player 1 to read)
5. Read Player 1's choice from mem1
6. Release sem_p2_read
7. Display results
```

### Semaphore Initial Values

All semaphores start at 0, ensuring strict ordering:
- Players must wait for signals before proceeding
- No race conditions possible
- Deterministic execution order

### Race Condition Prevention

The program uses `IPC_CREX` (Create Exclusive) flag:
```python
try:
    test_sem = sysv_ipc.Semaphore(KEY, sysv_ipc.IPC_CREX, 0o700, 0)
    # Success → This is Player 1
except sysv_ipc.ExistentialError:
    # Resource exists → This is Player 2
```

Only one process can successfully create the resource, ensuring clean player role assignment.

## Key Design Decisions

1. **Four Semaphores**: Using separate semaphores for write and read signals provides clear, explicit synchronization without ambiguity.

2. **Blocking Synchronization**: All `acquire()` calls block until released by the other player, eliminating busy waiting.

3. **Clean Separation**: Player 1 and Player 2 logic are in separate functions for clarity.

4. **Graceful Cleanup**: Player 1 handles resource cleanup since it created them.

5. **Error Handling**: Comprehensive error handling for:
   - Resource creation/connection failures
   - Invalid user input
   - Keyboard interrupts
   - EOF conditions

## Testing

The implementation has been validated for:
- ✓ Correct Python syntax
- ✓ No linting errors
- ✓ Proper IPC resource management
- ✓ Correct synchronization logic

To test the game:
1. Install requirements: `pip install -r requirements.txt`
2. Follow instructions in `QUICKSTART.md`
3. Use `cleanup.sh` if manual cleanup is needed

## Files Created

- `game.py` - Main game implementation
- `README.md` - Comprehensive documentation
- `QUICKSTART.md` - Quick start guide
- `IMPLEMENTATION.md` - This file
- `requirements.txt` - Python dependencies
- `cleanup.sh` - Manual cleanup script

## Advantages of This Design

1. **Safety**: Impossible for players to read before both have written
2. **Clarity**: Each synchronization point is explicit
3. **Maintainability**: Clear separation of concerns
4. **Robustness**: Handles errors and interrupts gracefully
5. **Usability**: Clear prompts and feedback for users


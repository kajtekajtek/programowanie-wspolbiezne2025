# Quick Start Guide

## Installation

```bash
pip install sysv_ipc
```

## Running the Game

### Terminal 1 (Player 1):
```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad6
python3 game.py
```

### Terminal 2 (Player 2):
```bash
cd /home/kajtek/Code/programowanie-wspolbiezne2025/zad6
python3 game.py
```

## Quick Test Scenario

### Round 1:
- Player 1: Enter `1`
- Player 2: Enter `2`
- Expected: Player 1 wins (different positions)

### Round 2:
- Player 1: Enter `3`
- Player 2: Enter `3`
- Expected: Player 2 wins (same position)

### Round 3:
- Player 1: Enter `2`
- Player 2: Enter `1`
- Expected: Player 1 wins (different positions)

**Expected Final Score**: Player 1: 2, Player 2: 1

## Troubleshooting

### Issue: "Error creating/connecting to resources"

1. Check if resources already exist:
```bash
ipcs
```

2. Clean up existing resources:
```bash
./cleanup.sh
```

### Issue: Process stuck

- Press `Ctrl+C` to interrupt
- Run cleanup script:
```bash
./cleanup.sh
```

### Issue: "Permission denied"

Make scripts executable:
```bash
chmod +x game.py cleanup.sh
```

## Verifying Synchronization

The game ensures proper synchronization:

1. **Order enforcement**: Player 1 always writes first, then Player 2
2. **No race conditions**: Both must write before either can read
3. **Turn-based**: Next round waits for both players to finish current round
4. **No busy waiting**: All synchronization uses blocking semaphores

You can verify this by observing:
- Player 2 cannot enter their guess until Player 1 has chosen
- Results are displayed only after both players have made their choices
- Next round doesn't start until current round completes


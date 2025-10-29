# Task 4: FIFO-based Client-Server Database

## Overview

A simple multi-access database server using FIFO queues for communication. The server maintains a database of (ID, surname) pairs and responds to client queries.

## Files

- `server.py` - Database server with signal handling
- `client.py` - Client program for querying the database
- `test_concurrent.sh` - Test script for concurrent clients
- `test_signals.sh` - Test script for signal handling

## Database Contents

| ID | Surname |
|----|---------|
| 1  | Kowalski |
| 2  | Nowak |
| 3  | Wiśniewski |
| 4  | Dąbrowski |
| 5  | Lewandowski |

## Communication Protocol

### Client to Server Message Format
```
| int (4 bytes) | int (4 bytes) | string (variable) |
|  msg length   |      ID       |  client queue path |
```

### Server to Client Message Format
```
| int (4 bytes) | string (variable) |
|  msg length   |     response      |
```

## Signal Handling

- **SIGHUP**: Ignored
- **SIGTERM**: Ignored
- **SIGUSR1**: Terminates the server

## Usage

### 1. Start the Server

```bash
chmod +x server.py
./server.py
```

The server will display its PID and start listening for requests.

### 2. Run Client Queries

In separate terminals:

```bash
chmod +x client.py
./client.py 1    # Query ID 1
./client.py 3    # Query ID 3
./client.py 99   # Query non-existent ID
```

### 3. Test Concurrent Clients

```bash
chmod +x test_concurrent.sh
./test_concurrent.sh
```

This will start 3 clients simultaneously to test queue handling.

### 4. Test Signal Handling

```bash
chmod +x test_signals.sh
./test_signals.sh <server_pid>
```

Replace `<server_pid>` with the actual PID displayed by the server.

## Implementation Details

- **Atomic writes**: All messages use single `os.write()` calls
- **Blocking reads**: Server uses non-blocking mode with sleep to avoid busy-waiting
- **Delay simulation**: 2-second delay in server allows testing concurrent requests
- **FIFO queues**:
  - Server queue: `/tmp/server_fifo` (shared by all clients)
  - Client queues: `/tmp/client_fifo_{pid}_{id}` (unique per client)

## Example Session

Terminal 1 (Server):
```
$ ./server.py
Database Server
==================================================

Database contents:
  1: Kowalski
  2: Nowak
  3: Wiśniewski
  4: Dąbrowski
  5: Lewandowski

Server FIFO created at: /tmp/server_fifo
Server PID: 12345
Server is running. Waiting for requests...
Send SIGUSR1 to stop the server
==================================================

Processing request: ID=1, Client queue=/tmp/client_fifo_12346_1
Simulating work delay (2 seconds)...
Found: Kowalski
Response sent to client
```

Terminal 2 (Client):
```
$ ./client.py 1
Client PID: 12346
Requesting record with ID: 1
Client FIFO created: /tmp/client_fifo_12346_1
Sending request to server...
Waiting for response...

==================================================
Response from server: Kowalski
==================================================
Client FIFO cleaned up
```

## Notes

- The server introduces a 2-second delay before responding to simulate work and enable testing with multiple concurrent clients
- FIFO queues are automatically cleaned up on exit
- Each client creates its own unique FIFO queue for receiving responses


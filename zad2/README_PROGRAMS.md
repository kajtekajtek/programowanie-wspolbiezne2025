# Text Communication System - Client-Server

A simple text communication system implemented in Python with file-based synchronization using lockfiles.

## Overview

The system consists of two programs:
- **Server** (`server.py`): Runs continuously, receives messages from clients and sends responses
- **Client** (`client.py`): Runs once to send a message and receive a response

## Features

- Multiple clients can connect simultaneously
- Lockfile-based synchronization prevents race conditions
- Atomic lock acquisition using `O_CREAT|O_EXCL` flags
- Clients display "Server busy, please wait" when server is occupied
- ESC character used as end-of-message marker

## Usage

### Starting the Server

```bash
python3 server.py <buffer_file>
```

Example:
```bash
python3 server.py server_buffer.txt
```

The server will:
1. Wait for clients to connect
2. Display received messages
3. Prompt for responses
4. Send responses back to clients

To stop the server, press `Ctrl+C`.

### Running the Client

```bash
python3 client.py <buffer_file> <response_file>
```

Example:
```bash
python3 client.py server_buffer.txt client1_response.txt
```

The client will:
1. Prompt you to enter a message
2. Wait if server is busy
3. Send the message to server
4. Wait for and display the response

To finish entering your message, press `Ctrl+D` (Linux/Mac) or `Ctrl+Z` then Enter (Windows).

## Testing Concurrent Access

To test the "Server busy" scenario:

### Terminal 1 - Start Server
```bash
python3 server.py server_buffer.txt
```

### Terminal 2 - First Client
```bash
python3 client.py server_buffer.txt client1_response.txt
```
Enter a message and press `Ctrl+D`. **Do not respond on the server yet.**

### Terminal 3 - Second Client (while server is processing first client)
```bash
python3 client.py server_buffer.txt client2_response.txt
```
You should see "Server busy, please wait..." messages.

### Terminal 1 - Server
Now respond to the first client. The second client should then proceed automatically.

## Example Session

### Server Terminal
```
Server starting...
Buffer file: server_buffer.txt
Lockfile: server.lock
Waiting for clients...

============================================================
Message received from client (response file: client1_response.txt)
============================================================
Hello server!
This is a test message.
============================================================

============================================================
Enter your response (press Ctrl+D or Ctrl+Z when done):
============================================================
Hello client!
Message received successfully.
[Press Ctrl+D]

Response sent to: client1_response.txt
Lockfile removed. Ready for next client.
```

### Client Terminal
```
Enter your message (press Ctrl+D or Ctrl+Z when done):
Hello server!
This is a test message.
[Press Ctrl+D]
Lock acquired. Sending message to server...
Message sent to server.
Waiting for server response...

============================================================
Server response:
============================================================
Hello client!
Message received successfully.
============================================================
```

## Technical Details

### Synchronization

- **Lockfile**: `server.lock` (created in working directory)
- **Atomic creation**: Uses `os.open()` with `O_CREAT|O_EXCL` flags
- Ensures only one client can communicate with server at a time

### Message Format

Server buffer file structure:
```
<response_file_path>
<message_line_1>
<message_line_2>
...
<ESC_character>
```

### Constants

Defined in both programs:
- `LOCKFILE_NAME`: Name of the lockfile
- `END_MARKER`: ESC character (`\x1b`)
- `LOCK_RETRY_INTERVAL`: Time between lock attempts (2 seconds)
- `RESPONSE_POLL_INTERVAL`: Time between response checks (0.5 seconds)
- `POLL_INTERVAL`: Server polling interval (0.5 seconds)

## Error Handling

- Client times out after 60 seconds waiting for response
- Server continues running even if errors occur
- Lockfile is cleaned up on interruption
- Response files are cleaned up after use

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)


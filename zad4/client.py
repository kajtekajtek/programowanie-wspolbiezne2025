#!/usr/bin/env python3
import os
import sys
import struct
import time

SERVER_FIFO = "/tmp/server_fifo"

def create_client_fifo(client_id: int) -> str:
    client_fifo = f"/tmp/client_fifo_{os.getpid()}_{client_id}"
    
    if os.path.exists(client_fifo):
        os.remove(client_fifo)
    
    os.mkfifo(client_fifo)
    return client_fifo

def cleanup_client_fifo(client_fifo: str) -> None:
    if os.path.exists(client_fifo):
        os.remove(client_fifo)

def send_request(record_id: int, client_fifo: str) -> None:
    client_fifo_bytes = client_fifo.encode('utf-8')
    
    remaining_length = 4 + len(client_fifo_bytes)
    
    message = struct.pack('i', remaining_length) + struct.pack('i', record_id) + client_fifo_bytes
    
    try:
        fd = os.open(SERVER_FIFO, os.O_WRONLY)
        os.write(fd, message)
        os.close(fd)
    except OSError as e:
        print(f"Error sending request to server: {e}")
        raise

def receive_response(client_fifo: str) -> str:
    fd = os.open(client_fifo, os.O_RDONLY)
    
    length_bytes = os.read(fd, 4)
    if not length_bytes:
        os.close(fd)
        error_msg = "Failed to receive response length"
        print(f"Error: {error_msg}")
        raise OSError(error_msg)
    
    response_length = struct.unpack('i', length_bytes)[0]
    
    response_bytes = os.read(fd, response_length)
    os.close(fd)
    
    return response_bytes.decode('utf-8')

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: ./client.py <ID>")
        print("Example: ./client.py 1")
        sys.exit(1)
    
    try:
        record_id = int(sys.argv[1])
    except ValueError:
        print("Error: ID must be an integer")
        sys.exit(1)
    
    print(f"Client PID: {os.getpid()}")
    print(f"Requesting record with ID: {record_id}")
    
    client_fifo = create_client_fifo(record_id)
    print(f"Client FIFO created: {client_fifo}")
    
    try:
        print("Sending request to server...")
        send_request(record_id, client_fifo)
        
        print("Waiting for response...")
        response = receive_response(client_fifo)
        
        print("\n" + "=" * 50)
        print(f"Response from server: {response}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup_client_fifo(client_fifo)
        print(f"Client FIFO cleaned up")

if __name__ == "__main__":
    main()


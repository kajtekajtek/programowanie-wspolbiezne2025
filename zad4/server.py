#!/usr/bin/env python3
import os
import signal
import struct
import time

SERVER_FIFO = "/tmp/server_fifo"
DELAY_SECONDS = 2

DATABASE = {
    1: "Kowalski",
    2: "Nowak",
    3: "Wiśniewski",
    4: "Dąbrowski",
    5: "Lewandowski",
}

shutdown_flag = False

def signal_handler_exit(signum: int, frame) -> None:
    global shutdown_flag
    print(f"\nReceived SIGUSR1 signal. Shutting down...")
    shutdown_flag = True

def signal_handler_ignore(signum: int, frame) -> None:
    signal_name = "SIGHUP" if signum == signal.SIGHUP else "SIGTERM"
    print(f"\nReceived {signal_name} signal. Ignoring...")

def setup_signal_handlers() -> None:
    signal.signal(signal.SIGHUP, signal_handler_ignore)
    signal.signal(signal.SIGTERM, signal_handler_ignore)
    signal.signal(signal.SIGUSR1, signal_handler_exit)

def create_server_fifo() -> None:
    if os.path.exists(SERVER_FIFO):
        os.remove(SERVER_FIFO)
    os.mkfifo(SERVER_FIFO)
    print(f"Server FIFO created at: {SERVER_FIFO}")

def cleanup() -> None:
    if os.path.exists(SERVER_FIFO):
        os.remove(SERVER_FIFO)
        print("Server FIFO removed")

def read_message(fd: int) -> tuple[int, str] | None:
    length_bytes = os.read(fd, 4)
    if not length_bytes:
        return None
    
    remaining_length = struct.unpack('i', length_bytes)[0]
    
    id_bytes = os.read(fd, 4)
    if len(id_bytes) < 4:
        return None
    
    record_id = struct.unpack('i', id_bytes)[0]
    
    client_queue_path_length = remaining_length - 4
    client_queue_path = os.read(fd, client_queue_path_length).decode('utf-8')
    
    return (record_id, client_queue_path)

def send_response(client_queue_path: str, response: str) -> None:
    response_bytes = response.encode('utf-8')
    response_length = len(response_bytes)
    
    message = struct.pack('i', response_length) + response_bytes
    
    try:
        fd = os.open(client_queue_path, os.O_WRONLY)
        os.write(fd, message)
        os.close(fd)
    except OSError as e:
        print(f"Error sending response to {client_queue_path}: {e}")
        raise

def process_request(record_id: int, client_queue_path: str) -> None:
    print(f"Processing request: ID={record_id}, Client queue={client_queue_path}")
    
    print(f"Simulating work delay ({DELAY_SECONDS} seconds)...")
    time.sleep(DELAY_SECONDS)
    
    if record_id in DATABASE:
        response = DATABASE[record_id]
        print(f"Found: {response}")
    else:
        response = "Nie ma"
        print(f"Not found")
    
    send_response(client_queue_path, response)
    print(f"Response sent to client\n")

def main() -> None:
    global shutdown_flag
    
    setup_signal_handlers()
    
    print("Database Server")
    print("=" * 50)
    print("\nDatabase contents:")
    for record_id, surname in DATABASE.items():
        print(f"  {record_id}: {surname}")
    print()
    
    create_server_fifo()
    
    print(f"Server PID: {os.getpid()}")
    print("Server is running. Waiting for requests...")
    print("Send SIGUSR1 to stop the server")
    print("=" * 50)
    print()
    
    try:
        fd = os.open(SERVER_FIFO, os.O_RDONLY | os.O_NONBLOCK)
        
        while not shutdown_flag:
            try:
                os.set_blocking(fd, False)
                
                try:
                    result = read_message(fd)
                    if result is not None:
                        record_id, client_queue_path = result
                        process_request(record_id, client_queue_path)
                except BlockingIOError:
                    time.sleep(0.1)
                    continue
                    
            except Exception as e:
                print(f"Error processing request: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        os.close(fd)
        
    except KeyboardInterrupt:
        print("\n\nServer interrupted by user")
    finally:
        cleanup()
        print("Server stopped")

if __name__ == "__main__":
    main()


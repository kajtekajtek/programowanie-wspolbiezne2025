#!/usr/bin/env python3
import argparse
import os
import time
import sys

LOCKFILE_NAME          = "server.lock"
END_MARKER             = "\x1b"
LOCK_RETRY_INTERVAL    = 2
RESPONSE_POLL_INTERVAL = 0.5
RESPONSE_TIMEOUT       = 60
ENCODING               = "utf-8"

def main():
    args = parse_args()

    try:
        run_client(args.buffer_file, args.response_file)
    except KeyboardInterrupt:
        print("\n\nClient interrupted. Exiting...")
        cleanup_response_file(args.response_file)
        sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Client for text communication system'
    )
    parser.add_argument(
        'buffer_file',
        help='Path to the server buffer file'
    )
    parser.add_argument(
        'response_file',
        help='Path to the client response file'
    )

    return parser.parse_args()

def run_client(buffer_file, response_file):
    cleanup_response_file(response_file)
    
    message_lines = get_user_message()
    
    if not message_lines:
        print("No message entered. Exiting.")
        sys.exit(0)

    wait_for_lock()
    
    send_message(buffer_file, response_file, message_lines)
    
    response = wait_for_response(response_file)
    
    if response:
        print()
        print("Server response:")
        print()
        print(response)
        print()
    else:
        print("Failed to receive response from server", file=sys.stderr)
        sys.exit(1)
    
    cleanup_response_file(response_file)

def get_user_message():
    print("Enter your message (press Ctrl+D or Ctrl+Z when done):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    return lines

def wait_for_lock():
    while not acquire_lock():
        print("Server busy, please wait...")
        time.sleep(LOCK_RETRY_INTERVAL)
    print("\nLock acquired. Sending message to server...")

def acquire_lock():
    try:
        fd = os.open(LOCKFILE_NAME, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        os.close(fd)
        return True
    except FileExistsError: return False
    except Exception as e:
        print(f"Error acquiring lock: {e}", file=sys.stderr)
        return False

def send_message(buffer_file, response_file, message_lines):
    try:
        with open(buffer_file, 'w', encoding=ENCODING) as f:
            f.write(response_file + '\n')
            for line in message_lines:
                f.write(line + '\n')
            f.write(END_MARKER)
        print("Message sent to server.")
    except Exception as e:
        print(f"Error writing to buffer file: {e}", file=sys.stderr)
        sys.exit(1)

def wait_for_response(response_file):
    print("Waiting for server response...")
    
    start_time = time.time()
    while time.time() - start_time < RESPONSE_TIMEOUT:
        if os.path.exists(response_file) and os.path.getsize(response_file) > 0:
            time.sleep(0.1)
            
            try:
                with open(response_file, 'r', encoding=ENCODING) as f:
                    content = f.read()
                
                if END_MARKER in content:
                    content = content.split(END_MARKER)[0]
                
                return content.strip()
            except Exception as e:
                print(f"Error reading response: {e}", file=sys.stderr)
                return None
        
        time.sleep(RESPONSE_POLL_INTERVAL)
    
    print("Timeout waiting for server response", file=sys.stderr)
    return None

def cleanup_response_file(response_file):
    try:
        if os.path.exists(response_file):
            os.remove(response_file)
    except Exception as e:
        print(f"Warning: Could not remove response file: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()

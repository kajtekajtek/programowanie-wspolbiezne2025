#!/usr/bin/env python3
import argparse
import os
import time
import sys

LOCKFILE_NAME = "server.lock"
END_MARKER    = "\x1b"
POLL_INTERVAL = 0.5
ENCODING      = "utf-8"

def main():
    args = parse_args()
    
    try:
        run_server(args.buffer_file)
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")
        if os.path.exists(LOCKFILE_NAME):
            try:
                os.remove(LOCKFILE_NAME)
            except:
                pass
        sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Server for text communication system'
    )
    parser.add_argument(
        'buffer_file',
        help='Path to the server buffer file'
    )
    return parser.parse_args()


def run_server(buffer_file):
    print(f"Server starting...")
    print(f"Buffer file: {buffer_file}")
    print(f"Lockfile: {LOCKFILE_NAME}")
    print(f"Waiting for clients...\n")
    
    while True:
        if os.path.exists(LOCKFILE_NAME):
            time.sleep(0.1)
            
            response_file, message_lines = read_client_message(buffer_file)
            
            if response_file and message_lines is not None:
                print()
                print(f"Message received from client (response file: {response_file})")
                print()
                print('\n'.join(message_lines))
                print()
                
                response = get_server_response()
                
                write_response(response_file, response)
                
                clear_buffer(buffer_file)
                
                try:
                    os.remove(LOCKFILE_NAME)
                    print(f"Lockfile removed. Ready for next client.\n")
                except Exception as e:
                    print(f"Error removing lockfile: {e}", file=sys.stderr)
            else:
                print("Error reading client message", file=sys.stderr)
                try:
                    os.remove(LOCKFILE_NAME)
                except:
                    pass
        
        time.sleep(POLL_INTERVAL)


def read_client_message(buffer_file):
    try:
        with open(buffer_file, 'r', encoding=ENCODING) as f:
            lines = f.read().split('\n')
        
        if not lines:
            return None, None
        
        response_file = lines[0].strip()
        message_lines = []
        
        for line in lines[1:]:
            if END_MARKER in line:
                message_lines.append(line.split(END_MARKER)[0])
                break
            message_lines.append(line)
        
        return response_file, message_lines
    except Exception as e:
        print(f"Error reading buffer file: {e}", file=sys.stderr)
        return None, None


def get_server_response():
    print()
    print("Enter your response (press Ctrl+D or Ctrl+Z when done):")
    print()
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    response = '\n'.join(lines) + '\n' + END_MARKER
    return response


def write_response(response_file, response):
    try:
        with open(response_file, 'w', encoding=ENCODING) as f:
            f.write(response)
        print(f"\nResponse sent to: {response_file}")
    except Exception as e:
        print(f"Error writing response: {e}", file=sys.stderr)


def clear_buffer(buffer_file):
    try:
        with open(buffer_file, 'w', encoding=ENCODING) as f:
            f.write('')
    except Exception as e:
        print(f"Error clearing buffer: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()

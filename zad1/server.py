#!/usr/bin/env python3
import os
import time

DATA_FILE     = "data.txt"
RESULT_FILE   = "result.txt"
POLL_INTERVAL = 0.1

def main():
    print("Server started. Waiting for client requests...")
    
    clear_file(DATA_FILE)
    clear_file(RESULT_FILE)
    
    try:
        while True:
            data = get_data()
            
            if data is not None:
                print(f"Received number: {data}")
                
                result = calculate_result(data)
                print(f"Calculated: f({data}) = {result}")
                
                write_result(result)
                print(f"Result saved to file '{RESULT_FILE}'")
                
                clear_file(DATA_FILE)
                print("File 'data' cleared. Waiting for next request...\n")
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        clear_file(DATA_FILE)
        clear_file(RESULT_FILE)

def clear_file(filename: str) -> None:
    try: write_file(filename, '')
    except IOError: pass

def write_file(filename: str, content: str) -> None:
    with open(filename, 'w') as f: f.write(content)

def get_data() -> int | None:
    if not os.path.exists(DATA_FILE): return None
    try: return int(read_file(DATA_FILE))
    except (ValueError, IOError): return None

def read_file(filename: str) -> str:
    try: 
        with open(filename, 'r') as f:
            content = f.read().strip()
            if content: return content
    except (ValueError, IOError): pass

    return ""

def calculate_result(x: int) -> int: return x**2

def write_result(result: int) -> None:
    write_file(RESULT_FILE, str(result))

if __name__ == "__main__":
    main()


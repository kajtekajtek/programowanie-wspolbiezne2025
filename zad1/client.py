#!/usr/bin/env python3
import os
import time

DATA_FILE     = "data.txt"
RESULT_FILE   = "result.txt"
POLL_INTERVAL = 0.1
TIMEOUT       = 30

def main():
    print("=== Client file communication ===")
    try:
        number_str = input("Enter an integer: ")
        number     = int(number_str)
        
        clear_file(RESULT_FILE)
        
        print(f"Sending number {number} to server...")
        send_integer_to_data_file(number)
        
        print("Waiting for response from server...")
        result = wait_for_result()
        
        if result is not None:
            print(f"\nReceived result: f({number}) = {result}")
            clear_file(RESULT_FILE)
        else:
            print(f"\nTimeout: No response in {TIMEOUT} seconds.")
            print("Check if server is running.")
    
    except ValueError:
        print("Error: check if you entered an integer.")
    except KeyboardInterrupt:
        print("\n\nClient interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")

def clear_file(filename: str) -> None:
    try: write_file(filename, '')
    except IOError: pass

def send_integer_to_data_file(n: int) -> None:
    write_file(DATA_FILE, str(n))

def write_file(filename: str, content: str) -> None:
    with open(filename, 'w') as f: f.write(content)

def wait_for_result() -> int | None:
    start_time = time.time()
    
    while True:
        result = get_result_from_result_file()
        
        if result is not None: return result
        
        if time.time() - start_time > TIMEOUT: return None
        
        time.sleep(POLL_INTERVAL)

def get_result_from_result_file() -> int | None:
    if not os.path.exists(RESULT_FILE): return None
    try: return int(read_file(RESULT_FILE))
    except (ValueError, IOError): return None

def read_file(filename: str) -> str:
    try: 
        with open(filename, 'r') as f:
            content = f.read().strip()
            if content: return content
    except (ValueError, IOError): pass
    
    return ""

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import sys
import re

def count_word_in_file(filename, word):
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist", file=sys.stderr)
        return 0
    
    count = 0
    child_pids = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                included_file = match_input_directive(line)
                if included_file:
                    pid = os.fork()
                    if pid == 0:
                        child_count = count_word_in_file(included_file, word)
                        sys.exit(child_count)
                    else:
                        child_pids.append(pid)
                else:
                    words = re.findall(r'\w+', line.lower())
                    count += words.count(word.lower())
    
    except Exception as e:
        print(f"Błąd podczas przetwarzania pliku {filename}: {e}", file=sys.stderr)
        return count
    
    for pid in child_pids:
        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status)
        count += exit_code
    
    return count

def match_input_directive(line):
    match = re.match(r'^\s*\\input\{(.+?)\}\s*$', line)
    return match.group(1) if match else None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python program.py <nazwa_pliku> <słowo>")
        sys.exit(1)
    
    filename = sys.argv[1]
    word = sys.argv[2]
    
    total_count = count_word_in_file(filename, word)
    
    print(f"Słowo '{word}' wystąpiło {total_count} razy.")


#!/usr/bin/env python3
import threading
import time
from typing import List


def pierwsza(k: int) -> bool:
    if k < 2:
        return False
    for i in range(2, k):
        if i * i > k:
            return True
        if k % i == 0:
            return False
    return True


def find_primes_in_range(start: int, end: int, pierwsze: List[int], lock: threading.Lock, barrier: threading.Barrier) -> None:
    local_primes = []
    
    for i in range(start, end + 1):
        if pierwsza(i):
            local_primes.append(i)
    
    with lock:
        pierwsze.extend(local_primes)
    
    barrier.wait()


def find_primes_multithreaded(l: int, r: int, num_threads: int) -> List[int]:
    pierwsze = []
    lock = threading.Lock()
    barrier = threading.Barrier(num_threads + 1)
    
    range_size = r - l + 1
    chunk_size = range_size // num_threads
    if chunk_size == 0:
        chunk_size = 1
        num_threads = min(num_threads, range_size)
        barrier = threading.Barrier(num_threads + 1)
    
    threads = []
    
    for i in range(num_threads):
        start = l + i * chunk_size
        if i == num_threads - 1:
            end = r
        else:
            end = l + (i + 1) * chunk_size - 1
        
        thread = threading.Thread(
            target=find_primes_in_range,
            args=(start, end, pierwsze, lock, barrier)
        )
        threads.append(thread)
        thread.start()
    
    barrier.wait()
    
    for thread in threads:
        thread.join()
    
    return sorted(pierwsze)


def main():
    print("=== Przykład z polecenia ===")
    l = 2
    r = 20
    num_threads = 3
    
    pierwsze = find_primes_multithreaded(l, r, num_threads)
    
    print(f"l = {l}, r = {r}")
    print(f"Liczba wątków: {num_threads}")
    print(f"Liczby pierwsze: {pierwsze}")
    
    expected = [2, 3, 5, 7, 11, 13, 17, 19]
    assert sorted(pierwsze) == expected, f"Błąd! Oczekiwano {expected}, otrzymano {pierwsze}"
    
    print("\n=== Przykład z większym zakresem ===")
    l = 2
    r = 1000
    num_threads = 4
    
    print(f"Szukanie liczb pierwszych w zakresie [{l}, {r}] z {num_threads} wątkami...")
    start_time = time.time()
    pierwsze = find_primes_multithreaded(l, r, num_threads)
    end_time = time.time()
    
    elapsed = end_time - start_time
    print(f"Czas wykonania: {elapsed:.4f} sekund")
    print(f"Znaleziono {len(pierwsze)} liczb pierwszych")
    print(f"Pierwsze 10: {pierwsze[:10]}")
    print(f"Ostatnie 10: {pierwsze[-10:]}")
    
    for threads in [1, 2, 4, 8]:
        print(f"\nTest z {threads} wątkami:")
        start_time = time.time()
        pierwsze = find_primes_multithreaded(l, r, threads)
        end_time = time.time()
        
        elapsed = end_time - start_time
        print(f"Czas wykonania: {elapsed:.4f} sekund")
        print(f"Znaleziono {len(pierwsze)} liczb pierwszych")


if __name__ == "__main__":
    main()


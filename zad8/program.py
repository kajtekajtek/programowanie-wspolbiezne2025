#!/usr/bin/env python3
import threading
import random
import time
from typing import List


def count_in_chunk(chunk: List[int], N: int, counts: List[int], lock: threading.Lock) -> None:
    local_counts = [0] * N
    
    for num in chunk:
        if 0 <= num < N:
            local_counts[num] += 1
    
    with lock:
        for i in range(N):
            counts[i] += local_counts[i]


def count_occurrences_multithreaded(L: List[int], N: int, num_threads: int) -> List[int]:
    counts = [0] * N
    
    lock = threading.Lock()
    
    chunk_size = len(L) // num_threads
    if chunk_size == 0:
        chunk_size = 1
        num_threads = min(num_threads, len(L))
    
    threads = []
    
    for i in range(num_threads):
        start_idx = i * chunk_size
        if i == num_threads - 1:
            end_idx = len(L)
        else:
            end_idx = (i + 1) * chunk_size
        
        chunk = L[start_idx:end_idx]
        
        thread = threading.Thread(
            target=count_in_chunk,
            args=(chunk, N, counts, lock)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return counts


def main():
    print("=== Przykład z polecenia ===")
    N = 3
    L = [2, 0, 1, 2, 1, 1, 1]
    num_threads = 2
    
    licz = count_occurrences_multithreaded(L, N, num_threads)
    
    print(f"N = {N}")
    print(f"L = {L}")
    print(f"Liczba wątków: {num_threads}")
    print("\nWyniki:")
    for i in range(N):
        print(f"licz[{i}] = {licz[i]}")
    
    expected = [1, 4, 2]
    assert licz == expected, f"Błąd! Oczekiwano {expected}, otrzymano {licz}"
    
    print("\n=== Przykład z większą listą ===")
    N = 20
    list_size = 1000000
    
    print(f"Generowanie listy o rozmiarze {list_size}...")
    L = [random.randint(0, N - 1) for _ in range(list_size)]
    
    for threads in [1, 2, 4, 8]:
        print(f"\nTest z {threads} wątkami:")
        start_time = time.time()
        licz = count_occurrences_multithreaded(L, N, threads)
        end_time = time.time()
        
        elapsed = end_time - start_time
        print(f"Czas wykonania: {elapsed:.4f} sekund")
        
        total = sum(licz)
        assert total == list_size, f"Błąd! Suma liczników ({total}) != rozmiar listy ({list_size})"
        print(f"Suma liczników: {total} (poprawna)")
        
        print(f"Przykładowe liczniki: licz[0]={licz[0]}, licz[1]={licz[1]}, licz[2]={licz[2]}")


if __name__ == "__main__":
    main()


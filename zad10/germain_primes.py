#!/usr/bin/env python3
import time
import math
import multiprocessing
from typing import List, Tuple


def is_prime(k: int) -> bool:
    if k < 2:
        return False
    if k == 2:
        return True
    if k % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(k)) + 1, 2):
        if k % i == 0:
            return False
    return True


def is_prime_optimized(k: int, small_primes: List[int]) -> bool:
    if k < 2:
        return False
    for p in small_primes:
        if p * p > k:
            return True
        if k % p == 0:
            return False
    return True


def find_small_primes(max_value: int) -> List[int]:
    """Create a list of small primes up to sqrt(max_value)"""
    small_primes = []
    s = math.ceil(math.sqrt(max_value))
    for i in range(2, s + 1):
        if is_prime(i):
            small_primes.append(i)
    return small_primes


def find_primes_in_range(l: int, r: int, small_primes: List[int]) -> List[int]:
    """Find primes in range [l, r] using small_primes"""
    primes = []
    for i in range(l, r + 1):
        if is_prime_optimized(i, small_primes):
            primes.append(i)
    return primes


def find_germain_sequential(l: int, r: int) -> List[int]:
    """
    Sequential finding of Germain primes in range [l, r]
    A Germain prime is a prime p such that 2p+1 is also prime
    """
    max_check = 2 * r + 1
    
    small_primes = find_small_primes(max_check)
    
    primes = find_primes_in_range(l, r, small_primes)
    
    germain_primes = []
    for p in primes:
        if 2 * p + 1 <= max_check:
            if is_prime_optimized(2 * p + 1, small_primes):
                germain_primes.append(p)
    
    return germain_primes


def find_germain_in_chunk(args: Tuple[int, int, List[int], int]) -> List[int]:
    chunk_start, chunk_end, small_primes, max_check = args
    germain_primes = []
    
    primes = []
    for i in range(chunk_start, chunk_end):
        if is_prime_optimized(i, small_primes):
            primes.append(i)
    
    for p in primes:
        if 2 * p + 1 <= max_check:
            if is_prime_optimized(2 * p + 1, small_primes):
                germain_primes.append(p)
    
    return germain_primes


def find_germain_parallel(l: int, r: int, num_processes: int = None) -> List[int]:
    """
    Parallel finding of Germain primes in range [l, r]
    using multiprocessing.Pool
    """
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    max_check = 2 * r + 1
    
    small_primes = find_small_primes(max_check)
    
    range_size = r - l + 1
    chunk_size = max(1, range_size // num_processes)
    
    chunks = []
    for i in range(num_processes):
        chunk_start = l + i * chunk_size
        if i == num_processes - 1:
            chunk_end = r + 1
        else:
            chunk_end = l + (i + 1) * chunk_size
        chunks.append((chunk_start, chunk_end, small_primes, max_check))
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(find_germain_in_chunk, chunks)
    
    germain_primes = []
    for result in results:
        germain_primes.extend(result)
    
    return sorted(germain_primes)


def main():
    """Main function with performance tests"""
    print("=" * 70)
    print("Finding Germain Primes")
    print("=" * 70)
    
    print("\n--- Verification test (small range) ---")
    l_test = 2
    r_test = 100
    
    print(f"Range: [{l_test}, {r_test}]")
    
    start = time.time()
    germain_seq = find_germain_sequential(l_test, r_test)
    time_seq = time.time() - start
    
    start = time.time()
    germain_par = find_germain_parallel(l_test, r_test, num_processes=2)
    time_par = time.time() - start
    
    print(f"Sequential: found {len(germain_seq)} Germain primes in {time_seq:.4f}s")
    print(f"Parallel (2 processes): found {len(germain_par)} Germain primes in {time_par:.4f}s")
    print(f"Germain primes: {germain_seq}")
    
    if sorted(germain_seq) == sorted(germain_par):
        print("Results match!")
    else:
        print("Error: results don't match!")
        print(f"  Sequential: {germain_seq}")
        print(f"  Parallel: {germain_par}")
    
    print("\n" + "=" * 70)
    print("Performance tests on large data")
    print("=" * 70)
    
    l = 1000000
    r = 2000000
    
    print(f"\nRange: [{l}, {r}]")
    print(f"Number of available CPUs: {multiprocessing.cpu_count()}")
    
    print("\n--- Sequential version ---")
    start = time.time()
    germain_seq = find_germain_sequential(l, r)
    time_seq = time.time() - start
    print(f"Time: {time_seq:.4f} seconds")
    print(f"Found {len(germain_seq)} Germain primes")
    if len(germain_seq) > 0:
        print(f"Examples: {germain_seq[:5]} ... {germain_seq[-5:]}")
    
    print("\n--- Parallel versions ---")
    for num_proc in [2, 4, 8]:
        if num_proc > multiprocessing.cpu_count():
            continue
        print(f"\n{num_proc} processes:")
        start = time.time()
        germain_par = find_germain_parallel(l, r, num_processes=num_proc)
        time_par = time.time() - start
        speedup = time_seq / time_par if time_par > 0 else 0
        print(f"  Time: {time_par:.4f} seconds")
        print(f"  Found {len(germain_par)} Germain primes")
        print(f"  Speedup: {speedup:.2f}x")
        
        if sorted(germain_seq) == sorted(germain_par):
            print(f"  Correctness: OK")
        else:
            print(f"  Error: results don't match!")
    
    print(f"\nAutomatic number of processes ({multiprocessing.cpu_count()}):")
    start = time.time()
    germain_par = find_germain_parallel(l, r)
    time_par = time.time() - start
    speedup = time_seq / time_par if time_par > 0 else 0
    print(f"  Time: {time_par:.4f} seconds")
    print(f"  Speedup: {speedup:.2f}x")


if __name__ == '__main__':
    main()


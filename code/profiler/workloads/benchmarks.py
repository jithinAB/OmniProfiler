"""
Benchmark Algorithms Suite

Pre-built algorithms with known complexity characteristics
for testing profiler capabilities.
"""

import time
import random
from typing import List, Any


class Benchmarks:
    """Collection of benchmark algorithms at different complexities"""

    # ===== O(n) - Linear Time =====

    @staticmethod
    def linear_sum(data: List[int]) -> int:
        """
        O(n) - Sum all elements

        Best case for algorithms - scales linearly
        """
        total = 0
        for item in data:
            total += item
        return total

    @staticmethod
    def linear_search(data: List[int], target: int) -> int:
        """
        O(n) - Linear search for element

        Returns index or -1 if not found
        """
        for i, item in enumerate(data):
            if item == target:
                return i
        return -1

    @staticmethod
    def linear_filter(data: List[int], threshold: int = 500) -> List[int]:
        """
        O(n) - Filter elements above threshold
        """
        return [x for x in data if x > threshold]

    # ===== O(n log n) - Linearithmic Time =====

    @staticmethod
    def merge_sort(data: List[int]) -> List[int]:
        """
        O(n log n) - Merge sort implementation

        Efficient sorting algorithm
        """
        if len(data) <= 1:
            return data

        mid = len(data) // 2
        left = Benchmarks.merge_sort(data[:mid])
        right = Benchmarks.merge_sort(data[mid:])

        # Merge
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])

        return result

    @staticmethod
    def quicksort(data: List[int]) -> List[int]:
        """
        O(n log n) average - Quicksort implementation

        Can degrade to O(n²) with bad pivots
        """
        if len(data) <= 1:
            return data

        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]

        return Benchmarks.quicksort(left) + middle + Benchmarks.quicksort(right)

    # ===== O(n²) - Quadratic Time =====

    @staticmethod
    def bubble_sort(data: List[int]) -> List[int]:
        """
        O(n²) - Bubble sort (inefficient!)

        Demonstrates quadratic scaling - very slow for large datasets
        """
        arr = data.copy()
        n = len(arr)

        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

        return arr

    @staticmethod
    def nested_loop_sum(data: List[int]) -> int:
        """
        O(n²) - Nested loop computation

        Classic quadratic bottleneck
        """
        total = 0
        for i in data:
            for j in data:
                total += i * j
        return total

    @staticmethod
    def pairwise_distance(data: List[int]) -> List[tuple]:
        """
        O(n²) - Calculate all pairwise differences

        Common in distance/similarity computations
        """
        distances = []
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                dist = abs(data[i] - data[j])
                distances.append((i, j, dist))
        return distances

    # ===== O(n³) - Cubic Time =====

    @staticmethod
    def matrix_multiply_naive(matrix_a: List[List[float]],
                              matrix_b: List[List[float]]) -> List[List[float]]:
        """
        O(n³) - Naive matrix multiplication

        Very slow for large matrices
        """
        n = len(matrix_a)
        result = [[0.0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]

        return result

    @staticmethod
    def triple_nested_loop(data: List[int]) -> int:
        """
        O(n³) - Three nested loops

        Extremely inefficient - only works for small data
        """
        total = 0
        for i in data:
            for j in data:
                for k in data:
                    total += i + j + k
        return total

    # ===== O(2^n) - Exponential Time =====

    @staticmethod
    def fibonacci_recursive(n: int) -> int:
        """
        O(2^n) - Naive recursive Fibonacci

        EXTREMELY slow - only use with n < 30!
        Demonstrates exponential explosion
        """
        if n <= 1:
            return n
        return Benchmarks.fibonacci_recursive(n - 1) + Benchmarks.fibonacci_recursive(n - 2)

    @staticmethod
    def fibonacci_optimized(n: int) -> int:
        """
        O(n) - Optimized iterative Fibonacci

        Shows the impact of algorithm choice
        """
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b

        return b

    # ===== Memory-Intensive Benchmarks =====

    @staticmethod
    def memory_intensive_copy(data: List[Any], num_copies: int = 100) -> List[List[Any]]:
        """
        Memory-intensive operation - creates multiple copies

        Tests peak memory usage
        """
        copies = []
        for _ in range(num_copies):
            copies.append(data.copy())
        return copies

    @staticmethod
    def memory_accumulation(size: int) -> List[List[int]]:
        """
        Gradually accumulates memory

        Tests memory growth patterns
        """
        accumulated = []
        for i in range(size):
            accumulated.append(list(range(i)))
        return accumulated

    # ===== I/O-Intensive Benchmarks =====

    @staticmethod
    def simulated_io_operations(data: List[str], delay_ms: float = 0.001) -> List[str]:
        """
        Simulates I/O-bound operations

        Uses sleep to simulate I/O latency
        """
        results = []
        for item in data:
            time.sleep(delay_ms / 1000)  # Simulate I/O delay
            results.append(item.upper())  # Simulate processing
        return results

    # ===== CPU-Intensive Benchmarks =====

    @staticmethod
    def cpu_intensive_computation(data: List[int]) -> List[float]:
        """
        CPU-intensive mathematical operations

        Pure computation, minimal memory
        """
        results = []
        for x in data:
            # Complex computation
            result = sum(x ** (1 / n) for n in range(1, 10))
            results.append(result)
        return results

    # ===== Mixed Workload =====

    @staticmethod
    def mixed_workload(data: List[int]) -> dict:
        """
        Mixed CPU, memory, and logic operations

        Realistic workload simulation
        """
        # CPU phase
        squares = [x ** 2 for x in data]

        # Memory phase
        sorted_data = sorted(data)

        # Logic phase
        filtered = [x for x in sorted_data if x % 2 == 0]

        # Aggregation
        return {
            'sum': sum(filtered),
            'count': len(filtered),
            'max': max(filtered) if filtered else 0,
            'squares_sample': squares[:10]
        }


class BenchmarkSuite:
    """Helper class for running benchmark suites"""

    COMPLEXITY_CLASSES = {
        'O(n)': [
            Benchmarks.linear_sum,
            Benchmarks.linear_search,
            Benchmarks.linear_filter
        ],
        'O(n log n)': [
            Benchmarks.merge_sort,
            Benchmarks.quicksort
        ],
        'O(n²)': [
            Benchmarks.bubble_sort,
            Benchmarks.nested_loop_sum,
            Benchmarks.pairwise_distance
        ],
        'O(n³)': [
            Benchmarks.triple_nested_loop
        ],
        'Special': [
            Benchmarks.memory_intensive_copy,
            Benchmarks.cpu_intensive_computation,
            Benchmarks.mixed_workload
        ]
    }

    @classmethod
    def list_benchmarks(cls) -> dict:
        """Get all available benchmarks organized by complexity"""
        result = {}
        for complexity, funcs in cls.COMPLEXITY_CLASSES.items():
            result[complexity] = [f.__name__ for f in funcs]
        return result

    @classmethod
    def get_benchmark(cls, name: str):
        """Get benchmark function by name"""
        for funcs in cls.COMPLEXITY_CLASSES.values():
            for func in funcs:
                if func.__name__ == name:
                    return func
        raise ValueError(f"Unknown benchmark: {name}")

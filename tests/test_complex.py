#!/usr/bin/env python3
"""
Test script with measurable CPU/memory activity for Scalene
"""
import time

def python_computation():
    """Pure Python - should show in Python CPU"""
    result = 0
    for i in range(500000):
        result += i ** 2
    return result

def system_calls():
    """System calls - should show in System CPU"""
    time.sleep(0.1)
    return "done"

def memory_operations():
    """Memory allocation"""
    data = []
    for i in range(50000):
        data.append([i] * 10)
    return len(data)

def main():
    print("Python computation:", python_computation())
    print("System calls:", system_calls())
    print("Memory ops:", memory_operations())

if __name__ == "__main__":
    main()

import time
import sys

def cpu_intensive():
    """Pure Python CPU-intensive function"""
    result = 0
    for i in range(1000000):
        result += i ** 2
    return result

def sleep_function():
    """System call heavy function"""
    time.sleep(0.1)
    return "done"

def memory_allocator():
    """Memory allocation test"""
    data = []
    for i in range(10000):
        data.append([i] * 100)
    return len(data)

def main():
    print("Testing CPU intensive...")
    cpu_intensive()
    
    print("Testing sleep...")
    sleep_function()
    
    print("Testing memory...")
    memory_allocator()
    
    print("All tests complete!")

if __name__ == "__main__":
    main()

import numpy as np
import time

def numpy_heavy():
    """Function with heavy native code usage"""
    arr = np.random.rand(1000, 1000)
    result = np.dot(arr, arr)
    return result.sum()

def python_heavy():
    """Pure Python computation"""
    total = 0
    for i in range(100000):
        total += i ** 2
    return total

def io_heavy():
    """I/O heavy function"""
    time.sleep(0.05)
    return "done"

if __name__ == "__main__":
    print("NumPy:", numpy_heavy())
    print("Python:", python_heavy())
    print("I/O:", io_heavy())

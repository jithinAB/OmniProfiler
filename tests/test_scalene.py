import time
import numpy as np

def heavy_computation():
    arr = np.random.rand(1000, 1000)
    time.sleep(0.1)
    return np.dot(arr, arr)

def main():
    heavy_computation()

if __name__ == '__main__':
    main()

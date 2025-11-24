import tracemalloc

# Simple test to verify tracemalloc works with exec
tracemalloc.start()

code = """
# Allocate 10MB
data = [i for i in range(100000)]
big_data = b'a' * 10 * 1024 * 1024
"""

print("Before exec:")
print(f"  Memory: {tracemalloc.get_traced_memory()}")

exec(code)

print("After exec:")
current, peak = tracemalloc.get_traced_memory()
print(f"  Memory: current={current}, peak={peak}")
print(f"  Peak MB: {peak / 1024 / 1024:.2f}")

tracemalloc.stop()

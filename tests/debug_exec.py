import inspect

code = """
import time
from math import sqrt

def my_func():
    pass
"""

namespace = {}
exec(code, namespace)

print("Items in namespace:")
for name, obj in namespace.items():
    if name == "__builtins__": continue
    print(f"Name: {name}, Callable: {callable(obj)}")
    if callable(obj):
        print(f"  Module: {getattr(obj, '__module__', 'N/A')}")
        try:
            print(f"  Source: {inspect.getsource(obj)}")
        except:
            print("  Source: N/A")

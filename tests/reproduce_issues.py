import sys
import os
import json
import psutil
from code.profiler.orchestrator import Orchestrator
from code.profiler.hardware import HardwareDetector

def test_function():
    # Simulate some work
    x = []
    for i in range(10000):
        x.append(i)
    
    # Allocate 10MB to ensure tracemalloc catches it
    y = b'a' * 10 * 1024 * 1024
    return len(x) + len(y)

def reproduce():
    print(f"PSUtil Version: {psutil.__version__}")
    
    # Test Hardware Detection directly
    print("\n--- Testing Hardware Detection ---")
    detector = HardwareDetector()
    hw_info = detector.detect()
    print(f"Hardware Info Object: {hw_info}")
    print(f"Hardware Info Dict: {hw_info.__dict__}")

    orchestrator = Orchestrator()
    
    # Profile the test function
    print("\n--- Profiling test function ---")
    result = orchestrator.profile_function(test_function)
    
    # Print key metrics to check for reported issues
    print("\n--- Analysis Results ---")
    
    # Check Memory
    memory = result.get('dynamic_analysis', {}).get('memory', {})
    print(f"Memory Peak: {memory.get('peak_memory')}")
    print(f"Memory Current: {memory.get('current_memory')}")
    
    # Check Context Switches (CPU metrics)
    cpu = result.get('dynamic_analysis', {}).get('cpu', {})
    print(f"Context Switches: {cpu.get('context_switches')}")
    
    # Check Call Tree
    call_tree = result.get('dynamic_analysis', {}).get('call_tree')
    print(f"Call Tree Present: {bool(call_tree)}")
    if call_tree:
        try:
            tree_json = json.loads(call_tree)
            print(f"Call Tree JSON Valid: True")
            # Check if it has expected structure
            root = tree_json.get('root_frame') or tree_json
            print(f"Root Function: {root.get('function')}")
        except json.JSONDecodeError:
            print(f"Call Tree JSON Valid: False (Raw length: {len(call_tree)})")
    
    # Check Hardware (correct key)
    hardware = result.get('hardware', {})
    print(f"Hardware Info (from result): {json.dumps(hardware, indent=2)}")

    # Dump full JSON for inspection if needed
    with open('debug_profile_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\nFull result saved to debug_profile_result.json")

if __name__ == "__main__":
    # Add the current directory to sys.path so we can import code
    sys.path.append(os.getcwd())
    reproduce()

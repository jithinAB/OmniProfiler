#!/usr/bin/env python3
"""Test the full orchestrator flow"""
import sys
import json
import tempfile
import os
sys.path.insert(0, '/Users/jithinvg/Desktop/vlad-bud')

from code.profiler.orchestrator import Orchestrator

# Create a temp file with test code
test_code = """print(42)"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    temp_file = f.name

try:
    print(f"Testing orchestrator.profile_file with: {temp_file}\n")
    
    orchestrator = Orchestrator()
    result = orchestrator.profile_file(temp_file)
    
    print(f"✅ Orchestrator returned result")
    print(f"   Keys: {list(result.keys())}")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(result)
        print(f"✅ Full result is JSON serializable")
        print(f"   Size: {len(json_str)} bytes")
        
        # Parse it back to verify
        parsed = json.loads(json_str)
        print(f"✅ JSON round-trip successful")
        
    except Exception as e:
        print(f"❌ JSON serialization FAILED: {e}")
        print(f"\nTesting each top-level key...")
        for key, value in result.items():
            try:
                json.dumps({key: value})
                print(f"   ✅ {key}: OK")
            except Exception as field_error:
                print(f"   ❌ {key}: FAILED - {field_error}")
                
                # Dig deeper if it's a dict
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        try:
                            json.dumps({subkey: subvalue})
                        except Exception as sub_error:
                            print(f"      ❌ {key}.{subkey}: {type(subvalue)} - {sub_error}")
                            
finally:
    os.unlink(temp_file)

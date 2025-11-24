#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/jithinvg/Desktop/vlad-bud')

from code.profiler.orchestrator import Orchestrator
import json

# Test profiling
orchestrator = Orchestrator()
result = orchestrator.profile_code("print(42)")

# Try to serialize
try:
    json_str = json.dumps(result)
    print("✅ JSON serialization SUCCESS")
    print(f"✅ Has GC: {'gc' in result.get('dynamic_analysis', {})}")
    print(f"✅ Has CPU: {'cpu' in result.get('dynamic_analysis', {})}")
    print(f"✅ Has Allocations: {'allocations' in result.get('dynamic_analysis', {})}")
except Exception as e:
    print(f"❌ JSON serialization FAILED: {e}")
    print(f"Error type: {type(e)}")
    
    # Find the problematic field
    for key, value in result.get('dynamic_analysis', {}).items():
        try:
            json.dumps({key: value})
        except Exception as field_error:
            print(f"❌ Problem in field '{key}': {field_error}")

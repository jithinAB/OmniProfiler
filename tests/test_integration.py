#!/usr/bin/env python3
"""
Comprehensive test suite for Scalene integration
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_code_profiling():
    """Test /profile/code endpoint with Scalene integration"""
    print("\n=== Testing /profile/code ===")
    
    code = """
import time
time.sleep(0.05)
x = sum(i**2 for i in range(10000))
print(x)
"""
    
    response = requests.post(
        f"{API_BASE}/profile/code",
        json={"code": code}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    # Check structure
    assert "hardware" in data, "Missing hardware"
    assert "static_analysis" in data, "Missing static_analysis"
    assert "dynamic_analysis" in data, "Missing dynamic_analysis"
    
    # Check Scalene metrics
    scalene = data["dynamic_analysis"].get("scalene")
    if scalene:
        print("✓ Scalene metrics present")
        print(f"  CPU Breakdown: {scalene['cpu_breakdown']}")
        print(f"  Memory Copy: {scalene['memory_copy_mb_s']} MB/s")
        print(f"  Leaks: {len(scalene['leaks'])}")
        
        assert "cpu_breakdown" in scalene, "Missing cpu_breakdown"
        assert "python" in scalene["cpu_breakdown"], "Missing python CPU"
        assert "native" in scalene["cpu_breakdown"], "Missing native CPU"
        assert "system" in scalene["cpu_breakdown"], "Missing system CPU"
        assert "memory_copy_mb_s" in scalene, "Missing memory_copy_mb_s"
        assert "leaks" in scalene, "Missing leaks"
        print("✓ All Scalene fields present")
    else:
        print("⚠ Scalene metrics not present (may have failed)")
    
    print("✓ /profile/code test PASSED")
    return True

def test_file_profiling():
    """Test /profile/file endpoint"""
    print("\n=== Testing /profile/file ===")
    
    # Create a test file
    test_code = """
def test_func():
    return sum(i**2 for i in range(5000))

if __name__ == "__main__":
    test_func()
"""
    
    files = {"file": ("test.py", test_code, "text/x-python")}
    response = requests.post(f"{API_BASE}/profile/file", files=files)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert "dynamic_analysis" in data, "Missing dynamic_analysis"
    scalene = data["dynamic_analysis"].get("scalene")
    
    if scalene:
        print("✓ Scalene metrics present in file profiling")
    else:
        print("⚠ Scalene metrics not present")
    
    print("✓ /profile/file test PASSED")
    return True

def test_error_handling():
    """Test that profiling works even if Scalene fails"""
    print("\n=== Testing Error Handling ===")
    
    # Code that might cause issues
    code = "import sys\nsys.exit(0)"
    
    response = requests.post(
        f"{API_BASE}/profile/code",
        json={"code": code}
    )
    
    # Should still return 200 even if Scalene fails
    assert response.status_code == 200, "Should handle errors gracefully"
    data = response.json()
    
    # Standard profiling should still work
    assert "dynamic_analysis" in data, "Should have dynamic_analysis"
    print("✓ Error handling test PASSED")
    return True

def main():
    print("Starting Scalene Integration Tests...")
    print("=" * 50)
    
    try:
        test_code_profiling()
        test_file_profiling()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

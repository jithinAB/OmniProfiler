import requests
import json

# Read the test_warmup.py content
with open("test_warmup.py", "r") as f:
    code = f.read()

url = "http://localhost:8000/profile/code"
headers = {"Content-Type": "application/json"}

# Test with 0 warm-up runs (should be slow/cold)
print("\n--- Testing with 0 warm-up runs ---")
data_cold = {
    "code": code,
    "warmup_runs": 0
}
try:
    response = requests.post(url, headers=headers, json=data_cold)
    if response.status_code == 200:
        result = response.json()
        print("Success!")
        # Check stdout to see if it says "Cold start"
        stdout = result.get("dynamic_analysis", {}).get("stdout", "")
        print(f"Output: {stdout.strip()}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")

# Reset flag
import os
if os.path.exists("/tmp/warmup_test_flag"):
    os.remove("/tmp/warmup_test_flag")

# Test with 1 warm-up run (should be fast/warm)
print("\n--- Testing with 1 warm-up run ---")
data_warm = {
    "code": code,
    "warmup_runs": 1
}
try:
    response = requests.post(url, headers=headers, json=data_warm)
    if response.status_code == 200:
        result = response.json()
        print("Success!")
        # Check stdout to see if it says "Warm start"
        # The profiled run happens AFTER warm-up, so it should see the flag created by warm-up
        stdout = result.get("dynamic_analysis", {}).get("stdout", "")
        print(f"Output: {stdout.strip()}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")

print("\n=== Memory Metrics ===")
memory = result.get('dynamic_analysis', {}).get('memory', {})
print(f"Peak Memory: {memory.get('peak_memory')}")
print(f"Current Memory: {memory.get('current_memory')}")

print("\n=== CPU Metrics ===")
cpu = result.get('dynamic_analysis', {}).get('cpu', {})
print(f"CPU: {json.dumps(cpu, indent=2)}")

print("\n=== Hardware ===")
hardware = result.get('hardware', {})
print(f"Hardware: {json.dumps(hardware, indent=2)}")

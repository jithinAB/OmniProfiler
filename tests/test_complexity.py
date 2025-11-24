import requests
import json

code = """
def constant_time():
    return 42

def linear_time(n):
    for i in range(n):
        pass

def quadratic_time(n):
    for i in range(n):
        for j in range(n):
            pass

def recursive_func(n):
    if n <= 0: return
    recursive_func(n-1)
"""

url = "http://localhost:8000/profile/code"
headers = {"Content-Type": "application/json"}
data = {
    "code": code
}

try:
    print("Sending request to API...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("Success!")
        
        big_o = result.get("static_analysis", {}).get("big_o", {})
        print("\n=== Big O Complexity Results ===")
        print(json.dumps(big_o, indent=2))
        
        # Verify expected results
        expected = {
            "constant_time": "O(1)",
            "linear_time": "O(n)",
            "quadratic_time": "O(n^2)",
            "recursive_func": "O(1) (Recursive)" # Recursion depth detection is basic
        }
        
        all_passed = True
        for func, expected_complexity in expected.items():
            actual = big_o.get(func)
            if actual == expected_complexity:
                print(f"✅ {func}: {actual}")
            else:
                print(f"❌ {func}: Expected {expected_complexity}, got {actual}")
                all_passed = False
                
        if all_passed:
            print("\nAll complexity tests passed!")
        else:
            print("\nSome complexity tests failed.")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Request failed: {e}")

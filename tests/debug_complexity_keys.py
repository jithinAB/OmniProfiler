import requests
import json

code = """
import time

def my_function(n):
    time.sleep(0.01)
    for i in range(n):
        pass

class MyClass:
    def my_method(self, n):
        time.sleep(0.01)
        for i in range(n):
            for j in range(n):
                pass

def main():
    my_function(10)
    obj = MyClass()
    obj.my_method(5)

main()
"""

url = "http://localhost:8000/profile/code"
headers = {"Content-Type": "application/json"}
data = {
    "code": code
}

try:
    print("Sending request...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        big_o = result.get("static_analysis", {}).get("big_o", {})
        print("\n=== Big O Keys ===")
        for k in big_o.keys():
            print(f"'{k}'")
            
        call_tree = result.get("dynamic_analysis", {}).get("call_tree", "")
        if call_tree:
            tree_data = json.loads(call_tree)
            print("\n=== Call Tree Functions ===")
            
            def print_functions(node):
                if not node: return
                print(f"'{node.get('function')}'")
                for child in node.get('children', []):
                    print_functions(child)
            
            # Handle root frame
            root = tree_data.get('root_frame', tree_data)
            print_functions(root)
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Request failed: {e}")

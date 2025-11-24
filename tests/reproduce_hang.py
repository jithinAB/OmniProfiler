import threading
import time

def blocking_code():
    namespace = {}
    code = "x = input('Enter something: ')"
    try:
        exec(code, namespace)
    except Exception as e:
        print(f"Caught expected error: {e}")

# Run in a thread so we don't hang the test runner forever
t = threading.Thread(target=blocking_code)
t.start()
time.sleep(1)
if t.is_alive():
    print("Thread is still running (blocked on input)")
    # We can't easily kill the thread, but we confirmed the behavior
else:
    print("Thread finished (unexpected)")

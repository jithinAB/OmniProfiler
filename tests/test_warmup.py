import time
import os

# Simulate a "cold start" vs "warm" execution
# We'll use a file-based flag to detect if this is the first run

FLAG_FILE = "/tmp/warmup_test_flag"

def expensive_initialization():
    # Simulate expensive one-time setup (e.g. loading models, heavy imports)
    time.sleep(1.0)

def normal_operation():
    # Fast operation
    time.sleep(0.1)

if not os.path.exists(FLAG_FILE):
    # First run (Cold)
    with open(FLAG_FILE, "w") as f:
        f.write("warmed_up")
    print("Cold start: initializing...")
    expensive_initialization()
else:
    # Subsequent runs (Warm)
    print("Warm start: skipping initialization...")

normal_operation()
print("Done.")

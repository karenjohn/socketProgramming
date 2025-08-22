import subprocess
import threading
import sys
import time

# Define paths to the script files
TRACKER_SCRIPT = "Tracker.py"
SEEDER_SCRIPT = "Seeder.py"
LEECHER_SCRIPT = "leecher.py"

# Function to dynamically find the correct Python interpreter
def get_python_executable():
    return sys.executable  # Automatically detects the Python version running this script

# Function to start a script in a separate process and print its output in real-time
def run_script(script_name):
    python_cmd = get_python_executable()
    process = subprocess.Popen(
        [python_cmd, script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Read output in real-time
    def print_output(stream, prefix):
        for line in stream:
            print(f"{prefix} {line}", end="")  # Print each line with a prefix

    # Start threads to capture stdout and stderr separately
    stdout_thread = threading.Thread(target=print_output, args=(process.stdout, f"[{script_name} OUTPUT]"))
    stderr_thread = threading.Thread(target=print_output, args=(process.stderr, f"[{script_name} ERROR]"))

    stdout_thread.start()
    stderr_thread.start()

    return process  # Return the process so we can wait for it later

# Start the tracker first
print("Starting Tracker...")
tracker_process = run_script(TRACKER_SCRIPT)
time.sleep(2)  # Wait for the tracker to initialize

# Start the seeder
print("Starting Seeder...")
seeder_process = run_script(SEEDER_SCRIPT)
time.sleep(5)  # Give the Seeder extra time before the Leecher starts

# Start the leecher
print("Starting Leecher...")
leecher_process = run_script(LEECHER_SCRIPT)

# Wait for processes to finish
tracker_process.wait()
seeder_process.wait()
leecher_process.wait()

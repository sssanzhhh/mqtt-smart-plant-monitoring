import subprocess
import time
import sys

# List of all Danial modules
scripts = [
    "controller_ph.py",
    "controller_salinity.py",
    "controller_root_temp.py",
    "publisher_ph.py",
    "publisher_salinity.py",
    "publisher_root_temp.py",
]

processes = []


def start_script(script):
    print(f"Starting {script}...")
    try:
        return subprocess.Popen([sys.executable, script])
    except Exception as e:
        print(f"Failed to start {script}: {e}")
        return None


def main():
    print("=== Danial Sensor System Starting ===\n")

    # Start controllers first
    for script in scripts[:3]:
        process = start_script(script)
        if process:
            processes.append(process)
        time.sleep(1)

    print("\n--- Controllers started ---\n")

    # Start publishers
    for script in scripts[3:]:
        process = start_script(script)
        if process:
            processes.append(process)
        time.sleep(1)

    print("\n--- Publishers started ---\n")
    print("System is running... Press CTRL+C to stop\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all processes...")

        for p in processes:
            if p:
                p.terminate()

        print("All processes stopped.")


if __name__ == "__main__":
    main()
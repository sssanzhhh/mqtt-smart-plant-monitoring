import importlib.util
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

PLANT_TYPES = ["ficus", "cactus"]

CONTROLLERS = [
    "controller_moisture.py",
    "controller_temp.py",
    "controller_humidity.py",
    "controller_nitrogen.py",
    "controller_phosphorus.py",
    "controller_potassium.py",
    "controller_ph.py",
    "controller_salinity.py",
    "controller_root_temp.py",
]

PUBLISHERS = [
    "publisher_moisture.py",
    "publisher_temp.py",
    "publisher_humidity.py",
    "publisher_nitrogen.py",
    "publisher_phosphorus.py",
    "publisher_potassium.py",
    "publisher_ph.py",
    "publisher_salinity.py",
    "publisher_root_temp.py",
]


def check_dependencies():
    """Check that required third-party packages are installed before launching."""
    missing = []
    if importlib.util.find_spec("paho") is None:
        missing.append("paho-mqtt")
    if importlib.util.find_spec("pygame") is None:
        missing.append("pygame")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install them with:")
        print(f"  {sys.executable} -m pip install -r {ROOT_DIR / 'requirements.txt'}")
        return False
    return True


def start_process(script_name, *args):
    """Launch a Python script as a subprocess using the current interpreter."""
    script_path = ROOT_DIR / script_name
    return subprocess.Popen(
        [sys.executable, str(script_path), *args],
        cwd=str(ROOT_DIR),
    )


def stop_process(process):
    """Gracefully terminate a subprocess, killing it if it does not stop in time."""
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main():
    if not check_dependencies():
        return 1

    print("Starting Smart Plant Monitoring System…")
    processes = {}

    print("\nLaunching controllers...")
    for script in CONTROLLERS:
        proc = start_process(script)
        processes[script] = proc
        time.sleep(0.2)

    time.sleep(2)

    print("\nLaunching publishers...")
    for plant_type in PLANT_TYPES:
        for script in PUBLISHERS:
            name = f"{script} ({plant_type})"
            proc = start_process(script, plant_type)
            processes[name] = proc
            time.sleep(0.15)

    print("\nLaunching dashboard...")
    dashboard = start_process("dashboard.py")
    processes["dashboard.py"] = dashboard

    print("\nAll services running. Press Ctrl+C to stop.\n")

    try:
        while True:
            for name, proc in processes.items():
                if proc.poll() is not None:
                    print(f"{name} stopped unexpectedly.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping all services…")
    finally:
        for proc in processes.values():
            stop_process(proc)
        print("All stopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import importlib.util
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


def check_dependencies():
    if importlib.util.find_spec("paho") is not None:
        return True

    print("Missing dependency: paho-mqtt")
    print("Install it with:")
    print(f"{sys.executable} -m pip install -r {ROOT_DIR / 'requirements.txt'}")
    return False


def start_process(script_name):
    script_path = ROOT_DIR / script_name
    return subprocess.Popen([sys.executable, str(script_path)], cwd=str(ROOT_DIR))


def stop_process(process):
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

    print("Starting Smart Plant Monitoring...")
    print("This will run controller and publisher together.")

    controller = start_process("controller.py")
    time.sleep(1)
    publisher = start_process("publisher.py")

    print("Running:")
    print("- controller.py")
    print("- publisher.py")
    print("Press Ctrl+C to stop both.")

    try:
        while True:
            if controller.poll() is not None:
                print("controller.py stopped.")
                break
            if publisher.poll() is not None:
                print("publisher.py stopped.")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        stop_process(publisher)
        stop_process(controller)
        print("Stopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

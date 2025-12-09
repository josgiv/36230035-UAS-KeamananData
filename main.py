import subprocess
import time
import sys
import os
import signal
from pathlib import Path

# Paths relative to this script (assumed to be in project root)
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

# Absolute paths to target files
API_PATH = SRC_DIR / "app" / "api.py"
WEB_DIR = SRC_DIR / "app" / "web" / "ddos-protection-full"
DUMMY_DATA_PATH = SRC_DIR / "app" / "dummy_data_stream.py"

processes = []

def run_process(command, cwd=None, env=None):
    """Helper to run a process in the background."""
    print(f"[*] Starting: {' '.join(command)}")
    p = subprocess.Popen(command, cwd=cwd, env=env)
    processes.append(p)
    return p

def main():
    print("="*60)
    print("   SHIELDGUARD AI SYSTEM LAUNCHER")
    print("   - API (FastAPI) : Port 8000")
    print("   - Dashboard (Next.js + Shadcn) : Port 3000")
    print("   - Traffic Simulator")
    print("="*60)

    try:
        # 1. Setup Environment
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + current_pythonpath
        
        # 2. Start FastAPI (Uvicorn)
        print("[*] Launching API Core...")
        proc_api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(SRC_DIR),
            env=env
        )
        processes.append(proc_api)
        
        # Wait a bit for API to come up
        time.sleep(3)
        
        # 3. Start Web Dashboard (Next.js)
        print("[*] Launching Next.js Dashboard...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        
        # Next.js runs on 3000 by default (npm run dev)
        # We assume 'npm run dev' is mapped to 'next dev --port 3000' or default
        proc_dashboard = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(WEB_DIR),
            env=env
        )
        processes.append(proc_dashboard)

        # 4. Start Dummy Data Stream
        print("[*] Starting Traffic Simulation...")
        proc_dummy = subprocess.Popen(
            [sys.executable, str(DUMMY_DATA_PATH)],
            cwd=str(SRC_DIR),
            env=env
        )
        processes.append(proc_dummy)
        
        print("\n[SUCCESS] All Systems Operational. Press Ctrl+C to stop.\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are alive
            if proc_api.poll() is not None:
                print("[!] API process died.")
                break
            if proc_dashboard.poll() is not None:
                print("[!] Dashboard process died.")
                break

    except KeyboardInterrupt:
        print("\n[!] Stopping all services...")
    finally:
        for p in processes:
            if p.poll() is None:
                try:
                    p.terminate()
                except:
                    pass
        print("[*] Cleanup complete.")

if __name__ == "__main__":
    main()

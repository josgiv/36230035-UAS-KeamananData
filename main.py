import subprocess
import sys
import os
import signal
import time
import shutil
import platform
import webbrowser

# Configuration
API_PORT = 8000
STREAMLIT_PORT = 8501
NEXTJS_PORT = 3000
SIMULATOR_DELAY = 5 # Seconds to wait before starting simulator

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEXTJS_DIR = os.path.join(BASE_DIR, "src", "app", "web", "ddos-protection-full")
STREAMLIT_EXPECTED_PATH = os.path.join(BASE_DIR, "src", "app", "web", "streamlit.py")
SIMULATOR_PATH = os.path.join(BASE_DIR, "src", "app", "dummy_data_stream.py")

processes = []

def log(message, level="INFO"):
    print(f"[{level}] {message}")

def check_npm():
    return shutil.which("npm") is not None

def run_api():
    """Runs the FastAPI backend."""
    log("Starting FastAPI Backend...")
    # Using 'src.app.api:app' assuming main.py is in root
    cmd = [sys.executable, "-m", "uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", str(API_PORT)]
    p = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(p)
    return p

def run_simulator():
    """Runs the Traffic Simulator."""
    log("Starting Real-time Traffic Simulator...")
    cmd = [sys.executable, SIMULATOR_PATH]
    p = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(p)
    return p

def run_streamlit():
    """Runs the Streamlit Dashboard."""
    log("Starting Streamlit Dashboard...")
    cmd = [sys.executable, "-m", "streamlit", "run", STREAMLIT_EXPECTED_PATH, "--server.port", str(STREAMLIT_PORT)]
    p = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(p)
    return p

def run_nextjs():
    """Runs the Next.js Frontend."""
    if not os.path.exists(NEXTJS_DIR):
        log(f"Next.js directory not found at {NEXTJS_DIR}", "WARNING")
        return None

    log("Starting Next.js Dashboard...")
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join(NEXTJS_DIR, "node_modules")):
         log("node_modules not found. Installing dependencies (this may take a while)...", "WARNING")
         subprocess.call(["npm", "install"], cwd=NEXTJS_DIR, shell=True)

    cmd = ["npm", "run", "dev"]
    # Update for Windows shell if needed
    shell = True if platform.system() == "Windows" else False
    
    p = subprocess.Popen(cmd, cwd=NEXTJS_DIR, shell=shell)
    processes.append(p)
    return p

def cleanup(signum, frame):
    log("\nShutting down all services...", "INFO")
    for p in processes:
        try:
            if platform.system() == "Windows":
                 subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
            else:
                p.terminate()
        except:
            pass
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("==================================================")
    print("   SHIELDGUARD SOC - INTEGRATED LAUNCHER")
    print("==================================================")

    # 1. Start API (Critical)
    api_proc = run_api()
    time.sleep(3) # Give API time to startup

    # 2. Start Streamlit (Always Fallback)
    st_proc = run_streamlit()
    
    # 3. Try Next.js
    npm_available = check_npm()
    primary_url = f"http://localhost:{STREAMLIT_PORT}"
    
    if npm_available:
        log("Node.js/NPM detected. Launching Advanced UI...")
        next_proc = run_nextjs()
        if next_proc:
            primary_url = f"http://localhost:{NEXTJS_PORT}"
            print(f"\n[SUCCESS] Services Running:")
            print(f" > API: http://localhost:{API_PORT}")
            print(f" > Streamlit (Fallback): http://localhost:{STREAMLIT_PORT}")
            print(f" > Next.js (Primary): http://localhost:{NEXTJS_PORT}")
        else:
            print(f"\n[PARTIAL] API and Streamlit running. Next.js failed to start.")
    else:
        log("npm not found. Skipping Next.js.", "WARNING")
        log("FALLBACK MODE ACTIVE: Using Streamlit Only.", "IMPORTANT")
        print(f"\n[SUCCESS] Services Running (Fallback Mode):")
        print(f" > API: http://localhost:{API_PORT}")
        print(f" > Streamlit: http://localhost:{STREAMLIT_PORT}")

    # 4. Start Simulator (Delayed to ensure API is ready)
    log(f"Waiting {SIMULATOR_DELAY}s before starting traffic simulation...")
    time.sleep(SIMULATOR_DELAY)
    sim_proc = run_simulator()

    # 5. Auto Open Browser
    print(f"\n[LAUNCH] Opening Default Dashboard: {primary_url}")
    try:
        webbrowser.open(primary_url)
        # Also open fallback if primary is Next.js, just in case user wants both
        if primary_url != f"http://localhost:{STREAMLIT_PORT}":
             webbrowser.open(f"http://localhost:{STREAMLIT_PORT}")
    except:
        pass

    # Keep alive
    try:
        while True:
            time.sleep(1)
            # Check if API died
            if api_proc.poll() is not None:
                log("API Process died! Exiting...", "ERROR")
                cleanup(None, None)
    except KeyboardInterrupt:
        cleanup(None, None)

if __name__ == "__main__":
    main()

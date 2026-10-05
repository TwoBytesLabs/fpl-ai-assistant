import subprocess
import sys
import os
import signal

def main():
    print("Starting FPL AI Assistant (Backend + Frontend)...")
    
    root_dir = os.getcwd()
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    python_path = os.path.join(backend_dir, "venv", "bin", "python")
    
    # Start Backend using module execution to avoid shebang path issues if folder was renamed
    backend = subprocess.Popen(
        [python_path, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"],
        cwd=backend_dir
    )
    
    # Start Frontend
    frontend = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host"],
        cwd=frontend_dir
    )
    
    def signal_handler(sig, frame):
        print("\nShutting down both servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()

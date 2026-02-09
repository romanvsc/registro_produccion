#!/usr/bin/env python3
"""
Development Server Launcher

Runs both FastAPI backend and Vue.js frontend concurrently.

Usage:
    python dev.py [--backend-port 8000] [--frontend-port 5173]
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def find_project_root():
    """Find the project root by looking for backend and frontend directories"""
    current = Path.cwd()
    
    # Check if we're already in project root
    if (current / "backend").exists() and (current / "frontend").exists():
        return current
    
    # Check if we're in backend or frontend
    if current.name in ["backend", "frontend"]:
        return current.parent
    
    # Check parent directory
    if (current.parent / "backend").exists() and (current.parent / "frontend").exists():
        return current.parent
    
    return None


def start_backend(port):
    """Start FastAPI backend"""
    backend_path = Path.cwd() / "backend"
    
    if not backend_path.exists():
        print("Error: backend directory not found")
        return None
    
    print(f"Starting backend on port {port}...")
    
    # Check for venv
    venv_python = backend_path / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = backend_path / "venv" / "bin" / "python"
    
    python_cmd = str(venv_python) if venv_python.exists() else "python"
    
    cmd = [
        python_cmd, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", str(port)
    ]
    
    return subprocess.Popen(
        cmd,
        cwd=backend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )


def start_frontend(port):
    """Start Vue.js frontend"""
    frontend_path = Path.cwd() / "frontend"
    
    if not frontend_path.exists():
        print("Error: frontend directory not found")
        return None
    
    print(f"Starting frontend on port {port}...")
    
    # Check if node_modules exists
    if not (frontend_path / "node_modules").exists():
        print("Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
    
    cmd = ["npm", "run", "dev", "--", "--port", str(port)]
    
    return subprocess.Popen(
        cmd,
        cwd=frontend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )


def print_output(process, name):
    """Print process output with prefix"""
    for line in process.stdout:
        print(f"[{name}] {line}", end="")


def main():
    parser = argparse.ArgumentParser(description="Run backend and frontend dev servers")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port")
    parser.add_argument("--frontend-port", type=int, default=5173, help="Frontend port")
    
    args = parser.parse_args()
    
    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root with backend/ and frontend/ directories")
        sys.exit(1)
    
    os.chdir(project_root)
    print(f"Project root: {project_root}")
    print()
    
    # Start both servers
    backend_proc = start_backend(args.backend_port)
    frontend_proc = start_frontend(args.frontend_port)
    
    if not backend_proc or not frontend_proc:
        print("Failed to start servers")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print(f"Backend running on: http://localhost:{args.backend_port}")
    print(f"Frontend running on: http://localhost:{args.frontend_port}")
    print(f"API docs: http://localhost:{args.backend_port}/docs")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop both servers")
    print()
    
    try:
        # Wait for processes
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Servers stopped")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# launch.py

import sys
import subprocess
import os
import platform

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import tkinter
        import PIL
        import reportlab
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please install them manually.")
        print("Run: pip install -r requirements.txt")
        return False

def main():
    """Main entry point for launching the application."""
    print("Starting Storyboard Generator...")
    
    # Add the parent directory to Python's path so it can find the package
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Check dependencies
    if not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    # Run the application using runner.py
    runner_path = os.path.join(project_dir, "runner.py")
    try:
        subprocess.check_call([sys.executable, runner_path])
    except subprocess.CalledProcessError:
        print("Application exited with an error.")
        sys.exit(1)

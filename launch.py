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
    
    # Check dependencies
    if not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    # Run the application directly
    try:
        # Set up the environment to ensure proper imports
        project_dir = os.path.dirname(os.path.abspath(__file__))
        env = os.environ.copy()
        
        # Add the project directory to PYTHONPATH
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{project_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = project_dir
        
        # Run the main script directly
        subprocess.check_call(
            [sys.executable, os.path.join(project_dir, "storyboard_generator", "main.py")],
            env=env
        )
    except subprocess.CalledProcessError:
        print("Application exited with an error.")
        sys.exit(1)

if __name__ == "__main__":
    main()

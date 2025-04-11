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
    
    # Check if we're running from source or as an installed package
    if os.path.exists("main.py"):
        # Running from source with root main.py
        script_path = "main.py"
    elif os.path.exists(os.path.join("storyboard_generator", "main.py")):
        # Running from source with main.py in subdirectory
        script_path = os.path.join("storyboard_generator", "main.py")
    else:
        # Try to import as a package
        try:
            from storyboard_generator import main as app_main
            app_main.main()
            return
        except ImportError:
            print("Cannot find the storyboard generator application.")
            print("Make sure it's installed or you're running from the source directory.")
            sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    # Run the application
    try:
        subprocess.check_call([sys.executable, script_path])
    except subprocess.CalledProcessError:
        print("Application exited with an error.")
        sys.exit(1)

if __name__ == "__main__":
    main()

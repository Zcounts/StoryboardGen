#!/usr/bin/env python3
# storyboard_generator/main.py

import tkinter as tk
import os
import sys

# Add parent directory to path to make imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try direct import approach
from storyboard_generator.app import StoryboardApp

def main():
    """Main entry point for the Storyboard Generator application."""
    root = tk.Tk()
    root.title("Storyboard Generator")
    root.geometry("1200x800")
    
    # Create and start the application
    app = StoryboardApp(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()

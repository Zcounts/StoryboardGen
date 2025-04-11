# storyboard_generator/main.py

import tkinter as tk
try:
    # Try relative import (when used as a package)
    from .app import StoryboardApp
except ImportError:
    # Fallback to absolute import (when run directly)
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

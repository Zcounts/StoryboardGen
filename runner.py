# runner.py - Place in the project root directory
import os
import sys

# Add the project root to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import and run the main function
from storyboard_generator.main import main

if __name__ == "__main__":
    main()

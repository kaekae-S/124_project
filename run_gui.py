"""
Launcher script for the LOLCODE Interpreter GUI
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.lolcode_interpreter_gui import main

if __name__ == "__main__":
    main()





"""
LOLCODE Interpreter - GUI Launcher


The LOLCODE Interpreter is a three-stage compiler:
1. Lexer: Converts source code into tokens
2. Parser: Builds abstract syntax tree from tokens
3. Semantic Analyzer: Validates logic and semantic correctness

This script simply starts the GUI application.
"""

import sys
import os

# Add src directory to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.lolcode_interpreter_gui import main

if __name__ == "__main__":
    main()


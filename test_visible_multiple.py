import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.lexer import Lexer
from parser.parser import Parser

lexer = Lexer()
parser = Parser(lexer)

code = '''HAI
I HAS A var ITZ 12
VISIBLE "noot noot" var
KTHXBYE'''

try:
    tree = parser.parse(code)
    print("SUCCESS: Parsed successfully!")
    print(f"Tree: {tree}")
except SyntaxError as e:
    print(f"ERROR: {e}")




"""
Debug Utility for Boolean Expressions
Purpose: Debug lexer and parser behavior on boolean expression sample

This script tests parsing of LOLCODE boolean operations
and displays tokens and parse results for troubleshooting.

Usage: python debug_bool.py 
"""

import sys
sys.path.insert(0, 'src')
from lexer.lexer import Lexer
from parser.parser import Parser

# Load sample LOLCODE file
path = 'src/tests/samples/05_bool.lol'
code = open(path).read()
print('=== SOURCE ===')
print(code)

# Tokenize
lexer = Lexer()
tokens = lexer.tokenize(code)
print('\n=== TOKENS AROUND LINE 12-20 ===')
for t in tokens:
    if t['line'] >= 12 and t['line'] <= 20:
        print(t)

# Parse
print('\n=== PARSING ATTEMPT ===')
parser = Parser(lexer)
try:
    tree = parser.parse(code)
    print('Parsed successfully')
    stmts = getattr(tree, 'statements_node', None)
    if stmts:
        print('Number of statements:', len(getattr(stmts,'statements',[])))
except Exception as e:
    print('Parser error:', e)
    # show current position token if available
    try:
        ct = parser.current_token
        print('Current token at error:', ct)
    except Exception:
        pass

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.lexer import Lexer
from parser.parser import Parser

lexer = Lexer()
parser = Parser(lexer)

# Test 1: Missing HAI
print("Test 1: Missing HAI")
try:
    code1 = 'VISIBLE "test"\nKTHXBYE'
    parser.parse(code1)
    print("  ERROR: Should have raised SyntaxError!")
except SyntaxError as e:
    print(f"  OK: Correctly caught error: {e}")

# Test 2: Missing KTHXBYE
print("\nTest 2: Missing KTHXBYE")
try:
    code2 = 'HAI\nVISIBLE "test"'
    parser.parse(code2)
    print("  ERROR: Should have raised SyntaxError!")
except SyntaxError as e:
    print(f"  OK: Correctly caught error: {e}")

# Test 3: Missing both
print("\nTest 3: Missing both HAI and KTHXBYE")
try:
    code3 = 'VISIBLE "test"'
    parser.parse(code3)
    print("  ERROR: Should have raised SyntaxError!")
except SyntaxError as e:
    print(f"  OK: Correctly caught error: {e}")

# Test 4: Correct program
print("\nTest 4: Correct program (should work)")
try:
    code4 = 'HAI\nVISIBLE "test"\nKTHXBYE'
    tree = parser.parse(code4)
    print(f"  OK: Parsed successfully: {tree}")
except SyntaxError as e:
    print(f"  ERROR: Should not have raised error: {e}")

print("\nAll tests completed!")


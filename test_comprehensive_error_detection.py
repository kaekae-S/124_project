"""
Comprehensive Error Detection Test Suite
Tests all error detection improvements in the parser.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.lexer import Lexer
from parser.parser import Parser

lexer = Lexer()
parser = Parser(lexer)

# Test results tracking
passed = 0
failed = 0
test_results = []

def run_test(name, code, should_fail=True, expected_error_contains=None):
    """Run a single test case."""
    global passed, failed
    try:
        tree = parser.parse(code)
        if should_fail:
            test_results.append(("FAIL", name, "Should have raised SyntaxError but parsed successfully"))
            failed += 1
        else:
            test_results.append(("PASS", name, "Parsed successfully (expected)"))
            passed += 1
    except SyntaxError as e:
        error_msg = str(e)
        if should_fail:
            if expected_error_contains:
                if expected_error_contains.lower() in error_msg.lower():
                    test_results.append(("PASS", name, f"Correctly caught: {error_msg[:60]}..."))
                    passed += 1
                else:
                    test_results.append(("FAIL", name, f"Error doesn't contain '{expected_error_contains}': {error_msg}"))
                    failed += 1
            else:
                test_results.append(("PASS", name, f"Correctly caught: {error_msg[:60]}..."))
                passed += 1
        else:
            test_results.append(("FAIL", name, f"Should not have raised error: {error_msg}"))
            failed += 1
    except Exception as e:
        test_results.append(("FAIL", name, f"Unexpected error type {type(e).__name__}: {e}"))
        failed += 1

print("=" * 80)
print("COMPREHENSIVE ERROR DETECTION TEST SUITE")
print("=" * 80)

# ============================================================================
# PROGRAM STRUCTURE ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("1. PROGRAM STRUCTURE ERRORS")
print("=" * 80)

run_test("Missing HAI - empty code", "", True, "HAI")
run_test("Missing HAI - only whitespace", "   \n  \n  ", True, "HAI")
run_test("Missing HAI - only comments", "BTW comment\nOBTW\ncomment\nTLDR", True, "HAI")
run_test("Missing HAI - starts with statement", 'VISIBLE "test"\nKTHXBYE', True, "HAI")
run_test("Missing KTHXBYE - ends with statement", 'HAI\nVISIBLE "test"', True, "KTHXBYE")
run_test("Missing both HAI and KTHXBYE", 'VISIBLE "test"', True, "HAI")
run_test("HAI wrong case", 'hai\nVISIBLE "test"\nKTHXBYE', True, "HAI")
run_test("KTHXBYE wrong case", 'HAI\nVISIBLE "test"\nkthxbye', True, "KTHXBYE")
run_test("Tokens after KTHXBYE", 'HAI\nKTHXBYE\nVISIBLE "test"', True, "after 'KTHXBYE'")
run_test("Valid: Complete program", 'HAI\nVISIBLE "test"\nKTHXBYE', False)

# ============================================================================
# WAZZUP/BUHBYE BLOCK ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("2. WAZZUP/BUHBYE BLOCK ERRORS")
print("=" * 80)

run_test("WAZZUP without BUHBYE", 'HAI\nWAZZUP\nI HAS A x\nKTHXBYE', True, "BUHBYE")
run_test("WAZZUP with KTHXBYE instead of BUHBYE", 'HAI\nWAZZUP\nI HAS A x\nKTHXBYE', True, "BUHBYE")
run_test("WAZZUP with unexpected token", 'HAI\nWAZZUP\nINVALID_TOKEN\nBUHBYE\nKTHXBYE', True, "Unexpected token")
run_test("WAZZUP empty block", 'HAI\nWAZZUP\nBUHBYE\nKTHXBYE', False)
run_test("Valid: WAZZUP with statements", 'HAI\nWAZZUP\nI HAS A x\nI HAS A y\nBUHBYE\nKTHXBYE', False)

# ============================================================================
# STATEMENT ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("3. STATEMENT ERRORS")
print("=" * 80)

run_test("Unknown statement", 'HAI\nUNKNOWN_STMT\nKTHXBYE', True, "Unexpected token")
run_test("VISIBLE without expression", 'HAI\nVISIBLE\nKTHXBYE', True, "expression")
run_test("I HAS A without identifier", 'HAI\nI HAS A\nKTHXBYE', True, "identifier after 'I HAS A'")
run_test("I HAS A ITZ without expression", 'HAI\nI HAS A x ITZ\nKTHXBYE', True, "expression")
run_test("GIMMEH without identifier", 'HAI\nGIMMEH\nKTHXBYE', True, "identifier after 'GIMMEH'")
run_test("GIMMEH AN without identifier", 'HAI\nGIMMEH x AN\nKTHXBYE', True, "identifier after 'AN'")
run_test("Assignment without R", 'HAI\nx\nKTHXBYE', True, "Unexpected token")
run_test("Assignment R without expression", 'HAI\nx R\nKTHXBYE', True, "expression")
run_test("Valid: VISIBLE with expression", 'HAI\nVISIBLE "test"\nKTHXBYE', False)
run_test("Valid: I HAS A with ITZ", 'HAI\nI HAS A x ITZ 5\nKTHXBYE', False)
run_test("Valid: GIMMEH multiple", 'HAI\nGIMMEH x AN y\nKTHXBYE', False)

# ============================================================================
# BOOLEAN EXPRESSION ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("4. BOOLEAN EXPRESSION ERRORS")
print("=" * 80)

run_test("NOT without expression", 'HAI\nVISIBLE NOT\nKTHXBYE', True, "expression")
run_test("BOTH OF without first operand", 'HAI\nVISIBLE BOTH OF\nKTHXBYE', True, "expression")
run_test("BOTH OF without AN", 'HAI\nVISIBLE BOTH OF 1\nKTHXBYE', True, "AN")
run_test("BOTH OF without second operand", 'HAI\nVISIBLE BOTH OF 1 AN\nKTHXBYE', True, "expression")
run_test("EITHER OF without first operand", 'HAI\nVISIBLE EITHER OF\nKTHXBYE', True, "expression")
run_test("EITHER OF without AN", 'HAI\nVISIBLE EITHER OF 1\nKTHXBYE', True, "AN")
run_test("WON OF without first operand", 'HAI\nVISIBLE WON OF\nKTHXBYE', True, "expression")
run_test("ALL OF without operand", 'HAI\nVISIBLE ALL OF\nKTHXBYE', True, "expression")
run_test("ALL OF AN without operand", 'HAI\nVISIBLE ALL OF 1 AN\nKTHXBYE', True, "expression")
run_test("ANY OF without operand", 'HAI\nVISIBLE ANY OF\nKTHXBYE', True, "expression")
run_test("Valid: NOT expression", 'HAI\nVISIBLE NOT WIN\nKTHXBYE', False)
run_test("Valid: BOTH OF", 'HAI\nVISIBLE BOTH OF WIN AN FAIL\nKTHXBYE', False)
run_test("Valid: ALL OF", 'HAI\nVISIBLE ALL OF WIN AN FAIL\nKTHXBYE', False)

# ============================================================================
# COMPARISON EXPRESSION ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("5. COMPARISON EXPRESSION ERRORS")
print("=" * 80)

run_test("BOTH SAEM without first operand", 'HAI\nVISIBLE BOTH SAEM\nKTHXBYE', True, "expression")
run_test("BOTH SAEM without AN", 'HAI\nVISIBLE BOTH SAEM 1\nKTHXBYE', True, "AN")
run_test("BOTH SAEM without second operand", 'HAI\nVISIBLE BOTH SAEM 1 AN\nKTHXBYE', True, "expression")
run_test("DIFFRINT without first operand", 'HAI\nVISIBLE DIFFRINT\nKTHXBYE', True, "expression")
run_test("DIFFRINT without AN", 'HAI\nVISIBLE DIFFRINT 1\nKTHXBYE', True, "AN")
run_test("DIFFRINT without second operand", 'HAI\nVISIBLE DIFFRINT 1 AN\nKTHXBYE', True, "expression")
run_test("Valid: BOTH SAEM", 'HAI\nVISIBLE BOTH SAEM 1 AN 1\nKTHXBYE', False)
run_test("Valid: DIFFRINT", 'HAI\nVISIBLE DIFFRINT 1 AN 2\nKTHXBYE', False)

# ============================================================================
# ARITHMETIC EXPRESSION ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("6. ARITHMETIC EXPRESSION ERRORS")
print("=" * 80)

run_test("SUM OF without first operand", 'HAI\nVISIBLE SUM OF\nKTHXBYE', True, "expression")
run_test("SUM OF without AN", 'HAI\nVISIBLE SUM OF 1\nKTHXBYE', True, "AN")
run_test("SUM OF without second operand", 'HAI\nVISIBLE SUM OF 1 AN\nKTHXBYE', True, "expression")
run_test("DIFF OF without first operand", 'HAI\nVISIBLE DIFF OF\nKTHXBYE', True, "expression")
run_test("DIFF OF without AN", 'HAI\nVISIBLE DIFF OF 1\nKTHXBYE', True, "AN")
run_test("PRODUKT OF without first operand", 'HAI\nVISIBLE PRODUKT OF\nKTHXBYE', True, "expression")
run_test("PRODUKT OF without AN", 'HAI\nVISIBLE PRODUKT OF 1\nKTHXBYE', True, "AN")
run_test("QUOSHUNT OF without first operand", 'HAI\nVISIBLE QUOSHUNT OF\nKTHXBYE', True, "expression")
run_test("QUOSHUNT OF without AN", 'HAI\nVISIBLE QUOSHUNT OF 1\nKTHXBYE', True, "AN")
run_test("MOD OF without first operand", 'HAI\nVISIBLE MOD OF\nKTHXBYE', True, "expression")
run_test("MOD OF without AN", 'HAI\nVISIBLE MOD OF 1\nKTHXBYE', True, "AN")
run_test("BIGGR OF without first operand", 'HAI\nVISIBLE BIGGR OF\nKTHXBYE', True, "expression")
run_test("BIGGR OF without AN", 'HAI\nVISIBLE BIGGR OF 1\nKTHXBYE', True, "AN")
run_test("SMALLR OF without first operand", 'HAI\nVISIBLE SMALLR OF\nKTHXBYE', True, "expression")
run_test("SMALLR OF without AN", 'HAI\nVISIBLE SMALLR OF 1\nKTHXBYE', True, "AN")
run_test("SMOOSH without operand", 'HAI\nVISIBLE SMOOSH\nKTHXBYE', True, "expression")
run_test("SMOOSH AN without operand", 'HAI\nVISIBLE SMOOSH "a" AN\nKTHXBYE', True, "expression")
run_test("Valid: SUM OF", 'HAI\nVISIBLE SUM OF 1 AN 2\nKTHXBYE', False)
run_test("Valid: SMOOSH", 'HAI\nVISIBLE SMOOSH "a" AN "b"\nKTHXBYE', False)

# ============================================================================
# STRING CONCATENATION ERRORS
# ============================================================================
print("\n" + "=" * 80)
print("7. STRING CONCATENATION ERRORS")
print("=" * 80)

run_test("+ without right operand", 'HAI\nVISIBLE "a" +\nKTHXBYE', True, "expression after '+'")
run_test("+ with invalid right operand", 'HAI\nVISIBLE "a" + KTHXBYE\nKTHXBYE', True, "expression after '+'")
run_test("Valid: String concatenation", 'HAI\nVISIBLE "a" + "b"\nKTHXBYE', False)
run_test("Valid: Multiple concatenations", 'HAI\nVISIBLE "a" + "b" + "c"\nKTHXBYE', False)

# ============================================================================
# COMPLEX VALID PROGRAMS
# ============================================================================
print("\n" + "=" * 80)
print("8. COMPLEX VALID PROGRAMS (Should Parse Successfully)")
print("=" * 80)

run_test("Valid: Nested expressions", 'HAI\nVISIBLE SUM OF BIGGR OF 3 AN 4 AN 5\nKTHXBYE', False)
run_test("Valid: Complex boolean", 'HAI\nVISIBLE BOTH OF BOTH SAEM 1 AN 1 AN WIN\nKTHXBYE', False)
run_test("Valid: WAZZUP with complex statements", '''HAI
WAZZUP
    I HAS A x ITZ SUM OF 1 AN 2
    VISIBLE x
BUHBYE
KTHXBYE''', False)
run_test("Valid: Multiple statements", '''HAI
I HAS A x ITZ 5
I HAS A y ITZ 10
VISIBLE SUM OF x AN y
KTHXBYE''', False)

# ============================================================================
# PRINT RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("TEST RESULTS SUMMARY")
print("=" * 80)

for status, name, message in test_results:
    status_symbol = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{status_symbol} {name}")
    if status == "FAIL":
        print(f"      {message}")

print("\n" + "=" * 80)
print(f"TOTAL: {passed + failed} tests")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print(f"SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
print("=" * 80)

if failed == 0:
    print("\n[SUCCESS] All tests passed!")
    sys.exit(0)
else:
    print(f"\n[FAILURE] {failed} test(s) failed")
    sys.exit(1)

"""
Comprehensive Error Detection Test Suite

Purpose: Validate that Lexer, Parser, and Semantic Analyzer catch all error types

Tests 23 different error scenarios covering:
- Syntax errors: Missing tokens, invalid constructs
- Semantic errors: Undefined variables, duplicates, scope issues
- Edge cases: Complex nested structures, boundary conditions

Each test verifies that the correct error type is detected with proper error messaging.

Test Result Summary Format:
[OK] Test passed (correct error detected or program executed)
[X]  Test failed (unexpected error or no error when expected)
"""

import sys
import os
sys.path.insert(0, 'src')

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer


def test_case(code, name, expect_error=False, error_type=None):
    """Execute a single test case.
    
    Reference: Each test uses the three-stage compilation pipeline:
    Lexer → Parser → Semantic Analyzer
    
    Args:
        code (str): LOLCODE source code to test
        name (str): Descriptive test name
        expect_error (bool): Whether an error should occur
        error_type (str): Type of expected error ('syntax', 'semantic')
    
    Returns:
        tuple: (test_passed: bool, error_message: str or None)
    """
    lexer = Lexer()
    parser = Parser(lexer)
    semantic_analyzer = SemanticAnalyzer()
    
    print(f"\n{'-'*80}")
    print(f"TEST: {name}")
    if expect_error:
        print(f"EXPECTED: {error_type.upper()} ERROR")
    print(f"{'-'*80}")
    
    try:
        # Tokenize
        tokens = lexer.tokenize(code)
        
        # Parse
        parse_tree = parser.parse(code)
        
        # Semantic analysis
        semantic_errors = semantic_analyzer.analyze(parse_tree)
        
        if semantic_errors:
            print(f"[X] SEMANTIC ERRORS ({len(semantic_errors)}):")
            for error in semantic_errors:
                print(f"    {error}")
            if expect_error and error_type == 'semantic':
                print(f"[OK] PASS - Expected semantic error caught")
                return True, None
            else:
                return False, f"Unexpected semantic error: {semantic_errors[0]}"
        else:
            if expect_error:
                return False, f"Expected {error_type} error but got none"
            print(f"[OK] PASS - No errors")
            return True, None
            
    except SyntaxError as e:
        print(f"[X] SYNTAX ERROR: {e}")
        if expect_error and error_type == 'syntax':
            print(f"[OK] PASS - Expected syntax error caught")
            return True, None
        else:
            return False, f"Unexpected syntax error: {str(e)}"
    except Exception as e:
        print(f"[X] ERROR: {type(e).__name__}: {e}")
        if expect_error and error_type == 'lexer':
            print(f"[OK] PASS - Expected lexer error caught")
            return True, None
        else:
            return False, f"Unexpected error: {str(e)}"


def main():
    """Run all edge case and error tests."""
    
    print("\n" + "[" + "="*78 + "]")
    print("[" + " "*15 + "COMPREHENSIVE ERROR CASE TESTING" + " "*32 + "]")
    print("[" + " "*78 + "]")
    print("[" + " Testing edge cases and error scenarios" + " "*40 + "]")
    print("[" + "="*78 + "]")
    
    results = []
    
    # =========================================================================
    # SEMANTIC ERRORS - Variable Issues
    # =========================================================================
    print("\n\n" + "="*80)
    print("SEMANTIC ERRORS - VARIABLE ISSUES")
    print("="*80)
    
    # Undefined in arithmetic
    results.append(test_case("""HAI
I HAS A result ITZ SUM OF undefined AN 5
KTHXBYE""", 
        "Undefined variable in arithmetic", 
        expect_error=True, error_type='semantic'))
    
    # Undefined in comparison
    results.append(test_case("""HAI
I HAS A eq ITZ BOTH SAEM x AN y
KTHXBYE""", 
        "Undefined variables in comparison", 
        expect_error=True, error_type='semantic'))
    
    # Undefined in boolean
    results.append(test_case("""HAI
I HAS A result ITZ BOTH OF a AN b
KTHXBYE""", 
        "Undefined variables in boolean operation", 
        expect_error=True, error_type='semantic'))
    
    # Multiple undefined
    results.append(test_case("""HAI
VISIBLE a
VISIBLE b
VISIBLE c
KTHXBYE""", 
        "Multiple undefined variables", 
        expect_error=True, error_type='semantic'))
    
    # Duplicate declaration
    results.append(test_case("""HAI
I HAS A x
I HAS A x
KTHXBYE""", 
        "Duplicate variable declaration", 
        expect_error=True, error_type='semantic'))
    
    # Multiple duplicates
    results.append(test_case("""HAI
I HAS A a
I HAS A a
I HAS A b
I HAS A b
KTHXBYE""", 
        "Multiple duplicate declarations", 
        expect_error=True, error_type='semantic'))
    
    # =========================================================================
    # SEMANTIC ERRORS - Input/Output Issues
    # =========================================================================
    print("\n\n" + "="*80)
    print("SEMANTIC ERRORS - INPUT/OUTPUT ISSUES")
    print("="*80)
    
    # GIMMEH to undefined variable
    results.append(test_case("""HAI
GIMMEH undefined
KTHXBYE""", 
        "GIMMEH to undefined variable", 
        expect_error=True, error_type='semantic'))
    
    # Multiple GIMMEH with one undefined
    results.append(test_case("""HAI
I HAS A x
GIMMEH x
GIMMEH undefined
KTHXBYE""", 
        "Mixed GIMMEH - one undefined", 
        expect_error=True, error_type='semantic'))
    
    # =========================================================================
    # SEMANTIC ERRORS - Function Issues
    # =========================================================================
    print("\n\n" + "="*80)
    print("SEMANTIC ERRORS - FUNCTION ISSUES")
    print("="*80)
    
    # Call undefined function
    results.append(test_case("""HAI
I HAS A result ITZ I IZ undefined_func YR 42
KTHXBYE""", 
        "Call to undefined function", 
        expect_error=True, error_type='semantic'))
    
    # Function with wrong arity
    results.append(test_case("""HAI
HOW IZ I add YR a AN YR b
    FOUND YR SUM OF a AN b
IF U SAY SO

I HAS A result ITZ I IZ add YR 5
KTHXBYE""", 
        "Function call with wrong arity (too few)", 
        expect_error=True, error_type='semantic'))
    
    # =========================================================================
    # VALID CASES - Should NOT error
    # =========================================================================
    print("\n\n" + "="*80)
    print("VALID CASES - SHOULD NOT ERROR")
    print("="*80)
    
    # Empty program
    results.append(test_case("""HAI
KTHXBYE""", 
        "Empty program", 
        expect_error=False))
    
    # Simple declaration
    results.append(test_case("""HAI
I HAS A x
KTHXBYE""", 
        "Simple variable declaration", 
        expect_error=False))
    
    # Declaration with initialization
    results.append(test_case("""HAI
I HAS A x ITZ 42
KTHXBYE""", 
        "Variable declaration with initialization", 
        expect_error=False))
    
    # Valid usage
    results.append(test_case("""HAI
I HAS A x ITZ 10
VISIBLE x
KTHXBYE""", 
        "Valid variable usage", 
        expect_error=False))
    
    # WAZZUP block
    results.append(test_case("""HAI
WAZZUP
    I HAS A x ITZ 42
BUHBYE
VISIBLE x
KTHXBYE""", 
        "Valid WAZZUP block", 
        expect_error=False))
    
    # Multiple declarations
    results.append(test_case("""HAI
I HAS A a
I HAS A b
I HAS A c
VISIBLE a
VISIBLE b
VISIBLE c
KTHXBYE""", 
        "Multiple different variables", 
        expect_error=False))
    
    # Arithmetic
    results.append(test_case("""HAI
I HAS A a ITZ 5
I HAS A b ITZ 3
I HAS A sum ITZ SUM OF a AN b
VISIBLE sum
KTHXBYE""", 
        "Valid arithmetic", 
        expect_error=False))
    
    # Comparisons
    results.append(test_case("""HAI
I HAS A x ITZ 5
I HAS A y ITZ 5
VISIBLE BOTH SAEM x AN y
VISIBLE DIFFRINT x AN y
KTHXBYE""", 
        "Valid comparisons", 
        expect_error=False))
    
    # Boolean operations
    results.append(test_case("""HAI
I HAS A a ITZ WIN
I HAS A b ITZ FAIL
VISIBLE BOTH OF a AN b
VISIBLE EITHER OF a AN b
KTHXBYE""", 
        "Valid boolean operations", 
        expect_error=False))
    
    # GIMMEH valid
    results.append(test_case("""HAI
I HAS A name
I HAS A age
GIMMEH name
GIMMEH age
VISIBLE name
VISIBLE age
KTHXBYE""", 
        "Valid GIMMEH statements", 
        expect_error=False))
    
    # =========================================================================
    # SYNTAX ERRORS
    # =========================================================================
    print("\n\n" + "="*80)
    print("SYNTAX ERRORS - PARSER ISSUES")
    print("="*80)
    
    # Missing HAI
    results.append(test_case("""VISIBLE x
KTHXBYE""", 
        "Missing HAI", 
        expect_error=True, error_type='syntax'))
    
    # Missing KTHXBYE
    results.append(test_case("""HAI
I HAS A x""", 
        "Missing KTHXBYE", 
        expect_error=True, error_type='syntax'))
    
    # Invalid statement
    results.append(test_case("""HAI
INVALID_STATEMENT
KTHXBYE""", 
        "Invalid statement", 
        expect_error=True, error_type='syntax'))
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results if result[0])
    failed = sum(1 for result in results if not result[0])
    
    print(f"\nTotal Tests:  {len(results)}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    
    if failed > 0:
        print("\n" + "-"*80)
        print("FAILED TESTS:")
        print("-"*80)
        for i, (passed_flag, error_msg) in enumerate(results, 1):
            if not passed_flag:
                print(f"{i}. {error_msg}")
    
    print("\n" + "="*80)
    
    if failed == 0:
        print("\n[**] ALL TESTS PASSED! [**]")
        print("\nThe system correctly:")
        print("  [OK] Catches undefined variable errors")
        print("  [OK] Catches duplicate declaration errors")
        print("  [OK] Catches input/output errors")
        print("  [OK] Catches function call errors")
        print("  [OK] Accepts valid programs")
        print("  [OK] Detects syntax errors")
    else:
        print(f"\n[ERROR] {failed} tests failed")
    
    print("="*80 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

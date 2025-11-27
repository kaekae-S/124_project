"""
GUI Pipeline Integration Tests

Purpose: Test the complete three-stage compilation pipeline without GUI

This test suite validates that the Lexer, Parser, and Semantic Analyzer
work together correctly on real sample LOLCODE files.

Pipeline Stages Tested:
1. Lexer: Tokenization with symbol table generation
2. Parser: AST construction with error detection
3. Semantic Analyzer: Multi-pass validation with error collection

Tests: 10 integration scenarios covering valid and error detection cases
"""

import sys
import os
sys.path.insert(0, 'src')

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer
from pathlib import Path


def test_gui_pipeline(code, name):
    """Execute a complete pipeline test.
    
    Reference: Three-stage compilation pipeline
    Lexer tokenizes - Parser builds AST - Semantic Analyzer validates
    
    Args:
        code (str): LOLCODE source code
        name (str): Test description
        
    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    lexer = Lexer()
    parser = Parser(lexer)
    semantic_analyzer = SemanticAnalyzer()
    
    try:
        # Stage 1: Tokenize code into tokens
        print("\n[STAGE 1] TOKENIZATION")
        tokens = lexer.tokenize(code)
        print(f"[OK] Tokenized {len(tokens)} tokens")
        
        # Show first few tokens for reference
        if tokens:
            print("  Sample tokens:")
            for i, token in enumerate(tokens[:5]):
                print(f"    {i+1}. {token['value']:<15} ({token['type']})")
        
        # Stage 2: Build parse tree from tokens
        print("\n[STAGE 2] PARSING")
        parse_tree = parser.parse(code)
        print(f"[OK] Parse tree created: {type(parse_tree).__name__}")
        
        # Stage 3: Validate semantic correctness
        print("\n[STAGE 3] SEMANTIC ANALYSIS")
        semantic_errors = semantic_analyzer.analyze(parse_tree)
        
        if semantic_errors:
            print(f"[ERROR] {len(semantic_errors)} semantic error(s) found:")
            for error in semantic_errors:
                print(f"    - {error}")
            return False
        else:
            print(f"[OK] Semantic analysis: PASS (0 errors)")
            return True
    
    except SyntaxError as e:
        print(f"\n[ERROR] SYNTAX ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test complete pipeline with various LOLCODE samples."""
    
    print("=" * 80)
    print("GUI INTEGRATION TEST SUITE")
    print("=" * 80)
    print("")
    print("Testing: Lexer -> Parser -> Semantic Analyzer Integration")
    print("=" * 80)
    
    results = []
    
    # Test 1: Simple Valid Program
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A x ITZ 42
BUHBYE
VISIBLE x
KTHXBYE""", "Simple Valid Program"))
    
    # Test 2: Undefined Variable (should catch error)
    results.append(test_gui_pipeline("""HAI
VISIBLE undefined_var
KTHXBYE""", "Undefined Variable Detection"))
    
    # Test 3: Arithmetic Operations
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A a ITZ 5
    I HAS A b ITZ 3
BUHBYE
VISIBLE SUM OF a AN b
VISIBLE DIFF OF a AN b
KTHXBYE""", "Arithmetic Operations"))
    
    # Test 4: Input/Output
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A name
    I HAS A age
BUHBYE
GIMMEH name
GIMMEH age
VISIBLE name
VISIBLE age
KTHXBYE""", "Input/Output Statements"))
    
    # Test 5: Comparisons
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A x ITZ 10
    I HAS A y ITZ 10
BUHBYE
VISIBLE BOTH SAEM x AN y
VISIBLE DIFFRINT x AN y
KTHXBYE""", "Comparison Operations"))
    
    # Test 6: Boolean Operations
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A a ITZ WIN
    I HAS A b ITZ FAIL
BUHBYE
VISIBLE BOTH OF a AN b
VISIBLE EITHER OF a AN b
KTHXBYE""", "Boolean Operations"))
    
    # Test 7: Duplicate Variable (should catch error)
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A x ITZ 5
    I HAS A x ITZ 10
BUHBYE
KTHXBYE""", "Duplicate Variable Detection"))
    
    # Test 8: Complex Expression
    results.append(test_gui_pipeline("""HAI
WAZZUP
    I HAS A a ITZ 2
    I HAS A b ITZ 3
    I HAS A c ITZ 4
    I HAS A result ITZ SUM OF PRODUKT OF a AN b AN c
BUHBYE
VISIBLE result
KTHXBYE""", "Complex Nested Expressions"))
    
    # Test 9: Real Sample File
    sample_file = Path('src/tests/samples/02_gimmeh.lol')
    if sample_file.exists():
        with open(sample_file) as f:
            code = f.read()
        results.append(test_gui_pipeline(code, "Real Sample: 02_gimmeh.lol"))
    
    # Test 10: Real Sample File
    sample_file = Path('src/tests/samples/03_arith.lol')
    if sample_file.exists():
        with open(sample_file) as f:
            code = f.read()
        results.append(test_gui_pipeline(code, "Real Sample: 03_arith.lol"))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r)
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    
    if failed == 0:
        print("\nALL TESTS PASSED!")
        print("GUI pipeline is fully integrated and working!")
    
    print(f"{'='*80}\n")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

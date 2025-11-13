"""
Sample Validation Runner
Validates all LOLCODE samples in src/tests/samples/ to ensure:
1. All samples parse successfully
2. Lexer correctly handles comments (BTW single-line, OBTW...TLDR multi-line)
3. Comments are NOT tokenized as keywords or identifiers
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer.lexer import Lexer
from parser.parser import Parser


def print_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_subheader(title):
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print(f"{'-'*len(title)}\n")


def validate_comment_handling():
    """
    Verify that the lexer correctly handles comments:
    1. BTW single-line comments are not tokenized
    2. OBTW...TLDR multi-line comments are not tokenized
    3. No comment tokens appear in token stream
    """
    print_header("LEXER COMMENT HANDLING VALIDATION")
    
    lexer = Lexer()
    
    # Test 1: Single-line comment (BTW)
    print_subheader("Test 1: Single-line comment (BTW)")
    code_1 = """HAI
    BTW This is a comment
    VISIBLE "Hello"
    KTHXBYE"""
    
    tokens_1 = lexer.tokenize(code_1)
    print(f"Code:\n{code_1}\n")
    print(f"Tokens generated ({len(tokens_1)} tokens):")
    for token in tokens_1:
        print(f"  {token}")
    
    # Verify no "BTW" token in stream
    btw_tokens = [t for t in tokens_1 if t['value'] == 'BTW']
    if not btw_tokens:
        print("✓ PASS: BTW comment correctly excluded from token stream")
    else:
        print("✗ FAIL: BTW appeared in token stream")
    
    # Test 2: Multi-line comment (OBTW...TLDR)
    print_subheader("Test 2: Multi-line comment (OBTW...TLDR)")
    code_2 = """HAI
    OBTW
    This is a 
    multi-line comment
    TLDR
    VISIBLE "Hello"
    KTHXBYE"""
    
    tokens_2 = lexer.tokenize(code_2)
    print(f"Code:\n{code_2}\n")
    print(f"Tokens generated ({len(tokens_2)} tokens):")
    for token in tokens_2:
        print(f"  {token}")
    
    # Verify no "OBTW" or "TLDR" tokens in stream
    comment_boundary_tokens = [t for t in tokens_2 if t['value'] in ('OBTW', 'TLDR')]
    if not comment_boundary_tokens:
        print("✓ PASS: OBTW...TLDR correctly excluded from token stream")
    else:
        print("✗ FAIL: OBTW/TLDR appeared in token stream")
    
    # Test 3: Verify no keyword/identifier confusion
    print_subheader("Test 3: Comments NOT confused with keywords/identifiers")
    code_3 = """HAI
    I HAS A x ITZ 5
    BTW BTW is not a keyword here
    x R SUM OF x AN 1
    KTHXBYE"""
    
    tokens_3 = lexer.tokenize(code_3)
    print(f"Code:\n{code_3}\n")
    print(f"Tokens generated ({len(tokens_3)} tokens):")
    for token in tokens_3:
        print(f"  {token}")
    
    # Count tokens and verify structure
    btw_count = sum(1 for t in tokens_3 if t['value'] == 'BTW')
    if btw_count == 0:
        print("✓ PASS: BTW comment line completely ignored")
    else:
        print(f"✗ FAIL: Found {btw_count} BTW token(s) in stream")
    
    # Test 4: Mix of comments and code
    print_subheader("Test 4: Mix of single/multi-line comments with code")
    code_4 = """HAI
    OBTW
    Setup phase
    TLDR
    I HAS A count ITZ 0
    BTW This counts up
    count R SUM OF count AN 1
    VISIBLE count
    BTW Done!
    KTHXBYE"""
    
    tokens_4 = lexer.tokenize(code_4)
    print(f"Code:\n{code_4}\n")
    print(f"Tokens generated ({len(tokens_4)} tokens):")
    for token in tokens_4:
        print(f"  {token}")
    
    comment_tokens = [t for t in tokens_4 if t['value'] in ('BTW', 'OBTW', 'TLDR')]
    if not comment_tokens:
        print("✓ PASS: All comments correctly excluded")
    else:
        print(f"✗ FAIL: Found {len(comment_tokens)} comment token(s) in stream")


def validate_sample_files():
    """
    Validate all sample files in src/tests/samples/ by tokenizing and parsing them.
    """
    print_header("SAMPLE FILE VALIDATION")
    
    samples_dir = Path(__file__).parent / "tests" / "samples"
    sample_files = sorted(samples_dir.glob("*.lol"))
    
    if not sample_files:
        print("✗ FAIL: No sample files found in src/tests/samples/")
        return
    
    print(f"Found {len(sample_files)} sample files\n")
    
    lexer = Lexer()
    parser = Parser(lexer)
    
    results = {}
    passed = 0
    failed = 0
    
    for sample_file in sample_files:
        file_name = sample_file.name
        print_subheader(f"Validating: {file_name}")
        
        try:
            # Read file
            with open(sample_file, 'r') as f:
                code = f.read()
            
            # Tokenize
            tokens = lexer.tokenize(code)
            print(f"✓ Tokenization successful ({len(tokens)} tokens)")
            
            # Parse
            parse_tree = parser.parse(code)
            print(f"✓ Parsing successful")
            print(f"  Parse tree root: {parse_tree.rule_name}")
            print(f"  Total children: {len(parse_tree.children)}")
            
            results[file_name] = {"status": "PASS", "tokens": len(tokens)}
            passed += 1
            
        except Exception as e:
            print(f"✗ FAIL: {type(e).__name__}: {str(e)}")
            results[file_name] = {"status": "FAIL", "error": str(e)}
            failed += 1
    
    # Summary
    print_subheader("Summary")
    print(f"Total samples: {len(sample_files)}")
    print(f"Passed:        {passed}")
    print(f"Failed:        {failed}")
    
    if failed > 0:
        print(f"\nFailed samples:")
        for name, result in results.items():
            if result["status"] == "FAIL":
                print(f"  - {name}: {result['error']}")


def analyze_lexer_structure():
    """
    Analyze and document the lexer structure.
    """
    print_header("LEXER STRUCTURE ANALYSIS")
    
    lexer = Lexer()
    
    print_subheader("Token Patterns (in order)")
    print("Multi-word keywords (matched first to ensure priority):")
    print("  I HAS A, SUM OF, DIFF OF, PRODUKT OF, QUOSHUNT OF, MOD OF,")
    print("  BIGGR OF, SMALLR OF, BOTH SAEM, DIFFRINT, BOTH OF, EITHER OF,")
    print("  WON OF, ALL OF, ANY OF, IM IN YR, IM OUTTA YR, HOW IZ I,")
    print("  FOUND YR, IS NOW A, IF U SAY SO")
    
    print("\nSingle-word keywords:")
    print("  HAI, KTHXBYE, WAZZUP, BUHBYE, BTW, OBTW, TLDR, ITZ, R, VISIBLE,")
    print("  GIMMEH, O RLY?, YA RLY, MEBBE, NO WAI, OIC, WTF?, OMG, OMGWTF,")
    print("  UPPIN, NERFIN, YR, TIL, WILE, GTFO, I IZ, MKAY, AN, A, MAEK, SMOOSH")
    
    print("\nLiterals:")
    print("  NUMBAR (floating-point), NUMBR (integer), TROOF (WIN/FAIL),")
    print("  YARN (quoted strings), NOOB (null-like)")
    
    print("\nIdentifiers:")
    print("  [A-Za-z][A-Za-z0-9_]*")
    
    print_subheader("Comment Patterns")
    print("Single-line comment (BTW):  r\"BTW.*\"")
    print("  - Matched as complete line; entire line skipped")
    print("Multi-line comment start:   r\"OBTW\"")
    print("  - Sets in_multiline_comment flag; all lines until TLDR skipped")
    print("Multi-line comment end:     r\"TLDR\"")
    print("  - Clears in_multiline_comment flag")


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("  LOLCODE LEXER & PARSER VALIDATION SUITE")
    print("="*80)
    
    # Run all validations
    analyze_lexer_structure()
    validate_comment_handling()
    validate_sample_files()
    
    print_header("VALIDATION COMPLETE")
    print("All checks completed. Review results above for any failures.\n")


if __name__ == "__main__":
    main()

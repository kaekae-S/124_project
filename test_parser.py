#!/usr/bin/env python3
"""
Simple test runner for the parser.
Parses LOLCODE sample files and prints parse tree structure.
"""

import sys
import os

# Add src to path so we can import lexer and parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.lexer import Lexer
from parser.parser import Parser


def print_tree(node, indent=0):
    """Recursively print parse tree structure."""
    prefix = "  " * indent
    print(f"{prefix}{node}")
    if hasattr(node, 'children'):
        for child in node.children:
            print_tree(child, indent + 1)


def test_parse_file(filepath):
    """Parse a LOLCODE file and print results."""
    print(f"\n{'='*60}")
    print(f"Parsing: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        print(f"\nSource code:\n{code}\n")
        
        # Tokenize
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        print(f"\nTokens ({len(tokens)} total):")
        for i, token in enumerate(tokens[:20]):  # Show first 20 tokens
            print(f"  {i}: {token}")
        if len(tokens) > 20:
            print(f"  ... ({len(tokens) - 20} more tokens)")
        
        # Parse
        parser = Parser(lexer)
        parse_tree = parser.parse(code)
        
        print(f"\nParse tree:")
        print_tree(parse_tree)
        
        print(f"\n✓ Parse successful!")
        return True
    
    except SyntaxError as e:
        print(f"\n✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run parser tests on sample files."""
    samples_dir = os.path.join(os.path.dirname(__file__), 'src', 'tests', 'samples')
    
    # Test files to run
    test_files = [
        '01_variables.lol',
        '02_gimmeh.lol',
        '03_arith.lol',
    ]
    
    results = []
    for filename in test_files:
        filepath = os.path.join(samples_dir, filename)
        if os.path.exists(filepath):
            success = test_parse_file(filepath)
            results.append((filename, success))
        else:
            print(f"\n✗ File not found: {filepath}")
            results.append((filename, False))
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for filename, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {filename}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nPassed: {passed}/{len(results)}")


if __name__ == '__main__':
    main()

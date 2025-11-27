"""
Comprehensive Sample File Validation

Purpose: Test all sample LOLCODE files against the compiler pipeline

Validates that:
- Valid programs parse and pass semantic analysis
- Programs with errors are correctly detected
- Complete pipeline (Lexer → Parser → Semantic) works end-to-end

Sample Coverage: 18 test files from tests/samples/
Results show which files pass and any errors detected

"""

import sys
import os
sys.path.insert(0, 'src')

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer
from pathlib import Path


def analyze_file(filepath):
    """Analyze a single LOLCODE file through the complete pipeline.
    
    Runs: Lexer - tokenizes, Parser - builds AST, Semantic Analyzer - validates
    
    Args:
        filepath (str): Path to .lol file
        
    Returns:
        dict: Contains success status, errors, token count, line count
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lexer = Lexer()
        parser = Parser(lexer)
        semantic_analyzer = SemanticAnalyzer()
        
        # Stage 1: Tokenize
        tokens = lexer.tokenize(code)
        
        # Stage 2: Parse
        tree = parser.parse(code)
        
        # Stage 3: Semantic analysis
        semantic_errors = semantic_analyzer.analyze(tree)
        
        return {
            'success': len(semantic_errors) == 0,
            'errors': semantic_errors,
            'tokens': len(tokens),
            'lines': len(code.split('\n')),
            'syntax_error': None
        }
    except SyntaxError as e:
        return {
            'success': False,
            'errors': [],
            'syntax_error': str(e),
            'tokens': 0,
            'lines': len(code.split('\n')) if 'code' in locals() else 0
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [],
            'syntax_error': f"{type(e).__name__}: {str(e)}",
            'tokens': 0,
            'lines': len(code.split('\n')) if 'code' in locals() else 0
        }


def main():
    """Validate all sample LOLCODE files against the compiler pipeline.
    
    Tests complete Lexer-Parser-Semantic flow on each sample file.
    Reports which files pass validation and any errors detected.
    """
    
    print("=" * 80)
    print("COMPREHENSIVE SEMANTIC VALIDATION TEST")
    print("=" * 80)
    print("")
    
    samples_dir = Path('src/tests/samples')
    if not samples_dir.exists():
        print(f"ERROR: Sample directory not found at {samples_dir}")
        return False
    
    sample_files = sorted(samples_dir.glob('*.lol'))
    
    print(f"Found {len(sample_files)} sample files\n")
    
    results = []
    
    for sample_file in sample_files:
        filename = sample_file.name
        result = analyze_file(sample_file)
        results.append((filename, result))
        
        # Display result
        status = "PASS" if result['success'] else "FAIL"
        print(f"[{status}] {filename:<25} Lines: {result['lines']:<3} Tokens: {result['tokens']:<4}")
        
        if result['syntax_error']:
            print(f"      Syntax Error: {result['syntax_error'][:70]}")
        
        if result['errors']:
            print(f"      Semantic Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"        - {error}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    valid_files = sum(1 for _, r in results if r['success'])
    total_files = len(results)
    
    print(f"\nTotal Sample Files: {total_files}")
    print(f"Valid Programs:    {valid_files}")
    print(f"Error Programs:    {total_files - valid_files}")
    
    # Breakdown
    syntax_errors = sum(1 for _, r in results if r['syntax_error'])
    semantic_errors = sum(1 for _, r in results if r['errors'] and not r['syntax_error'])
    
    if syntax_errors > 0:
        print(f"\nSyntax Errors:     {syntax_errors}")
    if semantic_errors > 0:
        print(f"Semantic Errors:   {semantic_errors}")
    
    # Show all captures semantic errors
    print("\n" + "-" * 80)
    print("SEMANTIC ERROR TYPES DETECTED:")
    print("-" * 80)
    
    error_types = {}
    for _, result in results:
        for error in result['errors']:
            error_type = error.split(':')[-1].strip() if ':' in error else error
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
    
    if error_types:
        for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"  - {error_type:<50} Count: {count}")
    else:
        print("  No semantic errors found in samples")
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

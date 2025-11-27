"""
Comprehensive Sample File Semantic Validation
Purpose: Validate semantic correctness of all sample LOLCODE files

Tests the complete parsing and semantic analysis pipeline on sample files.
Run from project root: python validate_semantic_all.py

Results show files that pass validation and any semantic errors found.
"""

import sys
import os
sys.path.insert(0, 'src')

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer
from pathlib import Path


def validate_sample(filepath):
    """Validate a single LOLCODE file through parse and semantic stages.
        
    Returns:
        tuple: (filename: str, success: bool, errors: list of error strings)
    """
    filename = os.path.basename(filepath)
    
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Parse code into AST
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        # Analyze semantics
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(tree)
        
        return filename, len(errors) == 0, errors
    
    except Exception as e:
        return filename, False, [f"Parse/Analysis Error: {str(e)}"]


def main():
    """Validate all samples and print report."""
    samples_dir = Path('src/tests/samples')
    
    if not samples_dir.exists():
        print(f"ERROR: Samples directory not found: {samples_dir}")
        return False
    
    # Find all .lol files
    sample_files = sorted(samples_dir.glob('*.lol'))
    
    if not sample_files:
        print(f"ERROR: No .lol files found in {samples_dir}")
        return False
    
    # Validate each sample
    results = []
    for filepath in sample_files:
        filename, success, errors = validate_sample(str(filepath))
        results.append((filename, success, errors))
    
    # Print report
    print("=" * 80)
    print("SEMANTIC VALIDATION REPORT - ALL SAMPLES")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for filename, success, errors in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}  {filename}")
        if errors:
            for error in errors:
                print(f"      └─ {error}")
            failed += 1
        else:
            passed += 1
    
    print()
    print("=" * 80)
    print(f"Total: {len(results)} samples")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

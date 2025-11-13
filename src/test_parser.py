

import os
import sys

from lexer.lexer import Lexer
from parser.parser import Parser


def print_node(node, indent=0):
    prefix = "  " * indent
    try:
        print(f"{prefix}{node}")
    except Exception:
        print(f"{prefix}{type(node).__name__}")
    for child in getattr(node, 'children', []) or []:
        print_node(child, indent + 1)


def run_code_and_report(code, name, lexer, parser):
    print('\n' + '-' * 60)
    print('TEST:', name)
    print('-' * 60)
    try:
        tokens = lexer.tokenize(code)
        print('  tokens:', len(tokens))
    except Exception as e:
        print('  tokenization error:', e)
        return
    try:
        tree = parser.parse(code)
        print('  parse: OK')
        print_node(tree, indent=1)
    except Exception as e:
        print('  parse: ERROR ->', e)


def main():
    # Basic runner over samples directory
    base = os.path.dirname(__file__)
    samples_dir = os.path.normpath(os.path.join(base, 'tests', 'samples'))
    if not os.path.isdir(samples_dir):
        print('ERROR: samples directory not found:', samples_dir)
        sys.exit(1)

    lexer = Lexer()
    parser = Parser(lexer)

    # Run the full sample suite
    sample_files = sorted([f for f in os.listdir(samples_dir) if f.endswith('.lol')])
    for fname in sample_files:
        path = os.path.join(samples_dir, fname)
        with open(path, 'r', encoding='utf-8') as fh:
            code = fh.read()
        run_code_and_report(code, fname, lexer, parser)

    # Additional targeted tests for input & comparison edge cases
    extra_tests = {
        'gimmeh_single': 'HAI\nGIMMEH target\nKTHXBYE',
        'gimmeh_multiple': 'HAI\nGIMMEH a AN b AN c\nKTHXBYE',
        'bothsaem_nested': 'HAI\nVISIBLE BOTH SAEM BOTH SAEM 1 AN 1 AN 0\nKTHXBYE',
        'diffrint_exprs': 'HAI\nVISIBLE DIFFRINT SUM OF 1 AN 2 AN DIFFRINT 3 AN 4\nKTHXBYE',
    }

    for name, code in extra_tests.items():
        run_code_and_report(code, name, lexer, parser)

    print('\nAll tests completed.')


if __name__ == '__main__':
    main()


"""
Parser smoke-test runner (new file).
This iterates samples in src/tests/samples, tokenizes and parses each file,
then prints a compact parse-tree summary.
"""

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


def main():
    base = os.path.dirname(__file__)
    samples_dir = os.path.normpath(os.path.join(base, 'tests', 'samples'))
    if not os.path.isdir(samples_dir):
        print('ERROR: samples directory not found:', samples_dir)
        sys.exit(1)

    sample_files = sorted([f for f in os.listdir(samples_dir) if f.endswith('.lol')])
    if not sample_files:
        print('No .lol files found in', samples_dir)
        return

    lexer = Lexer()
    parser = Parser(lexer)

    for fname in sample_files:
        path = os.path.join(samples_dir, fname)
        print('\n' + '=' * 60)
        print('FILE:', fname)
        print('=' * 60)
        with open(path, 'r', encoding='utf-8') as fh:
            code = fh.read()
        try:
            tokens = lexer.tokenize(code)
            print('  tokens:', len(tokens))
        except Exception as e:
            print('  tokenization error:', e)
            continue

        try:
            tree = parser.parse(code)
            print('  parse: OK')
            print_node(tree, indent=1)
        except Exception as e:
            print('  parse: ERROR ->', e)

    print('\nAll samples processed.')


if __name__ == '__main__':
    main()

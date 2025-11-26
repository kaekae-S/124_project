import sys
sys.path.insert(0, 'src')
from lexer.lexer import Lexer
from parser.parser import Parser

path = 'src/tests/samples/05_bool.lol'
code = open(path).read()
print('=== SOURCE ===')
print(code)

lexer = Lexer()
tokens = lexer.tokenize(code)
print('\n=== TOKENS AROUND LINE 16 ===')
for t in tokens:
    if t['line'] >= 12 and t['line'] <= 20:
        print(t)

print('\n=== PARSE ATTEMPT ===')
parser = Parser(lexer)
try:
    tree = parser.parse(code)
    print('Parsed successfully')
    stmts = getattr(tree, 'statements_node', None)
    if stmts:
        print('Number of statements:', len(getattr(stmts,'statements',[])))
except Exception as e:
    print('Parser error:', e)
    # show current position token if available
    try:
        ct = parser.current_token
        print('Current token at error:', ct)
    except Exception:
        pass

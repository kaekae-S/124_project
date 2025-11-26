from lexer.lexer import Lexer
import sys
p = sys.argv[1]
with open(p, encoding='utf-8') as f:
    s = f.read()
lex = Lexer()
for t in lex.tokenize(s):
    print(t)

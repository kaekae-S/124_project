import sys
sys.path.insert(0, 'src')

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer

code = open('src/tests/samples/02_gimmeh.lol').read()
print("=== CODE ===")
print(code)
print("\n=== PARSING ===")

lexer = Lexer()
parser = Parser(lexer)
parse_tree = parser.parse(code)

print("Parse tree obtained")
stmts = getattr(parse_tree, 'statements_node', None)
if stmts:
    print(f"Number of statements: {len(getattr(stmts, 'statements', []))}")
    for i, stmt in enumerate(getattr(stmts, 'statements', [])):
        rule_name = getattr(stmt, 'rule_name', 'N/A')
        print(f"  Statement {i}: {type(stmt).__name__} rule={rule_name}")
        # Try to unwrap and see inner
        if hasattr(stmt, 'children') and stmt.children:
            inner = stmt.children[0]
            inner_rule = getattr(inner, 'rule_name', 'N/A')
            print(f"    -> Inner: {type(inner).__name__} rule={inner_rule}")

print("\n=== WAZZUP STRUCTURE ===")
wazzup_stmt = getattr(stmts, 'statements', [])[0]
print(f"WAZZUP statement: rule={getattr(wazzup_stmt, 'rule_name', 'N/A')}")
if hasattr(wazzup_stmt, 'children'):
    for i, c in enumerate(wazzup_stmt.children):
        c_rule = getattr(c, 'rule_name', 'N/A')
        print(f"  Child {i}: {type(c).__name__} rule={c_rule}")
        if hasattr(c, 'children'):
            for j, cc in enumerate(c.children[:5]):  # first 5 children
                cc_rule = getattr(cc, 'rule_name', 'N/A')
                print(f"    Grandchild {j}: {type(cc).__name__} rule={cc_rule}")

print("\n=== SEMANTIC ANALYSIS ===")
analyzer = SemanticAnalyzer()
print(f"Before analyze: scopes={len(analyzer.scopes)}")
errors = analyzer.analyze(parse_tree)
print(f"After analyze: scopes={len(analyzer.scopes)}")

if analyzer.scopes:
    print(f"Global scope vars: {analyzer.scopes[0]}")
    if len(analyzer.scopes) > 1:
        for i, scope in enumerate(analyzer.scopes[1:], 1):
            print(f"Scope {i}: {scope}")
else:
    print("ERROR: No scopes!")
    
print(f"Errors ({len(errors)}): {errors}")

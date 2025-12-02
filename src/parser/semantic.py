"""
Semantic Analyzer for LOLCODE

Project: 124 - LOLCODE Compiler/Interpreter


The semantic analyzer performs two passes over the parse tree:
1. Collection Pass: Gathers all variable and function declarations
2. Validation Pass: Checks for semantic errors

Comprehensive Error Detection:
- Undefined variables: Using variables before declaration
- Duplicate declarations: Redeclaring same variable in same scope
- Function errors: Undefined calls, arity mismatches, duplicate definitions
- Control flow errors: GTFO (break) outside loops, FOUND YR (return) outside functions
- Assignment errors: Assigning to undeclared variables
- Input errors: Reading input into undeclared variables

Design Pattern - Two-Pass Analysis:
Reference: https://www.geeksforgeeks.org/compiler-design/single-pass-two-pass-and-multi-pass-compilers/
Pass 1 ensures all symbols exist before validation checks in Pass 2, allowing
forward references and handling WAZZUP blocks that declare globals from anywhere.

Scope Management:
- Stack of scopes (global + nested blocks/functions)
- Function tracking with arity (parameter count)
- Loop depth counter for break statement validation
""" 

from typing import List, Dict, Any


class SemanticAnalyzer:
    def __init__(self):
        self.errors: List[str] = []
        # Stack of scopes; each scope maps variable -> metadata dict
        # metadata: { 'declared': bool, 'assigned': bool, 'type': Optional[str] }
        self.scopes: List[Dict[str, Dict[str, Any]]] = []
        # Functions: name -> parameter_count
        self.functions: Dict[str, int] = {}
        # Track if we're inside a function
        self.in_function: bool = False
        # Track if we're inside a loop
        self.in_loop: int = 0  # depth counter for nested loops

    def analyze(self, program_node) -> List[str]:
        """Entry point. program_node is the root parse tree returned by Parser.parse()."""
        self.errors = []
        self.scopes = [{}]  # global scope
        self.functions = {}

        # Parser sets a `statements_node` attribute on the Program node
        stmts = getattr(program_node, 'statements_node', None)
        if not stmts:
            return self.errors

        # statements_node typically has attribute `statements` (list)
        # First pass: collect all variable declarations (including from WAZZUP blocks)
        # This ensures that variables declared in WAZZUP are available globally
        for stmt in getattr(stmts, 'statements', []):
            self._collect_declarations(stmt)

        # Second pass: analyze the program with all declarations available
        for stmt in getattr(stmts, 'statements', []):
            self._visit_statement_wrapper(stmt)

        return self.errors

    def _collect_declarations(self, stmt_node):
        """First pass: collect all variable and function declarations from entire program."""
        if not stmt_node:
            return
        
        name = getattr(stmt_node, 'rule_name', stmt_node.__class__.__name__)
        
        # Check if this node itself is what we're looking for
        if name in ('VariableDeclaration', 'VariableDeclarationNode'):
            ident = getattr(stmt_node, 'identifier_node', None)
            var_name = self._get_identifier_name(ident)
            line = getattr(ident, 'line', None) or (ident.token['line'] if getattr(ident, 'token', None) else None)
            if var_name:
                self._declare_var(var_name, line)
            return
        
        # Handle StatementNode wrapper - unwrap it first
        elif name == 'Statement':
            # StatementNode wrapper contains the actual statement as children[0]
            if hasattr(stmt_node, 'children') and stmt_node.children:
                inner = stmt_node.children[0]
                if inner:
                    self._collect_declarations(inner)
            return
        
        elif name == 'WAZZUP_Block':
            # Recursively collect from WAZZUP block's children (which include statements)
            for c in getattr(stmt_node, 'children', []) or []:
                self._collect_declarations(c)
            return
        
        elif name in ('Function', 'FunctionNode'):
            # Don't collect nested declarations from function bodies in first pass
            return
        
        # Skip token nodes (WAZZUP, BUHBYE, HAI, KTHXBYE, etc.)
        elif name in ('WAZZUP', 'BUHBYE', 'HAI', 'KTHXBYE', 'I_HAS_A', 'ITZ', 'R', 'VISIBLE', 'GIMMEH'):
            return
        
        # For other nodes, recursively check children
        for c in getattr(stmt_node, 'children', []) or []:
            self._collect_declarations(c)

    # --- Scope helpers
    def _enter_scope(self):
        self.scopes.append({})

    def _exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def _declare_var(self, name: str, line: Any = None):
        cur = self.scopes[-1]
        if name in cur:
            self._error(f"Duplicate declaration of variable '{name}'", line)
        else:
            cur[name] = {'declared': True, 'assigned': False, 'type': None}

    def _is_declared(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def _is_assigned(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return bool(scope[name].get('assigned', False))
        return False

    def _mark_assigned(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['assigned'] = True
                return

    def _set_var_type(self, name: str, var_type: str):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['type'] = var_type
                return

    def _get_var_type(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name].get('type')
        return None

    def _declare_function(self, name: str, arity: int, line: Any = None):
        if name in self.functions:
            self._error(f"Duplicate function definition '{name}'", line)
        else:
            self.functions[name] = arity

    # --- Error helper
    def _error(self, msg: str, line: Any = None):
        if line is not None:
            try:
                self.errors.append(f"Line {line}: {msg}")
            except Exception:
                self.errors.append(str(msg))
        else:
            self.errors.append(str(msg))

    # --- Visitors
    def _visit_statement_wrapper(self, stmt_node):
        # Many statements are wrapped in a StatementNode with a single child
        if not stmt_node:
            return
        # Try to find the inner statement
        inner = None
        if hasattr(stmt_node, 'children') and stmt_node.children:
            inner = stmt_node.children[0]
        else:
            inner = stmt_node

        if inner is None:
            return

        name = getattr(inner, 'rule_name', inner.__class__.__name__)
        # Dispatch based on node type name
        if name in ('VariableDeclaration', 'VariableDeclarationNode'):
            self._visit_variable_declaration(inner)
        elif name in ('Assignment', 'AssignmentNode'):
            self._visit_assignment(inner)
        elif name in ('InputStatement', 'InputStatementNode'):
            self._visit_input_statement(inner)
        elif name in ('PrintStatement', 'PrintStatementNode'):
            self._visit_print_statement(inner)
        elif name in ('Function', 'FunctionNode'):
            self._visit_function_declaration(inner)
        elif name in ('FunctionCall', 'FunctionCallNode'):
            self._visit_function_call(inner)
        elif name in ('Loop', 'LoopNode'):
            self._visit_loop(inner)
        elif name in ('Conditional', 'ConditionalNode'):
            self._visit_conditional(inner)
        elif name in ('Switch', 'SwitchNode'):
            self._visit_switch(inner)
        elif name in ('Break', 'BreakNode', 'GTFO'):
            # Check if break is inside a loop
            line = getattr(inner, 'line', None)
            if self.in_loop == 0:
                self._error("'GTFO' (break) statement used outside of a loop", line)
        elif name == 'WAZZUP_Block':
            # WAZZUP...BUHBYE is just a grouping block in global scope, not a new scope.
            # Visit all statements inside it directly (don't create new scope).
            for c in getattr(inner, 'children', []) or []:
                c_rule = getattr(c, 'rule_name', None)
                # Process Statement wrappers and actual statement nodes
                if c_rule == 'Statement':
                    self._visit_statement_wrapper(c)
                elif c_rule in ('VariableDeclaration', 'Assignment', 'InputStatement', 'Function', 'FunctionCall', 'Loop', 'Conditional', 'Switch'):
                    self._visit_statement_wrapper(c)
                # Skip token nodes like WAZZUP, BUHBYE
                elif c_rule not in ('WAZZUP', 'BUHBYE'):
                    self._visit_node(c)
        else:
            # Generic visit of children
            for c in getattr(inner, 'children', []) or []:
                # If child looks like a statement, visit as statement wrapper
                if getattr(c, 'rule_name', None) in ('VariableDeclaration', 'Assignment', 'InputStatement', 'Function', 'FunctionCall', 'Loop', 'Conditional', 'Switch'):
                    self._visit_statement_wrapper(c)
                else:
                    self._visit_node(c)

    def _visit_variable_declaration(self, node):
        # Note: Variables were already declared in first pass (_collect_declarations)
        # So we don't call _declare_var here - that would cause duplicate errors!
        # Just visit the initializer expression if present to check for undefined references
        
        expr = getattr(node, 'expression_node', None)
        if expr:
            self._visit_node(expr)

    def _visit_assignment(self, node):
        ident = getattr(node, 'identifier_node', None)
        name = self._get_identifier_name(ident)
        line = getattr(ident, 'line', None) or (ident.token['line'] if getattr(ident, 'token', None) else None)
        if not name:
            self._error("Assignment to unknown identifier (missing name)", line)
            return
        if not self._is_declared(name):
            self._error(f"Assignment to undeclared variable '{name}'", line)

        # Visit RHS expression
        expr = getattr(node, 'expression_node', None)
        if expr:
            self._visit_node(expr)

    def _visit_input_statement(self, node):
        # node.identifier_nodes is a list of Identifier nodes
        ids = getattr(node, 'identifier_nodes', []) or []
        for ident in ids:
            name = self._get_identifier_name(ident)
            line = getattr(ident, 'line', None) or (ident.token['line'] if getattr(ident, 'token', None) else None)
            if not self._is_declared(name):
                self._error(f"Input target '{name}' is not declared", line)

    def _visit_print_statement(self, node):
        expr = getattr(node, 'expression_node', None)
        if expr:
            self._visit_node(expr)

    def _visit_function_declaration(self, node):
        # Register function first
        fn_node = getattr(node, 'function_name', None)
        fn_name = self._get_identifier_name(fn_node)
        params = getattr(node, 'parameters', []) or []
        arity = len(params)
        line = getattr(fn_node, 'line', None) or (fn_node.token['line'] if getattr(fn_node, 'token', None) else None)
        if fn_name:
            self._declare_function(fn_name, arity, line)

        # Analyze function body in new scope
        self._enter_scope()
        prev_in_function = self.in_function
        self.in_function = True
        
        # declare parameters in function scope
        for p in params:
            pname = self._get_identifier_name(p)
            pline = getattr(p, 'line', None) or (p.token['line'] if getattr(p, 'token', None) else None)
            if pname:
                self._declare_var(pname, pline)

        # Visit body statements
        for s in getattr(node, 'body_statements', []) or []:
            self._visit_statement_wrapper(s)

        # Visit return expression
        ret = getattr(node, 'return_expr', None)
        if ret:
            self._visit_node(ret)

        self._exit_scope()
        self.in_function = prev_in_function

    def _visit_function_call(self, node):
        fn_node = getattr(node, 'function_name', None)
        fn_name = self._get_identifier_name(fn_node)
        line = getattr(fn_node, 'line', None) or (fn_node.token['line'] if getattr(fn_node, 'token', None) else None)
        args = getattr(node, 'arguments', []) or []
        # Visit argument expressions
        for a in args:
            self._visit_node(a)

        if fn_name:
            if fn_name not in self.functions:
                self._error(f"Call to undefined function '{fn_name}'", line)
            else:
                expected = self.functions[fn_name]
                if len(args) != expected:
                    self._error(f"Function '{fn_name}' called with {len(args)} arg(s) but expects {expected}", line)

    def _visit_loop(self, node):
        # loop.var_node may be a ParseTreeNode("Variable", [], token) or similar
        var_node = getattr(node, 'var_node', None)
        var_name = None
        if var_node is not None:
            # try to get token value
            if getattr(var_node, 'token', None):
                var_name = var_node.token.get('value')
            else:
                var_name = self._get_identifier_name(var_node)

        # Loop variable must be pre-declared (according to LOLCODE semantics)
        if var_name and not self._is_declared(var_name):
            self._error(f"Loop variable '{var_name}' is not declared", getattr(var_node, 'line', None))

        # Visit condition (in current scope)
        cond = getattr(node, 'condition_node', None)
        if cond:
            self._visit_node(cond)

        # Visit body statements in a new scope (loop block scope)
        self.in_loop += 1
        self._enter_scope()
        for s in getattr(node, 'body_statements', []) or []:
            self._visit_statement_wrapper(s)
        self._exit_scope()
        self.in_loop -= 1

    def _visit_conditional(self, node):
        # condition_expr, ya_rly_statements, mebbe_blocks, no_wai_statements
        cond = getattr(node, 'condition_expr', None)
        if cond:
            self._visit_node(cond)

        # YA RLY block in new scope
        self._enter_scope()
        for s in getattr(node, 'ya_rly_statements', []) or []:
            self._visit_statement_wrapper(s)
        self._exit_scope()

        # MEBBE blocks may be list of (expr, stmts)
        for mebbe in getattr(node, 'mebbe_blocks', []) or []:
            expr, stmts = mebbe
            if expr:
                self._visit_node(expr)
            self._enter_scope()
            for s in stmts or []:
                self._visit_statement_wrapper(s)
            self._exit_scope()

        # NO WAI block
        self._enter_scope()
        for s in getattr(node, 'no_wai_statements', []) or []:
            self._visit_statement_wrapper(s)
        self._exit_scope()

    def _visit_switch(self, node):
        # switch_expr, omg_cases(list of (expr, stmts)), omgwtf_statements
        switch_expr = getattr(node, 'switch_expr', None)
        if switch_expr:
            self._visit_node(switch_expr)

        for case in getattr(node, 'omg_cases', []) or []:
            expr, stmts = case
            if expr:
                self._visit_node(expr)
            self._enter_scope()
            for s in stmts or []:
                self._visit_statement_wrapper(s)
            self._exit_scope()

        for s in getattr(node, 'omgwtf_statements', []) or []:
            self._visit_statement_wrapper(s)

    def _visit_node(self, node):
        if node is None:
            return
        # If node is one of the specialized classes, handle accordingly
        cls_name = getattr(node, 'rule_name', None) or node.__class__.__name__

        # Literal: nothing to check
        if cls_name in ('Literal',) or getattr(node, 'token', None) and node.token.get('type') in ('NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB'):
            return

        if cls_name in ('Variable', 'VariableNode'):
            # Variable may wrap an Identifier node
            ident = getattr(node, 'identifier_node', None) or getattr(node, 'token', None)
            name = self._get_identifier_name(ident)
            line = getattr(node, 'line', None) or (ident.token['line'] if getattr(ident, 'token', None) else None)
            if name and not self._is_declared(name):
                self._error(f"Use of undeclared variable '{name}'", line)
            return

        # FunctionCall
        if cls_name in ('FunctionCall', 'FunctionCallNode'):
            self._visit_function_call(node)
            return

        # BinaryExpression: visit left/right
        if cls_name in ('BinaryExpression', 'BinaryExpressionNode'):
            left = getattr(node, 'left_node', None)
            right = getattr(node, 'right_node', None)
            # some BinaryExpressionNodes have operator node and an_node present
            if left:
                self._visit_node(left)
            if right:
                self._visit_node(right)
            return

        # BooleanExpression
        if cls_name in ('BooleanExpression', 'BooleanExpressionNode', 'Not'):
            for c in getattr(node, 'children', []) or []:
                self._visit_node(c)
            return

        # ReturnExpression (FOUND YR)
        if cls_name in ('ReturnExpression', 'ReturnExpressionNode', 'FoundYR'):
            line = getattr(node, 'line', None)
            if not self.in_function:
                self._error("'FOUND YR' (return) statement used outside of a function", line)
            # Visit the return expression value
            expr = getattr(node, 'expression_node', None) or getattr(node, 'value_node', None)
            if expr:
                self._visit_node(expr)
            return

        # Comparison or others - traverse children generically
        for child in getattr(node, 'children', []) or []:
            self._visit_node(child)

    # --- Utility
    def _get_identifier_name(self, node):
        if node is None:
            return None
        # Node may be ParseTreeNode with .token
        tok = getattr(node, 'token', None)
        if tok and isinstance(tok, dict) and 'value' in tok:
            return tok['value']
        # Or node could be a ParseTreeNode wrapping another identifier (e.g., parameter nodes)
        # Try to inspect children for token
        for c in getattr(node, 'children', []) or []:
            n = getattr(c, 'token', None)
            if n and isinstance(n, dict) and 'value' in n:
                return n['value']
        # Some parser created identifier nodes with value stored in a nested token attribute
        if hasattr(node, 'children') and node.children:
            for c in node.children:
                tok2 = getattr(c, 'token', None)
                if tok2 and isinstance(tok2, dict) and 'value' in tok2:
                    return tok2['value']
        return None
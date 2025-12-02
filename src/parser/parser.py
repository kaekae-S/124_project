"""
LOLCODE Parser - Recursive Descent Parser

Purpose: Convert token stream into abstract syntax tree (AST)

The parser implements a recursive descent parsing algorithm that:
1. Validates grammar structure (HAI...KTHXBYE)
2. Recognizes all LOLCODE language constructs (variables, functions, loops, conditionals)
3. Builds a parse tree for semantic analysis
4. Reports clear syntax errors with line numbers

Key Design Patterns:
- Each grammar rule has a dedicated parsing method (parse_statement, parse_expression, etc.)
- Methods handle both required terminals and optional constructs
- Error messages indicate expected vs. found tokens
- Parse tree nodes are structured for semantic validation pass

Reference: Recursive Descent Parsing is a top-down parsing technique where each
grammar rule is implemented as a function that recognizes that rule.
See: https://www.geeksforgeeks.org/compiler-design/recursive-descent-parser/
"""

from lexer.lexer import Lexer
from parser.parse_tree_nodes import (
    ParseTreeNode, ProgramNode, StatementListNode, StatementNode,
    VariableDeclarationNode, PrintStatementNode, InputStatementNode,
    ExpressionNode, BinaryExpressionNode, PrimaryExpressionNode,
    LiteralNode, VariableNode, ComparisonNode, BothSaemNode, DiffrintNode,
    AssignmentNode, TypecastAssignmentNode, BooleanExpressionNode, NotNode, LoopNode, ConditionalNode, SwitchNode,
    FunctionNode, FunctionCallNode
)


class Parser:
    """Recursive Descent Parser for LOLCODE grammar."""
    
    def __init__(self, lexer):
        """Initialize parser with lexer instance."""
        self.lexer = lexer
        self.tokens = []
        self.current_pos = 0
        self.current_token = None
        self.pending_comment = None  # Track pending comments for nodes
    
    def parse(self, code):
        """Parse LOLCODE source code into a parse tree.
        
        Entry point: Tokenizes code and builds the AST.
        Grammar: Program → HAI StatementList KTHXBYE
        
        Args:
            code (str): LOLCODE source code
            
        Returns:
            ParseTreeNode: Root node of the program tree
            
        Raises:
            SyntaxError: If code doesn't match LOLCODE grammar
        """
        # Tokenize the source code
        self.tokens = self.lexer.tokenize(code)
        self.current_pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
        # Parse the program structure: Program → HAI Statements KTHXBYE
        line = self.current_token['line'] if self.current_token else None
        
        # Skip leading comment tokens before checking for HAI
        while self.current_token and self.current_token['type'] == 'Comment':
            if not self.current_token.get('inline', False):
                self.pending_comment = self.current_token['value']
            self.advance()  # Move to next token
        
        # Parse HAI token (required to start program)
        if not self.current_token:
            raise SyntaxError("Line 1: Expected 'HAI' at start of program")
        if self.current_token['value'] != 'HAI':
            raise SyntaxError(f"Line {self.current_token['line']}: Expected 'HAI' at start of program, but found '{self.current_token['value']}'")
        hai_node = ParseTreeNode("HAI", [], self.current_token, line=self.current_token['line'])
        self.advance()
        
        # Parse statements between HAI and KTHXBYE
        statements_node = self.parse_statement_list()
        
        # Parse KTHXBYE token (required to end program)
        if not self.current_token:
            raise SyntaxError("Unexpected end of input. Expected 'KTHXBYE' at end of program")
        if self.current_token['value'] != 'KTHXBYE':
            raise SyntaxError(f"Line {self.current_token['line']}: Expected 'KTHXBYE' at end of program, but found '{self.current_token['value']}'")
        kthxbye_node = ParseTreeNode("KTHXBYE", [], self.current_token, line=self.current_token['line'])
        self.advance()
        
        # Check for any remaining tokens after KTHXBYE (skip trailing comments)
        while self.current_token and self.current_token['type'] == 'Comment':
            self.advance()
        
        # Error if there are tokens after KTHXBYE
        if self.current_token:
            raise SyntaxError(f"Line {self.current_token['line']}: Unexpected token '{self.current_token['value']}' after 'KTHXBYE'. Program must end after 'KTHXBYE'")
        
        # Build and return the Program node
        program_children = [hai_node, statements_node, kthxbye_node]
        program = ParseTreeNode("Program", program_children, line=line)
        program.statements_node = statements_node
        return program
    
    def parse_statement_list(self):
        """Parse StatementList → Statement* (KTHXBYE | BUHBYE).
        
        Collects and parses all statements until reaching program/block end markers.
        Handles WAZZUP (global variable blocks) and regular statements.
        
        Returns:
            StatementListNode: Contains all parsed statements
        """
        statements = []
        line = self.current_token['line'] if self.current_token else None
        
        # Loop until we hit KTHXBYE (program end) or BUHBYE (block end)
        while self.current_token and self.current_token['value'] != 'KTHXBYE' and self.current_token['value'] != 'BUHBYE':
            # Skip comment tokens
            if self.current_token and self.current_token['type'] == 'Comment':
                if not self.current_token.get('inline', False):
                    self.pending_comment = self.current_token['value']
                self.advance()
                continue
            
            # Handle WAZZUP global variable declaration block
            if self.current_token and self.current_token['value'] == 'WAZZUP':
                # Parse WAZZUP block
                wazzup_line = self.current_token['line']
                wazzup_node = ParseTreeNode("WAZZUP", [], self.current_token, line=wazzup_line)
                self.advance()
                
                # Parse statements in WAZZUP block
                wazzup_statements = []
                while self.current_token and self.current_token['value'] != 'BUHBYE' and self.current_token['value'] != 'KTHXBYE':
                    if self.current_token['type'] == 'Comment':
                        if not self.current_token.get('inline', False):
                            self.pending_comment = self.current_token['value']
                        self.advance()
                        continue
                    stmt = self.parse_statement() #parse statement and return a statement node or none if no tokens
                    if stmt:
                        wazzup_statements.append(stmt) #append statement node to WAZZZUP statemets
                    else:
                        # If we can't parse a statement and we're not at BUHBYE, that's an error
                        if self.current_token and self.current_token['value'] != 'BUHBYE':
                            raise SyntaxError(f"Line {self.current_token['line']}: Unexpected token '{self.current_token['value']}' in WAZZUP block. Expected statement or 'BUHBYE'")
                
                # Check for required BUHBYE
                if not self.current_token:
                    raise SyntaxError(f"Line {wazzup_line}: Expected 'BUHBYE' to close 'WAZZUP' block, but reached end of input")
                if self.current_token['value'] != 'BUHBYE':
                    if self.current_token['value'] == 'KTHXBYE':
                        raise SyntaxError(f"Line {self.current_token['line']}: Expected 'BUHBYE' to close 'WAZZUP' block, but found 'KTHXBYE'")
                    raise SyntaxError(f"Line {self.current_token['line']}: Expected 'BUHBYE' to close 'WAZZUP' block, but found '{self.current_token['value']}'")
                
                buhbye_node = ParseTreeNode("BUHBYE", [], self.current_token, line=self.current_token['line'])
                self.advance()
                
                # Create WAZZUP block node
                wazzup_block = ParseTreeNode("WAZZUP_Block", [wazzup_node] + wazzup_statements + [buhbye_node])
                statements.append(wazzup_block)
            else:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                else:
                    break
        
        return StatementListNode(statements, line=line)
    
    def advance(self):
        """Move to next token in stream. Updates current_token and position."""
        self.current_pos += 1
        # Advance until we hit a non-comment token (skip comments centrally)
        while self.current_pos < len(self.tokens):
            tok = self.tokens[self.current_pos]
            if tok and tok.get('type') == 'Comment':
                # preserve non-inline comment text for pending_comment
                if not tok.get('inline', False):
                    self.pending_comment = tok.get('value')
                # skip this comment token and advance
                self.current_pos += 1
                continue
            # found a non-comment token
            self.current_token = self.tokens[self.current_pos]
            break
        else:
            # Reached end of token stream
            self.current_token = None
    
    def peek(self, offset=0):
        """Lookahead: examine token at offset without consuming."""
        pos = self.current_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def expect(self, expected_value, error_msg=None):
        """Verify token matches expected value and advance. Error handling for parse errors."""
        if not self.current_token:
            raise SyntaxError(f"Unexpected end of input. Expected: {expected_value}")
        if self.current_token['value'] != expected_value:
            msg = error_msg or f"Expected '{expected_value}' but found '{self.current_token['value']}'"
            raise SyntaxError(f"Line {self.current_token['line']}: {msg}")
        value = self.current_token['value']
        self.advance()
        return value
    
    def _could_start_conditional(self):
        """Check if current token could start a conditional statement (expression followed by O RLY?)."""
        if not self.current_token:
            return False

        # Quick check: current token must be able to start an expression.
        expr_start_values = {
            'NOT', 'BOTH OF', 'EITHER OF', 'WON OF', 'ALL OF', 'ANY OF',
            'BOTH SAEM', 'DIFFRINT', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF',
            'MOD OF', 'BIGGR OF', 'SMALLR OF', 'SMOOSH', 'I IZ', 'IT'
        }

        # If identifier followed by 'R' it's an assignment, not a conditional-start
        if self.current_token['type'] == 'Identifier' and self.peek(1) and self.peek(1)['value'] == 'R':
            return False

        can_start = False
        if self.current_token['type'] in ('NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB', 'Identifier'):
            can_start = True
        elif self.current_token['value'] in expr_start_values:
            can_start = True

        if not can_start:
            return False

        # Non-destructive scan ahead for 'O RLY?' pattern (either combined token or 'O' followed by 'RLY')
        lookahead_limit = 60
        for offset in range(0, lookahead_limit):
            t = self.peek(offset)
            if not t:
                break
            # Combined token
            if t['value'] == 'O RLY?':
                return True
        return False
    
    def _could_start_switch(self):
        """Check if current token could start a switch statement (expression followed by WTF?)."""
        if not self.current_token:
            return False
        
        # Save current position
        saved_pos = self.current_pos
        
        # Try to parse an expression
        try:
            # Note: WTF? is tokenized as "WTF" (Identifier)
            expr = self.parse_expression()
            if expr and self.current_token:
                # Check for "WTF?" pattern (WTF as identifier)
                if (self.current_token['type'] == 'Identifier' and self.current_token['value'] == 'WTF'):
                    # Restore position - we'll parse it properly in parse_switch_statement
                    self.current_pos = saved_pos
                    if saved_pos < len(self.tokens):
                        self.current_token = self.tokens[saved_pos]
                    else:
                        self.current_token = None
                    return True
                # Also check for "WTF?" as single keyword (if lexer is fixed)
                if self.current_token['value'] == 'WTF?':
                    # Restore position
                    self.current_pos = saved_pos
                    if saved_pos < len(self.tokens):
                        self.current_token = self.tokens[saved_pos]
                    else:
                        self.current_token = None
                    return True
            # Restore position
            self.current_pos = saved_pos
            if saved_pos < len(self.tokens):
                self.current_token = self.tokens[saved_pos]
            else:
                self.current_token = None
            return False
        except:
            # If parsing fails, restore position and return False
            self.current_pos = saved_pos
            if saved_pos < len(self.tokens):
                self.current_token = self.tokens[saved_pos]
            else:
                self.current_token = None
            return False
    
    def parse_statement(self):
        """Parse Statement → VariableDeclaration | PrintStatement | InputStatement | Assignment. Dispatch based on keyword."""
        if not self.current_token:
            return None
        
        # Skip comment tokens
        if self.current_token['type'] == 'Comment':
            if not self.current_token.get('inline', False):
                self.pending_comment = self.current_token['value']
            self.advance()
            if not self.current_token:
                return None
        
        line = self.current_token['line']
        
        # Check for assignment (Identifier R Expression)
        if self.current_token['type'] == 'Identifier' and self.peek(1) and self.peek(1)['value'] == 'R':
            stmt = self.parse_assignment()
        # Check for assignment (ISNOW A Typecast)
        elif self.current_token['type'] == 'Identifier' and self.peek(1)['value'] == 'IS NOW A':
            stmt = self.parse_typecast_assignment()
        # Variable declaration: I HAS A var [ITZ expr]
        elif self.current_token['value'] == 'I HAS A':
            stmt = self.parse_variable_declaration()
        # Print statement: VISIBLE expr
        elif self.current_token['value'] == 'VISIBLE':
            stmt = self.parse_print_statement()
        # Input statement: GIMMEH var
        elif self.current_token['value'] == 'GIMMEH':
            stmt = self.parse_input_statement()
        # Loop statement: IM IN YR label UPPIN/NERFIN YR var WILE/TIL condition
        elif self.current_token['value'] == 'IM IN YR':
            stmt = self.parse_loop_statement()
        # Function declaration: HOW IZ I identifier YR param [AN YR param]* [statements] FOUND YR expression IF U SAY SO
        elif self.current_token['value'] == 'HOW IZ I':
            stmt = self.parse_function_declaration()
        # Function call statement: I IZ identifier YR arg [AN YR arg]*
        elif self.current_token['value'] == 'I IZ':
            func_call = self.parse_function_call()
            stmt = StatementNode("FunctionCallStatement", [func_call], line=line)
        # Switch statement: Expression WTF? ...
        elif self._could_start_switch():
            print("Check switch")
            stmt = self.parse_switch_statement()
        # Conditional statement: Expression O RLY? ...
        elif self._could_start_conditional():
            stmt = self.parse_conditional_statement()
        else:
            # Unknown statement - raise error instead of silently skipping
            raise SyntaxError(f"Line {line}: Unexpected token '{self.current_token['value']}'. Expected statement (I HAS A, VISIBLE, GIMMEH, assignment, IM IN YR, HOW IZ I, I IZ, switch, or conditional)")
        
        # Handle inline comments (add as child node if present)
        if self.current_token and self.current_token['type'] == 'Comment' and self.current_token.get('inline', False) and self.current_token['line'] == line:
            comment_node = ParseTreeNode("Comment", [], self.current_token, line=self.current_token['line'])
            stmt.children.append(comment_node)
            self.advance()
        
        # Wrap statement in StatementNode
        stmt_node = StatementNode("Statement", [stmt], line=line)
        return stmt_node
    
    def parse_typecast_assignment(self):
        ident = self.current_token
        self.advance()   # identifier

        self.expect("IS NOW A")
        type_token = self.current_token
        print(f"Token = {type_token}")
        if type_token['value'] not in ("NUMBR","NUMBAR","YARN","TROOF"):
            raise SyntaxError(f"Line {type_token['line']}: Expected type after 'IS NOW A'")

        self.advance()
        return TypecastAssignmentNode(ident, type_token)

    def parse_variable_declaration(self):
        """Parse VariableDeclaration → I HAS A Identifier [ITZ Expression]. Optional initialization."""
        line = self.current_token['line']
        
        # Parse "I HAS A" token
        i_has_a_token = self.current_token
        self.expect('I HAS A')
        i_has_a_node = ParseTreeNode("I_HAS_A", [], i_has_a_token, line=line)
        
        # Parse identifier
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected identifier after 'I HAS A'")
        
        identifier_token = self.current_token
        identifier_node = ParseTreeNode("Identifier", [], identifier_token, line=identifier_token['line'])
        self.advance()
        
        # Parse optional ITZ Expression
        itz_node = None
        expression_node = None
        if self.current_token and self.current_token['value'] == 'ITZ':
            itz_token = self.current_token
            itz_line = itz_token['line']
            self.advance()
            itz_node = ParseTreeNode("ITZ", [], itz_token, line=itz_line)
            
            # If ITZ is present, expression is required
            if not self.current_token:
                raise SyntaxError(f"Line {itz_line}: Expected expression after 'ITZ'")
            expression_node = self.parse_expression()
            if not expression_node:
                raise SyntaxError(f"Line {itz_line}: Expected expression after 'ITZ', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return VariableDeclarationNode(i_has_a_node, identifier_node, itz_node, expression_node, line=line)
    
    def parse_print_statement(self):
        """Parse PrintStatement → VISIBLE Expression [Expression]*. Output to console."""
        line = self.current_token['line']
        visible_token = self.current_token
        self.expect('VISIBLE')
        visible_node = ParseTreeNode("VISIBLE", [], visible_token, line=line)
        
        # Parse one or more expressions (VISIBLE can output multiple values)
        expressions = []
        
        # Parse first expression - must be present
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'VISIBLE'")
        
        # Keep parsing expressions on the same line until we hit a new statement or end
        while self.current_token and self.current_token['line'] == line:
            # Stop if we hit a statement terminator
            if self.current_token['value'] in ('KTHXBYE', 'BUHBYE'):
                break
            
            # Check if next token starts a new statement (on same line, this shouldn't happen, but be safe)
            if (self.current_token['value'] in ('I', 'VISIBLE', 'GIMMEH', 'WAZZUP') and 
                self.current_token['line'] == line and len(expressions) > 0):
                # This is a new statement on the same line (unusual but possible)
                break
            
            # Try to parse an expression
            expr = self.parse_expression()
            if expr:
                expressions.append(expr)
            else:
                # If parse_expression returns None, try parsing as atomic expression
                # (for simple identifiers/literals that might not be recognized as full expressions)
                if self.current_token and self.current_token['line'] == line:
                    atomic = self.parse_atomic_expression()
                    if atomic:
                        expressions.append(atomic)
                    else:
                        # Can't parse as expression or atomic, stop
                        break
                else:
                    break
        
        if not expressions:
            raise SyntaxError(f"Line {line}: Expected expression after 'VISIBLE', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        # If only one expression, use it directly; otherwise create a list node
        if len(expressions) == 1:
            expression_node = expressions[0]
        else:
            # Create a node to hold multiple expressions (they'll be concatenated in output)
            expression_node = ParseTreeNode("VISIBLE_Expressions", expressions, line=line)
        
        return PrintStatementNode(visible_node, expression_node, line=line)
    
    def parse_input_statement(self):
        """Parse InputStatement → GIMMEH Identifier [AN Identifier]*. Multi-target input support."""
        line = self.current_token['line']
        gimmeh_token = self.current_token
        self.expect('GIMMEH')
        gimmeh_node = ParseTreeNode("GIMMEH", [], gimmeh_token, line=line)
        
        # Parse one or more identifiers (allow: GIMMEH x AN y ...)
        identifiers = []
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected identifier after 'GIMMEH'")

        # collect first identifier
        identifier_token = self.current_token
        identifiers.append(ParseTreeNode("Identifier", [], identifier_token, line=identifier_token['line']))
        self.advance()

        # allow additional identifiers separated by AN
        while self.current_token and self.current_token['value'] == 'AN':
            # consume AN
            an_tok = self.current_token
            self.advance()
            if not self.current_token or self.current_token['type'] != 'Identifier':
                raise SyntaxError(f"Line {line}: Expected identifier after 'AN' in GIMMEH list")
            identifier_token = self.current_token
            identifiers.append(ParseTreeNode("Identifier", [], identifier_token, line=identifier_token['line']))
            self.advance()

        return InputStatementNode(gimmeh_node, identifiers, line=line)
    
    def parse_expression(self):
        """Parse Expression → BooleanExpr | ComparisonExpr | ArithmeticExpr. Operator precedence via recursion."""
        expr = self.parse_boolean_expression()
        if expr:
            return expr
        return self.parse_comparison_expression()

    def parse_boolean_expression(self):
        """Parse BooleanExpr → NOT expr | (BOTH|EITHER|WON) OF expr AN expr | (ALL|ANY) OF expr [AN expr]* MKAY."""
        if not self.current_token:
            return None

        tok = self.current_token['value']
        line = self.current_token['line']

        if tok == 'NOT':
            # Unary NOT
            self.expect('NOT')
            if not self.current_token:
                raise SyntaxError(f"Line {line}: Expected expression after 'NOT'")
            expr = self.parse_expression()
            if not expr:
                raise SyntaxError(f"Line {line}: Expected expression after 'NOT', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
            return NotNode(expr, line=line)

        if tok in ('BOTH OF', 'EITHER OF', 'WON OF'):
            op_token = self.current_token
            self.advance()
            op_node = ParseTreeNode(op_token['value'].replace(' ', '_'), [], op_token, line=line)

            # parse first operand
            if not self.current_token:
                raise SyntaxError(f"Line {line}: Expected expression after '{tok}'")
            left = self.parse_expression()
            if not left:
                raise SyntaxError(f"Line {line}: Expected expression after '{tok}', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
            
            # require AN
            if not self.current_token or self.current_token['value'] != 'AN':
                raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in {tok}")
            an_token = self.current_token
            self.advance()
            an_node = ParseTreeNode('AN', [], an_token, line=an_token['line'])
            
            # parse second operand
            if not self.current_token:
                raise SyntaxError(f"Line {line}: Expected expression after 'AN' in {tok}")
            right = self.parse_expression()
            if not right:
                raise SyntaxError(f"Line {line}: Expected expression after 'AN' in {tok}, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")

            return BooleanExpressionNode(op_token['value'], [left, right], line=line)

        if tok in ('ALL OF', 'ANY OF'):
            op_token = self.current_token
            self.advance()
            operands = []
            # parse at least one operand
            if not self.current_token:
                raise SyntaxError(f"Line {line}: Expected expression after '{tok}'")
            first = self.parse_expression()
            if not first:
                raise SyntaxError(f"Line {line}: Expected expression after '{tok}', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
            operands.append(first)
            
            # allow additional operands separated by AN
            while self.current_token and self.current_token['value'] == 'AN':
                self.advance()  # consume AN
                if not self.current_token:
                    raise SyntaxError(f"Line {line}: Expected expression after 'AN' in {tok}")
                nxt = self.parse_expression()
                if not nxt:
                    raise SyntaxError(f"Line {line}: Expected expression after 'AN' in {tok}, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
                operands.append(nxt)
            # After collecting operands, expect MKAY to terminate the construct
            if not self.current_token or self.current_token['value'] != 'MKAY':
                raise SyntaxError(f"Line {line}: Expected 'MKAY' to terminate {tok}")
            # consume MKAY
            self.advance()
            return BooleanExpressionNode(op_token['value'], operands, line=line)

        return None
    
    def parse_comparison_expression(self):
        """Parse ComparisonExpr → BOTH SAEM expr AN expr | DIFFRINT expr AN expr | ArithmeticExpr."""
        if not self.current_token:
            return None
        
        # Check for comparison operators
        if self.current_token['value'] == 'BOTH SAEM':
            return self.parse_both_saem()
        elif self.current_token['value'] == 'DIFFRINT':
            return self.parse_diffrint()
        else:
            # Fall through to arithmetic expression
            return self.parse_arithmetic_expression()
    
    def parse_both_saem(self):
        """Parse BOTH SAEM expr AN expr. Equality comparison."""
        line = self.current_token['line']
        both_saem_token = self.current_token
        self.expect('BOTH SAEM')
        both_saem_node = ParseTreeNode("BOTH_SAEM", [], both_saem_token, line=line)
        
        # Parse left expression (allow any expression so comparisons may nest)
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'BOTH SAEM'")
        left_expr = self.parse_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'BOTH SAEM', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        # Parse AN separator
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in BOTH SAEM")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        # Parse right expression (allow any expression)
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in BOTH SAEM")
        right_expr = self.parse_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in BOTH SAEM, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(both_saem_node, left_expr, an_node, right_expr, line=line)
    
    def parse_diffrint(self):
        """Parse DIFFRINT expr AN expr. Inequality comparison."""
        line = self.current_token['line']
        diffrint_token = self.current_token
        self.expect('DIFFRINT')
        diffrint_node = ParseTreeNode("DIFFRINT", [], diffrint_token, line=line)
        
        # Parse left expression (allow nested comparisons/boolean expressions)
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'DIFFRINT'")
        left_expr = self.parse_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'DIFFRINT', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        # Parse AN separator
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in DIFFRINT")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        # Parse right expression (allow nested expressions)
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in DIFFRINT")
        right_expr = self.parse_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in DIFFRINT, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(diffrint_node, left_expr, an_node, right_expr, line=line)
    
    def parse_arithmetic_expression(self):
        """Parse ArithmeticExpr → (SUM|DIFF|PRODUKT|QUOSHUNT|MOD|BIGGR|SMALLR|SMOOSH) OF expr AN expr | PrimaryExpr."""
        if not self.current_token:
            return None
        
        # Check for arithmetic operators
        if self.current_token['value'] == 'SUM OF':
            return self.parse_sum_of()
        elif self.current_token['value'] == 'DIFF OF':
            return self.parse_diff_of()
        elif self.current_token['value'] == 'PRODUKT OF':
            return self.parse_produkt_of()
        elif self.current_token['value'] == 'QUOSHUNT OF':
            return self.parse_quoshunt_of()
        elif self.current_token['value'] == 'MOD OF':
            return self.parse_mod_of()
        elif self.current_token['value'] == 'BIGGR OF':
            return self.parse_biggr_of()
        elif self.current_token['value'] == 'SMALLR OF':
            return self.parse_smallr_of()
        elif self.current_token['value'] == 'SMOOSH':
            return self.parse_smoosh()
        else:
            # Fall through to primary expression
            return self.parse_primary_expression()

    def parse_smoosh(self):
        """Parse SMOOSH expr AN expr [AN expr]*. String concatenation operator."""
        line = self.current_token['line']
        smoosh_token = self.current_token
        self.expect('SMOOSH')
        operands = []

        # First operand
        first = self.parse_primary_expression()
        if not first:
            raise SyntaxError(f"Line {line}: Expected expression after 'SMOOSH'")
        operands.append(first)

        # Additional operands separated by AN
        while self.current_token and self.current_token['value'] == 'AN':
            self.advance()
            nxt = self.parse_primary_expression()
            if not nxt:
                raise SyntaxError(f"Line {line}: Expected expression after 'AN' in SMOOSH")
            operands.append(nxt)

        return ParseTreeNode('Smoosh', operands, smoosh_token, line=line)
    
    def parse_sum_of(self):
        """Parse SUM OF expr AN expr. Addition."""
        line = self.current_token['line']
        sum_token = self.current_token
        self.expect('SUM OF')
        sum_node = ParseTreeNode("SUM_OF", [], sum_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'SUM OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'SUM OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in SUM OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in SUM OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in SUM OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(sum_node, left_expr, an_node, right_expr, line=line)
    
    def parse_diff_of(self):
        """Parse DIFF OF expr AN expr. Subtraction."""
        line = self.current_token['line']
        diff_token = self.current_token
        self.expect('DIFF OF')
        diff_node = ParseTreeNode("DIFF_OF", [], diff_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'DIFF OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'DIFF OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in DIFF OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in DIFF OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in DIFF OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(diff_node, left_expr, an_node, right_expr, line=line)
    
    def parse_produkt_of(self):
        """Parse PRODUKT OF expr AN expr. Multiplication."""
        line = self.current_token['line']
        produkt_token = self.current_token
        self.expect('PRODUKT OF')
        produkt_node = ParseTreeNode("PRODUKT_OF", [], produkt_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'PRODUKT OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'PRODUKT OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in PRODUKT OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in PRODUKT OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in PRODUKT OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(produkt_node, left_expr, an_node, right_expr, line=line)
    
    def parse_quoshunt_of(self):
        """Parse QUOSHUNT OF expr AN expr. Division."""
        line = self.current_token['line']
        quoshunt_token = self.current_token
        self.expect('QUOSHUNT OF')
        quoshunt_node = ParseTreeNode("QUOSHUNT_OF", [], quoshunt_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'QUOSHUNT OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'QUOSHUNT OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in QUOSHUNT OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in QUOSHUNT OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in QUOSHUNT OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(quoshunt_node, left_expr, an_node, right_expr, line=line)
    
    def parse_mod_of(self):
        """Parse MOD OF expr AN expr. Modulo."""
        line = self.current_token['line']
        mod_token = self.current_token
        self.expect('MOD OF')
        mod_node = ParseTreeNode("MOD_OF", [], mod_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'MOD OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'MOD OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in MOD OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in MOD OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in MOD OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(mod_node, left_expr, an_node, right_expr, line=line)
    
    def parse_biggr_of(self):
        """Parse BIGGR OF expr AN expr. Maximum value."""
        line = self.current_token['line']
        biggr_token = self.current_token
        self.expect('BIGGR OF')
        biggr_node = ParseTreeNode("BIGGR_OF", [], biggr_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'BIGGR OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'BIGGR OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in BIGGR OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in BIGGR OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in BIGGR OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(biggr_node, left_expr, an_node, right_expr, line=line)
    
    def parse_smallr_of(self):
        """Parse SMALLR OF expr AN expr. Minimum value."""
        line = self.current_token['line']
        smallr_token = self.current_token
        self.expect('SMALLR OF')
        smallr_node = ParseTreeNode("SMALLR_OF", [], smallr_token, line=line)
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'SMALLR OF'")
        left_expr = self.parse_arithmetic_expression()
        if not left_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'SMALLR OF', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in SMALLR OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in SMALLR OF")
        right_expr = self.parse_arithmetic_expression()
        if not right_expr:
            raise SyntaxError(f"Line {line}: Expected expression after 'AN' in SMALLR OF, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return BinaryExpressionNode(smallr_node, left_expr, an_node, right_expr, line=line)
    
    def parse_primary_expression(self):
        """Parse PrimaryExpr → AtomicExpr [+ AtomicExpr]*. String concatenation with + operator."""
        if not self.current_token:
            return None
        
        # Handle string concatenation with +
        expr = self.parse_atomic_expression()
        if not expr:
            return None
        
        # Check for concatenation operator
        while self.current_token and (self.current_token['value'] == '+' or (self.current_token['type'] == 'Operator' and self.current_token['value'] == '+')):
            line = self.current_token['line']
            plus_token = self.current_token
            self.advance()
            plus_node = ParseTreeNode("CONCAT", [], plus_token, line=line)
            
            if not self.current_token:
                raise SyntaxError(f"Line {line}: Expected expression after '+' operator")
            
            # Try to parse right operand - can be any expression (arithmetic, comparison, etc.)
            # Use parse_arithmetic_expression() which will handle SUM OF, DIFF OF, etc.
            # and fall through to parse_atomic_expression() for simple cases
            try:
                right_expr = self.parse_arithmetic_expression()
                if not right_expr:
                    raise SyntaxError(f"Line {line}: Expected expression after '+' operator, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
            except SyntaxError as e:
                # If parsing raises an error, provide a clearer message
                if self.current_token:
                    raise SyntaxError(f"Line {line}: Expected expression after '+' operator, but found '{self.current_token['value']}'")
                raise
            expr = BinaryExpressionNode(plus_node, expr, None, right_expr, line=line)
        
        return expr
    
    def parse_atomic_expression(self):
        """Parse AtomicExpr → Literal | Identifier | FunctionCall | IT | (Expression). Terminal expressions."""
        if not self.current_token:
            return None
        
        # Function call: I IZ identifier YR arg [AN YR arg]*
        if self.current_token['value'] == 'I IZ':
            return self.parse_function_call()
        
        # IT keyword (refers to last function call result)
        if self.current_token['value'] == 'IT':
            it_token = self.current_token
            self.advance()
            it_node = ParseTreeNode("IT", [], it_token, line=it_token['line'])
            return it_node
        
        # Literal: NUMBR, NUMBAR, YARN, TROOF, NOOB
        if self.current_token['type'] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB']:
            literal_token = self.current_token
            self.advance()
            literal_node = LiteralNode(literal_token, line=literal_token['line'])
            return literal_node
        
        # Variable: Identifier
        elif self.current_token['type'] == 'Identifier':
            identifier_token = self.current_token
            self.advance()
            identifier_node = ParseTreeNode("Identifier", [], identifier_token, line=identifier_token['line'])
            variable_node = VariableNode(identifier_node, line=identifier_token['line'])
            return variable_node
        
        else:
            raise SyntaxError(f"Line {self.current_token['line']}: Unexpected token '{self.current_token['value']}' in expression")
    
    def parse_function_call(self):
        """Parse FunctionCall → I IZ identifier YR arg [AN YR arg]*"""
        line = self.current_token['line']
        
        # Parse "I IZ"
        if self.current_token['value'] != 'I IZ':
            raise SyntaxError(f"Line {line}: Expected 'I IZ' in function call")
        i_iz_token = self.current_token
        self.advance()
        
        # Parse function name (identifier)
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected function name (identifier) after 'I IZ'")
        func_name_token = self.current_token
        func_name_node = ParseTreeNode("FunctionName", [], func_name_token, line=func_name_token['line'])
        self.advance()
        
        # Parse arguments: YR arg [AN YR arg]*
        arguments = []
        while self.current_token and self.current_token['value'] == 'YR':
            yr_token = self.current_token
            self.advance()
            
            if not self.current_token:
                raise SyntaxError(f"Line {yr_token['line']}: Expected argument expression after 'YR'")
            arg_expr = self.parse_expression()
            if not arg_expr:
                raise SyntaxError(f"Line {yr_token['line']}: Expected argument expression after 'YR', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
            arguments.append(arg_expr)
            
            # Check if there's another argument (AN YR ...)
            # Only consume AN if the next token is YR (indicating another argument)
            # Otherwise, leave AN for the outer parser (e.g., in SUM OF ... AN ...)
            # But we need to be careful: if the current token after parsing the expression
            # is not AN, or if AN is not followed by YR, we're done with this function call
            if self.current_token and self.current_token['value'] == 'AN':
                # Peek ahead to see if next is YR (indicating another argument)
                next_token = self.peek(1)
                if next_token and next_token['value'] == 'YR':
                    self.advance()  # Consume AN, next iteration will check for YR
                    # Continue loop to parse next argument
                else:
                    # Not another argument (AN is for outer expression), stop parsing function call
                    # Don't consume AN, leave it for outer parser
                    break
            else:
                # No AN token, we're done with function call
                break
        
        return FunctionCallNode(func_name_node, arguments, line=line)
    
    def parse_assignment(self):
        """Parse Assignment → Identifier R Expression. Variable assignment."""
        line = self.current_token['line']
        
        # Parse identifier
        if self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected identifier in assignment")
        
        identifier_token = self.current_token
        identifier_node = ParseTreeNode("Identifier", [], identifier_token, line=identifier_token['line'])
        self.advance()
        
        # Parse R operator
        if not self.current_token or self.current_token['value'] != 'R':
            raise SyntaxError(f"Line {line}: Expected 'R' in assignment")
        
        r_token = self.current_token
        self.advance()
        r_node = ParseTreeNode("R", [], r_token, line=r_token['line'])
        
        # Parse expression - must be present
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected expression after 'R' in assignment")
        expression_node = self.parse_expression()
        if not expression_node:
            raise SyntaxError(f"Line {line}: Expected expression after 'R' in assignment, but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        return AssignmentNode(identifier_node, expression_node, line=line)
    
    def parse_loop_statement(self):
        """Parse Loop → IM IN YR label UPPIN YR var WILE condition | IM IN YR label NERFIN YR var TIL condition
                       statements
                       IM OUTTA YR label"""
        line = self.current_token['line']
        
        # Parse "IM IN YR"
        if self.current_token['value'] != 'IM IN YR':
            raise SyntaxError(f"Line {line}: Expected 'IM IN YR' in loop statement")
        im_in_yr_token = self.current_token
        im_in_yr_node = ParseTreeNode("IM IN YR", [], im_in_yr_token, line=im_in_yr_token['line'])
        self.advance()
        
        # Parse loop label (identifier)
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected loop label (identifier) after 'IM IN YR'")
        label_token = self.current_token
        label_node = ParseTreeNode("Label", [], label_token, line=label_token['line'])
        loop_label = label_token['value']
        self.advance()
        
        # Parse direction: UPPIN or NERFIN
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected 'UPPIN' or 'NERFIN' after loop label")
        if self.current_token['value'] not in ('UPPIN', 'NERFIN'):
            raise SyntaxError(f"Line {line}: Expected 'UPPIN' or 'NERFIN' after loop label, but found '{self.current_token['value']}'")
        direction_token = self.current_token
        direction_node = ParseTreeNode(direction_token['value'], [], direction_token, line=direction_token['line'])
        is_uppin = direction_token['value'] == 'UPPIN'
        self.advance()
        
        # Parse "YR"
        if not self.current_token or self.current_token['value'] != 'YR':
            raise SyntaxError(f"Line {line}: Expected 'YR' after '{direction_token['value']}'")
        yr_token1 = self.current_token
        self.advance()
        
        # Parse variable (identifier)
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected variable identifier after 'YR'")
        var_token = self.current_token
        var_node = ParseTreeNode("Variable", [], var_token, line=var_token['line'])
        self.advance()
        
        # Parse condition keyword: WILE (for UPPIN) or TIL (for NERFIN)
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected 'WILE' or 'TIL' after loop variable")
        if is_uppin:
            if self.current_token['value'] != 'WILE':
                raise SyntaxError(f"Line {line}: Expected 'WILE' after 'UPPIN YR', but found '{self.current_token['value']}'")
        else:
            if self.current_token['value'] != 'TIL':
                raise SyntaxError(f"Line {line}: Expected 'TIL' after 'NERFIN YR', but found '{self.current_token['value']}'")
        condition_keyword_token = self.current_token
        self.advance()
        
        # Parse condition expression
        if not self.current_token:
            raise SyntaxError(f"Line {line}: Expected condition expression after '{condition_keyword_token['value']}'")
        condition_node = self.parse_expression()
        if not condition_node:
            raise SyntaxError(f"Line {line}: Expected condition expression after '{condition_keyword_token['value']}', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        # Parse loop body (statements until IM OUTTA YR label)
        body_statements = []
        while self.current_token and self.current_token['value'] != 'IM OUTTA YR':
            # Skip comment tokens
            if self.current_token and self.current_token['type'] == 'Comment':
                if not self.current_token.get('inline', False):
                    self.pending_comment = self.current_token['value']
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                body_statements.append(stmt)
            else:
                break
        
        # Parse "IM OUTTA YR"
        if not self.current_token or self.current_token['value'] != 'IM OUTTA YR':
            raise SyntaxError(f"Line {line}: Expected 'IM OUTTA YR' to close loop '{loop_label}'")
        im_outta_yr_token = self.current_token
        im_outta_yr_node = ParseTreeNode("IM OUTTA YR", [], im_outta_yr_token, line=im_outta_yr_token['line'])
        self.advance()
        
        # Parse closing label (should match opening label)
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {im_outta_yr_token['line']}: Expected loop label after 'IM OUTTA YR'")
        closing_label = self.current_token['value']
        if closing_label != loop_label:
            raise SyntaxError(f"Line {self.current_token['line']}: Loop label mismatch. Expected '{loop_label}' but found '{closing_label}'")
        self.advance()
        
        return LoopNode(im_in_yr_node, label_node, direction_node, var_node, condition_node, body_statements, im_outta_yr_node, line=line)
    
    def parse_conditional_statement(self):
        """Parse Conditional → Expression O RLY? YA RLY statements [MEBBE Expression statements]* [NO WAI statements] OIC"""
        line = self.current_token['line']
        
        # Parse condition expression
        condition_expr = self.parse_expression()
        if not condition_expr:
            raise SyntaxError(f"Line {line}: Expected expression before 'O RLY?'")
        
        # Parse "O RLY?" (tokenized as "O" Identifier followed by "RLY" Identifier)
        if not self.current_token or self.current_token['value'] != 'O RLY?':
            # Also check for "O RLY?" as single keyword (if lexer is fixed)
            if not self.current_token or self.current_token['value'] != 'O RLY?':
                raise SyntaxError(f"Line {line}: Expected 'O RLY?' after condition expression")
        o_rly_token = self.current_token
        self.advance()
        
        # Parse "YA RLY" block
        if not self.current_token or self.current_token['value'] != 'YA RLY':
            raise SyntaxError(f"Line {o_rly_token['line']}: Expected 'YA RLY' after 'O RLY?'")
        ya_rly_token = self.current_token
        self.advance()
        
        # Parse YA RLY statements
        ya_rly_statements = []
        while self.current_token and self.current_token['value'] not in ('MEBBE', 'NO WAI', 'OIC'):
            # Skip comment tokens
            if self.current_token and self.current_token['type'] == 'Comment':
                if not self.current_token.get('inline', False):
                    self.pending_comment = self.current_token['value']
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                ya_rly_statements.append(stmt)
            else:
                break
        
        # Parse optional MEBBE blocks
        mebbe_blocks = []
        while self.current_token and self.current_token['value'] == 'MEBBE':
            mebbe_token = self.current_token
            self.advance()
            
            # Parse MEBBE condition expression
            mebbe_expr = self.parse_expression()
            if not mebbe_expr:
                raise SyntaxError(f"Line {mebbe_token['line']}: Expected expression after 'MEBBE'")
            
            # Parse MEBBE statements
            mebbe_statements = []
            while self.current_token and self.current_token['value'] not in ('MEBBE', 'NO WAI', 'OIC'):
                # Skip comment tokens
                if self.current_token and self.current_token['type'] == 'Comment':
                    if not self.current_token.get('inline', False):
                        self.pending_comment = self.current_token['value']
                    self.advance()
                    continue
                
                stmt = self.parse_statement()
                if stmt:
                    mebbe_statements.append(stmt)
                else:
                    break
            
            mebbe_blocks.append((mebbe_expr, mebbe_statements))
        
        # Parse optional NO WAI block
        no_wai_statements = None
        if self.current_token and self.current_token['value'] == 'NO WAI':
            no_wai_token = self.current_token
            self.advance()
            
            no_wai_statements = []
            while self.current_token and self.current_token['value'] != 'OIC':
                # Skip comment tokens
                if self.current_token and self.current_token['type'] == 'Comment':
                    if not self.current_token.get('inline', False):
                        self.pending_comment = self.current_token['value']
                    self.advance()
                    continue
                
                stmt = self.parse_statement()
                if stmt:
                    no_wai_statements.append(stmt)
                else:
                    break
        
        # Parse "OIC"
        if not self.current_token or self.current_token['value'] != 'OIC':
            raise SyntaxError(f"Line {line}: Expected 'OIC' to close conditional statement")
        oic_token = self.current_token
        self.advance()
        
        return ConditionalNode(condition_expr, ya_rly_statements, mebbe_blocks if mebbe_blocks else None, no_wai_statements, line=line)
    
    def parse_switch_statement(self):
        """Parse Switch → Expression WTF? [OMG Expression statements [GTFO]]* [OMGWTF statements] OIC"""
        line = self.current_token['line']
        
        # Parse switch expression
        switch_expr = self.parse_expression()
        if not switch_expr:
            raise SyntaxError(f"Line {line}: Expected expression before 'WTF?'")
        
        # Parse "WTF?" (tokenized as "WTF" Identifier)
        if not self.current_token or not (self.current_token['type'] == 'Identifier' and self.current_token['value'] == 'WTF'):
            # Also check for "WTF?" as single keyword (if lexer is fixed)
            if not self.current_token or self.current_token['value'] != 'WTF?':
                raise SyntaxError(f"Line {line}: Expected 'WTF?' after switch expression")
        wtf_token = self.current_token
        self.advance()
        
        # Parse OMG cases
        omg_cases = []
        while self.current_token and self.current_token['value'] == 'OMG':
            omg_token = self.current_token
            self.advance()
            
            # Parse OMG case value expression
            omg_expr = self.parse_expression()
            if not omg_expr:
                raise SyntaxError(f"Line {omg_token['line']}: Expected expression after 'OMG'")
            
            # Parse OMG case statements
            omg_statements = []
            has_gtfo = False
            while self.current_token and self.current_token['value'] not in ('OMG', 'OMGWTF', 'OIC'):
                # Skip comment tokens
                if self.current_token and self.current_token['type'] == 'Comment':
                    if not self.current_token.get('inline', False):
                        self.pending_comment = self.current_token['value']
                    self.advance()
                    continue
                
                # Check for GTFO (break statement)
                if self.current_token and self.current_token['value'] == 'GTFO':
                    gtfo_token = self.current_token
                    self.advance()
                    has_gtfo = True
                    break
                
                stmt = self.parse_statement()
                if stmt:
                    omg_statements.append(stmt)
                else:
                    break
            
            omg_cases.append((omg_expr, omg_statements))
        
        # Parse optional OMGWTF (default case)
        omgwtf_statements = None
        if self.current_token and self.current_token['value'] == 'OMGWTF':
            omgwtf_token = self.current_token
            self.advance()
            
            omgwtf_statements = []
            while self.current_token and self.current_token['value'] != 'OIC':
                # Skip comment tokens
                if self.current_token and self.current_token['type'] == 'Comment':
                    if not self.current_token.get('inline', False):
                        self.pending_comment = self.current_token['value']
                    self.advance()
                    continue
                
                stmt = self.parse_statement()
                if stmt:
                    omgwtf_statements.append(stmt)
                else:
                    break
        
        # Parse "OIC"
        if not self.current_token or self.current_token['value'] != 'OIC':
            raise SyntaxError(f"Line {line}: Expected 'OIC' to close switch statement")
        oic_token = self.current_token
        self.advance()
        
        return SwitchNode(switch_expr, omg_cases if omg_cases else None, omgwtf_statements, line=line)
    
    def parse_function_declaration(self):
        """Parse Function → HOW IZ I identifier YR param [AN YR param]* [statements] FOUND YR expression IF U SAY SO"""
        line = self.current_token['line']
        
        # Parse "HOW IZ I"
        if self.current_token['value'] != 'HOW IZ I':
            raise SyntaxError(f"Line {line}: Expected 'HOW IZ I' in function declaration")
        how_iz_i_token = self.current_token
        self.advance()
        
        # Parse function name (identifier)
        if not self.current_token or self.current_token['type'] != 'Identifier':
            raise SyntaxError(f"Line {line}: Expected function name (identifier) after 'HOW IZ I'")
        func_name_token = self.current_token
        func_name_node = ParseTreeNode("FunctionName", [], func_name_token, line=func_name_token['line'])
        self.advance()
        
        # Parse parameters: YR param [AN YR param]*
        parameters = []
        while self.current_token and self.current_token['value'] == 'YR':
            yr_token = self.current_token
            self.advance()
            
            if not self.current_token or self.current_token['type'] != 'Identifier':
                raise SyntaxError(f"Line {yr_token['line']}: Expected parameter name (identifier) after 'YR'")
            param_token = self.current_token
            param_node = ParseTreeNode("Parameter", [], param_token, line=param_token['line'])
            parameters.append(param_node)
            self.advance()
            
            # Check if there's another parameter (AN YR ...)
            if self.current_token and self.current_token['value'] == 'AN':
                self.advance()  # Consume AN, next iteration will check for YR
            else:
                break
        
        # Parse optional function body statements (before FOUND YR)
        body_statements = []
        while self.current_token and self.current_token['value'] != 'FOUND YR':
            # Skip comment tokens
            if self.current_token and self.current_token['type'] == 'Comment':
                if not self.current_token.get('inline', False):
                    self.pending_comment = self.current_token['value']
                self.advance()
                continue
            
            # Check for GTFO (early return/break)
            if self.current_token and self.current_token['value'] == 'GTFO':
                gtfo_token = self.current_token
                self.advance()
                # GTFO in function means early return, we can represent it as a statement
                continue
            
            stmt = self.parse_statement()
            if stmt:
                body_statements.append(stmt)
            else:
                break
        
        # Parse "FOUND YR"
        if not self.current_token or self.current_token['value'] != 'FOUND YR':
            raise SyntaxError(f"Line {line}: Expected 'FOUND YR' in function declaration")
        found_yr_token = self.current_token
        self.advance()
        
        # Parse return expression
        if not self.current_token:
            raise SyntaxError(f"Line {found_yr_token['line']}: Expected return expression after 'FOUND YR'")
        return_expr = self.parse_expression()
        if not return_expr:
            raise SyntaxError(f"Line {found_yr_token['line']}: Expected return expression after 'FOUND YR', but found '{self.current_token['value'] if self.current_token else 'end of input'}'")
        
        # Parse "IF U SAY SO"
        if not self.current_token or self.current_token['value'] != 'IF U SAY SO':
            found_token = self.current_token['value'] if self.current_token else 'end of input'
            raise SyntaxError(f"Line {line}: Expected 'IF U SAY SO' to close function declaration, but found '{found_token}'")
        if_u_say_so_token = self.current_token
        self.advance()
        
        return FunctionNode(func_name_node, parameters, body_statements, return_expr, line=line)
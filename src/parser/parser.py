"""
Recursive Descent Parser for LOLCODE
This parser consumes tokens from the Lexer and builds a Parse Tree
"""

from lexer.lexer import Lexer
from parser.parse_tree_nodes import (
    ParseTreeNode, ProgramNode, StatementListNode, StatementNode,
    VariableDeclarationNode, PrintStatementNode, InputStatementNode,
    ExpressionNode, BinaryExpressionNode, PrimaryExpressionNode,
    LiteralNode, VariableNode, ComparisonNode, BothSaemNode, DiffrintNode,
    AssignmentNode, BooleanExpressionNode, NotNode
)


class Parser:
    """Recursive Descent Parser for LOLCODE."""
    
    def __init__(self, lexer):
        """Initialize parser with lexer."""
        self.lexer = lexer
        self.tokens = []
        self.current_pos = 0
        self.current_token = None
        self.pending_comment = None  # Track comment 
    
    def parse(self, code):
        """Parse Program → HAI StatementList KTHXBYE. Entry point for recursive descent."""
        self.tokens = self.lexer.tokenize(code)
        self.current_pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
        # Parse the program: Program → HAI Statements KTHXBYE
        line = self.current_token['line'] if self.current_token else None
        
        # Skip leading comment tokens before checking for HAI
        while self.current_token and self.current_token['type'] == 'Comment':
            if not self.current_token.get('inline', False):
                self.pending_comment = self.current_token['value']
            self.advance() #move current token to next token in the list
        
        # Parse HAI token if present
        hai_node = None
        if self.current_token and self.current_token['value'] == 'HAI':
            hai_node = ParseTreeNode("HAI", [], self.current_token, line=self.current_token['line'])
            self.advance()
        
        # Parse StatementList
        statements_node = self.parse_statement_list()
        
        # Parse KTHXBYE token if present
        kthxbye_node = None
        if self.current_token and self.current_token['value'] == 'KTHXBYE':
            kthxbye_node = ParseTreeNode("KTHXBYE", [], self.current_token, line=self.current_token['line'])
            self.advance()
        
        # Build Program node with all children
        program_children = []
        if hai_node:
            program_children.append(hai_node)
        program_children.append(statements_node)
        if kthxbye_node:
            program_children.append(kthxbye_node)
        
        program = ParseTreeNode("Program", program_children, line=line)
        program.statements_node = statements_node
        return program
    
    def parse_statement_list(self):
        """Parse StatementList → Statement* (KTHXBYE | BUHBYE). Recursive descent: collect statements."""
        statements = []
        line = self.current_token['line'] if self.current_token else None
        
        while self.current_token and self.current_token['value'] != 'KTHXBYE' and self.current_token['value'] != 'BUHBYE':
            #loop while KTHXBYE
            # Skip comment tokens
            if self.current_token and self.current_token['type'] == 'Comment':
                if not self.current_token.get('inline', False):
                    self.pending_comment = self.current_token['value']
                self.advance()
                continue
            
            # if current token is wazzup 
            if self.current_token and self.current_token['value'] == 'WAZZUP':
                # Parse WAZZUP block
                wazzup_node = ParseTreeNode("WAZZUP", [], self.current_token, line=self.current_token['line'])
                self.advance()
                
                # Parse statements in WAZZUP block
                wazzup_statements = []
                while self.current_token and self.current_token['value'] != 'BUHBYE':
                    if self.current_token['type'] == 'Comment':
                        if not self.current_token.get('inline', False):
                            self.pending_comment = self.current_token['value']
                        self.advance()
                        continue
                    stmt = self.parse_statement() #parse statement and return a statement node or none if no tokens
                    if stmt:
                        wazzup_statements.append(stmt) #append statement node to WAZZZUP statemets
                
                buhbye_node = None
                if self.current_token and self.current_token['value'] == 'BUHBYE':
                    buhbye_node = ParseTreeNode("BUHBYE", [], self.current_token, line=self.current_token['line'])
                    self.advance()
                
                # Create WAZZUP block node
                wazzup_block = ParseTreeNode("WAZZUP_Block", [wazzup_node] + wazzup_statements + ([buhbye_node] if buhbye_node else []))
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
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
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
        if self.current_token['type'] == 'Identifier' and self.peek() and self.peek()['value'] == 'R':
            stmt = self.parse_assignment()
        # Variable declaration: I HAS A var [ITZ expr]
        elif self.current_token['value'] == 'I HAS A':
            stmt = self.parse_variable_declaration()
        # Print statement: VISIBLE expr
        elif self.current_token['value'] == 'VISIBLE':
            stmt = self.parse_print_statement()
        # Input statement: GIMMEH var
        elif self.current_token['value'] == 'GIMMEH':
            stmt = self.parse_input_statement()
        else:
            # Unknown statement - skip it for now
            self.advance()
            return None
        
        # Handle inline comments (add as child node if present)
        if self.current_token and self.current_token['type'] == 'Comment' and self.current_token.get('inline', False) and self.current_token['line'] == line:
            comment_node = ParseTreeNode("Comment", [], self.current_token, line=self.current_token['line'])
            stmt.children.append(comment_node)
            self.advance()
        
        # Wrap statement in StatementNode
        stmt_node = StatementNode("Statement", [stmt], line=line)
        return stmt_node
    
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
            self.advance()
            itz_node = ParseTreeNode("ITZ", [], itz_token, line=itz_token['line'])
            expression_node = self.parse_expression()
        
        return VariableDeclarationNode(i_has_a_node, identifier_node, itz_node, expression_node, line=line)
    
    def parse_print_statement(self):
        """Parse PrintStatement → VISIBLE Expression. Output to console."""
        line = self.current_token['line']
        visible_token = self.current_token
        self.expect('VISIBLE')
        visible_node = ParseTreeNode("VISIBLE", [], visible_token, line=line)
        
        expression_node = self.parse_expression()
        
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
            expr = self.parse_expression()
            return NotNode(expr, line=line)

        if tok in ('BOTH OF', 'EITHER OF', 'WON OF'):
            op_token = self.current_token
            self.advance()
            op_node = ParseTreeNode(op_token['value'].replace(' ', '_'), [], op_token, line=line)

            # parse first operand
            left = self.parse_expression()
            # require AN
            if not self.current_token or self.current_token['value'] != 'AN':
                raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in {tok}")
            an_token = self.current_token
            self.advance()
            an_node = ParseTreeNode('AN', [], an_token, line=an_token['line'])
            right = self.parse_expression()

            return BooleanExpressionNode(op_token['value'], [left, right], line=line)

        if tok in ('ALL OF', 'ANY OF'):
            op_token = self.current_token
            self.advance()
            operands = []
            # parse at least one operand
            first = self.parse_expression()
            operands.append(first)
            # allow additional operands separated by AN
            while self.current_token and self.current_token['value'] == 'AN':
                self.advance()  # consume AN
                nxt = self.parse_expression()
                operands.append(nxt)
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
        left_expr = self.parse_expression()
        
        # Parse AN separator
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in BOTH SAEM")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        # Parse right expression (allow any expression)
        right_expr = self.parse_expression()
        
        return BinaryExpressionNode(both_saem_node, left_expr, an_node, right_expr, line=line)
    
    def parse_diffrint(self):
        """Parse DIFFRINT expr AN expr. Inequality comparison."""
        line = self.current_token['line']
        diffrint_token = self.current_token
        self.expect('DIFFRINT')
        diffrint_node = ParseTreeNode("DIFFRINT", [], diffrint_token, line=line)
        
        # Parse left expression (allow nested comparisons/boolean expressions)
        left_expr = self.parse_expression()
        
        # Parse AN separator
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in DIFFRINT")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        # Parse right expression (allow nested expressions)
        right_expr = self.parse_expression()
        
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
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in SUM OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(sum_node, left_expr, an_node, right_expr, line=line)
    
    def parse_diff_of(self):
        """Parse DIFF OF expr AN expr. Subtraction."""
        line = self.current_token['line']
        diff_token = self.current_token
        self.expect('DIFF OF')
        diff_node = ParseTreeNode("DIFF_OF", [], diff_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in DIFF OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(diff_node, left_expr, an_node, right_expr, line=line)
    
    def parse_produkt_of(self):
        """Parse PRODUKT OF expr AN expr. Multiplication."""
        line = self.current_token['line']
        produkt_token = self.current_token
        self.expect('PRODUKT OF')
        produkt_node = ParseTreeNode("PRODUKT_OF", [], produkt_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in PRODUKT OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(produkt_node, left_expr, an_node, right_expr, line=line)
    
    def parse_quoshunt_of(self):
        """Parse QUOSHUNT OF expr AN expr. Division."""
        line = self.current_token['line']
        quoshunt_token = self.current_token
        self.expect('QUOSHUNT OF')
        quoshunt_node = ParseTreeNode("QUOSHUNT_OF", [], quoshunt_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in QUOSHUNT OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(quoshunt_node, left_expr, an_node, right_expr, line=line)
    
    def parse_mod_of(self):
        """Parse MOD OF expr AN expr. Modulo."""
        line = self.current_token['line']
        mod_token = self.current_token
        self.expect('MOD OF')
        mod_node = ParseTreeNode("MOD_OF", [], mod_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in MOD OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(mod_node, left_expr, an_node, right_expr, line=line)
    
    def parse_biggr_of(self):
        """Parse BIGGR OF expr AN expr. Maximum value."""
        line = self.current_token['line']
        biggr_token = self.current_token
        self.expect('BIGGR OF')
        biggr_node = ParseTreeNode("BIGGR_OF", [], biggr_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in BIGGR OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(biggr_node, left_expr, an_node, right_expr, line=line)
    
    def parse_smallr_of(self):
        """Parse SMALLR OF expr AN expr. Minimum value."""
        line = self.current_token['line']
        smallr_token = self.current_token
        self.expect('SMALLR OF')
        smallr_node = ParseTreeNode("SMALLR_OF", [], smallr_token, line=line)
        
        left_expr = self.parse_primary_expression()
        
        if not self.current_token or self.current_token['value'] != 'AN':
            raise SyntaxError(f"Line {line}: Expected 'AN' after first operand in SMALLR OF")
        an_token = self.current_token
        self.advance()
        an_node = ParseTreeNode("AN", [], an_token, line=an_token['line'])
        
        right_expr = self.parse_arithmetic_expression()
        
        return BinaryExpressionNode(smallr_node, left_expr, an_node, right_expr, line=line)
    
    def parse_primary_expression(self):
        """Parse PrimaryExpr → AtomicExpr [+ AtomicExpr]*. String concatenation with + operator."""
        if not self.current_token:
            return None
        
        # Handle string concatenation with +
        expr = self.parse_atomic_expression()
        
        # Check for concatenation operator
        while self.current_token and self.current_token['value'] == '+':
            line = self.current_token['line']
            plus_token = self.current_token
            self.advance()
            plus_node = ParseTreeNode("CONCAT", [], plus_token, line=line)
            
            right_expr = self.parse_atomic_expression()
            expr = BinaryExpressionNode(plus_node, expr, None, right_expr, line=line)
        
        return expr
    
    def parse_atomic_expression(self):
        """Parse AtomicExpr → Literal | Identifier | (Expression). Terminal expressions."""
        if not self.current_token:
            return None
        
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
        
        # Parse expression
        expression_node = self.parse_expression()
        
        return AssignmentNode(identifier_node, expression_node, line=line)
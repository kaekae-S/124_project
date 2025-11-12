"""
Recursive Descent Parser for LOLCODE
This parser consumes tokens from the Lexer and builds a Parse Tree
"""

from lexer.lexer import Lexer
from parser.parse_tree_nodes import (
    ParseTreeNode, ProgramNode, StatementListNode, StatementNode,
    VariableDeclarationNode, PrintStatementNode, InputStatementNode,
    ExpressionNode, BinaryExpressionNode, PrimaryExpressionNode,
    LiteralNode, VariableNode
)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []
        self.current_pos = 0
        self.current_token = None
        self.pending_comment = None  # Track comment 
    
    def parse(self, code):
        #Main entry point: tokenize and parse the code into a parse tree
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
        #Parse StatementList → Statement StatementList | Statement | ε
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
        #Move to the next token
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None
    
    def peek(self, offset=0):
        #Look ahead at a token without consuming it
        pos = self.current_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def expect(self, expected_value, error_msg=None):
        #Expect a specific token value, raise error if not found
        if not self.current_token:
            raise SyntaxError(f"Unexpected end of input. Expected: {expected_value}")
        if self.current_token['value'] != expected_value:
            msg = error_msg or f"Expected '{expected_value}' but found '{self.current_token['value']}'"
            raise SyntaxError(f"Line {self.current_token['line']}: {msg}")
        value = self.current_token['value']
        self.advance()
        return value
    
    def parse_statement(self):
        #Parse a single statement: Statement → VariableDeclaration | PrintStatement | InputStatement
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
        
        # Variable declaration: I HAS A var [ITZ expr]
        if self.current_token['value'] == 'I HAS A':
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
        #Parse: VariableDeclaration → I_HAS_A Identifier ITZ Expression
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
        # Parse: PrintStatement -> VISIBLE Expression
        line = self.current_token['line'] if self.current_token else None
        visible_token = self.current_token
        # consume VISIBLE
        self.expect('VISIBLE')
        visible_node = ParseTreeNode("VISIBLE", [], visible_token, line=line)
        expr_node = self.parse_expression()
        return PrintStatementNode(visible_node, expr_node, line=line)


    # --- Expressions ---
    # Note, the multi-line strings here are docstrings for documentation

    def parse_expression(self):
        """Expression -> BinaryExpression | PrimaryExpression"""
        # attempt to parse binary expression
        binary = self.parse_binary_expression()
        if binary:
            return binary
        return self.parse_primary_expression()


    # Arithmetic operations
    def parse_binary_expression(self):
        """BinaryExpression -> Operator Expression AN Expression
        Operator token values: 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF',
        'MOD OF', 'BIGGR OF', 'SMALLR OF'.
        """
        # Identify if operator
        if not self.current_token:
            return None

        # Accept operators as value strings
        op_values = {"SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF",  "MOD OF", "BIGGR OF", "SMALLR OF"}

        cur = self.current_token
        is_op = (cur.get('value') in op_values)
        if not is_op:
            return None

        # operator node
        operator_token = cur
        operator_node = ParseTreeNode("Operator", [], operator_token, line=operator_token.get('line'))
        self.advance()

        # left operand (Expression)
        left = self.parse_expression()
        if not left:
            raise SyntaxError(f"Line {operator_token.get('line')}: Expected left operand after operator {operator_token}")

        # require AN separator
        if not self.current_token or not self.current_token.get('value') == 'AN':
            raise SyntaxError(f"Line {operator_token.get('line')}: Expected 'AN' between operands of {operator_token.get('value')}")
        an_token = self.current_token
        an_node = ParseTreeNode("AN", [], an_token, line=an_token.get('line'))
        self.advance()

        # right operand (Expression)
        right = self.parse_expression()
        if not right:
            raise SyntaxError(f"Line {operator_token.get('line')}: Expected right operand after 'AN'")

        return BinaryExpressionNode(operator_node, left, an_node, right, line=operator_token.get('line'))


    # Atomic values
    def parse_primary_expression(self):
        """PrimaryExpression -> Literal | Variable
        Literal token types: NUMBR, NUMBAR, YARN, TROOF, NOOB.
        Variable: Identifier token type.
        """

        # check if token exists
        if not self.current_token:
            return None

        atom = self.current_token
        # Literals
        if atom.get('type') in ('NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB', 'Number', 'String', 'Boolean'):
            literal_token = atom
            self.advance()
            return LiteralNode(literal_token, line=literal_token.get('line'))

        # Identifier
        if atom.get('type') == 'Identifier':
            identifier_token = atom
            identifier_node = ParseTreeNode("Identifier", [], identifier_token, line=identifier_token.get('line'))
            self.advance()
            return VariableNode(identifier_node, line=identifier_node.get('line'))

        return None
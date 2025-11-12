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
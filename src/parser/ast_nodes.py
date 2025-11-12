"""
Abstract Syntax Tree Node Classes
These represent the structure of parsed LOLCODE programs
"""

class ASTNode:
    # Base class for all AST nodes
    def __init__(self, line=None, comment=None):
        self.line = line
        self.comment = comment  # comment attached 
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Program(ASTNode):
    # Root node representing the entire program
    def __init__(self, statements, line=None):
        super().__init__(line)
        self.statements = statements
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


# Expression Nodes
class Expression(ASTNode):
    # Base class for expressions
    pass


class Literal(Expression):  # inherits from Expression (since expression has no initialization it goes to ast_nodes)
    # Represents a literal value (number, string, boolean)
    def __init__(self, value, literal_type, line=None):
        super().__init__(line) # Calls Expression.__init__(line)
        self.value = value
        self.type = literal_type  # NUMBR, NUMBAR, YARN, TROOF, NOOB
    
    def __repr__(self):
        return f"Literal({self.type}: {self.value})"


class Variable(Expression):
    # Represents a variable reference
    def __init__(self, name, line=None):
        super().__init__(line)
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"


class BinaryOp(Expression):
    # Represents a binary operation (SUM OF, DIFF OF, etc.)"""
    def __init__(self, operator, left, right, line=None):
        super().__init__(line)
        self.operator = operator  # "SUM OF", "DIFF OF", "PRODUKT OF", etc.
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.operator}, {self.left}, {self.right})"


# Statement Nodes
class Statement(ASTNode):
    # Base class for statements
    pass


class VariableDeclaration(Statement):
    # Represents: I HAS A var [ITZ expr]
    def __init__(self, variable_name, initial_value=None, line=None, comment=None):
        super().__init__(line, comment)
        self.variable_name = variable_name
        self.initial_value = initial_value  # None if not initialized
    
    def __repr__(self):
        # make string comment if comments are present
        comment_str = f" [comment: {self.comment}]" if self.comment else ""
        if self.initial_value:
            return f"VarDecl({self.variable_name} = {self.initial_value}){comment_str}"
        return f"VarDecl({self.variable_name}){comment_str}" #if no initial value


class PrintStatement(Statement):
       # VISIBLE expr
    def __init__(self, expression, line=None, comment=None):#use none as a default if no parameter is passed
        super().__init__(line, comment)
        self.expression = expression
    
    def __repr__(self):
        comment_str = f" [comment: {self.comment}]" if self.comment else ""
        return f"Print({self.expression}){comment_str}"


class InputStatement(Statement):
      # Represents: GIMMEH var
    def __init__(self, variable_name, line=None, comment=None): #use none as a default if no parameter is passed
        super().__init__(line, comment)
        self.variable_name = variable_name
    
    def __repr__(self):
        comment_str = f" [comment: {self.comment}]" if self.comment else ""
        return f"Input({self.variable_name}){comment_str}"


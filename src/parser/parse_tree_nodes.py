"""
Parse Tree Node Classes
"""

class ParseTreeNode:
    #Base class for all parse tree nodes
    def __init__(self, rule_name, children=None, token=None, line=None):
        self.rule_name = rule_name 
        self.children = children or []  # Child nodes
        self.token = token  # Token 
        self.line = line  # Line number
    
    def __repr__(self):
        if self.token:
            # Leaf node show token
            return f"{self.rule_name}({self.token['type']}: {self.token['value']})"
        # Internal node show rule name and child count
        return f"{self.rule_name}({len(self.children)} children)"
    
    def add_child(self, child):
        #Add a child node
        if child:
            self.children.append(child)
    
    def is_leaf(self):
        #Check if this is a leaf node 
        return self.token is not None


class ProgramNode(ParseTreeNode):
    #Root node: Program → HAI Statements KTHXBYE
    def __init__(self, statements_node, line=None):
        super().__init__("Program", [statements_node], line=line)#call function to initiate and use line as default
        self.statements_node = statements_node


class StatementListNode(ParseTreeNode):
    #StatementList → Statement Statements | Statement | ε
    def __init__(self, statements=None, line=None):
        super().__init__("StatementList", statements or [], line=line)
        self.statements = statements or []


#Statement nodes
class StatementNode(ParseTreeNode):
    #Statement → VariableDeclaration | PrintStatement | InputStatement | ...
    pass


class VariableDeclarationNode(ParseTreeNode):
    #VariableDeclaration → I_HAS_A Identifier : ITZ Expression
    def __init__(self, i_has_a_node, identifier_node, itz_node=None, expression_node=None, line=None):
        children = [i_has_a_node, identifier_node]
        if itz_node:
            children.append(itz_node)
        if expression_node:
            children.append(expression_node)
        super().__init__("VariableDeclaration", children, line=line)
        self.i_has_a_node = i_has_a_node
        self.identifier_node = identifier_node
        self.itz_node = itz_node
        self.expression_node = expression_node


class PrintStatementNode(ParseTreeNode):
    #PrintStatement → VISIBLE Expression
    def __init__(self, visible_node, expression_node, line=None):
        super().__init__("PrintStatement", [visible_node, expression_node], line=line)
        self.visible_node = visible_node
        self.expression_node = expression_node


class InputStatementNode(ParseTreeNode):
    #InputStatement → GIMMEH Identifier
    def __init__(self, gimmeh_node, identifier_nodes, line=None):
        # identifier_nodes: list of Identifier nodes (support multiple targets separated by AN)
        children = [gimmeh_node] + (identifier_nodes if isinstance(identifier_nodes, list) else [identifier_nodes])
        super().__init__("InputStatement", children, line=line)
        self.gimmeh_node = gimmeh_node
        self.identifier_nodes = identifier_nodes if isinstance(identifier_nodes, list) else [identifier_nodes]


# Expression nodes
class ExpressionNode(ParseTreeNode):
    #Expression → BinaryExpression | PrimaryExpression
    pass


class BinaryExpressionNode(ParseTreeNode):
    #BinaryExpression → Operator PrimaryExpression AN PrimaryExpression
    def __init__(self, operator_node, left_node, an_node, right_node, line=None):
        super().__init__("BinaryExpression", [operator_node, left_node, an_node, right_node], line=line)
        self.operator_node = operator_node
        self.left_node = left_node
        self.an_node = an_node
        self.right_node = right_node


class PrimaryExpressionNode(ParseTreeNode):
    #PrimaryExpression → Literal | Variable | BinaryExpression
    pass


class LiteralNode(ParseTreeNode):
    #Literal → NUMBR | NUMBAR | YARN | TROOF | NOOB
    def __init__(self, literal_token, line=None):
        super().__init__("Literal", [], literal_token, line=line)
        self.literal_token = literal_token


class VariableNode(ParseTreeNode):
    #Variable → Identifier
    def __init__(self, identifier_node, line=None):
        super().__init__("Variable", [identifier_node], line=line)
        self.identifier_node = identifier_node


# Comparison operation nodes
class ComparisonNode(ParseTreeNode):
    #ComparisonNode → BOTH SAEM | DIFFRINT
    def __init__(self, operator, left_node, right_node, line=None):
        operator_node = ParseTreeNode(operator, [], line=line)
        super().__init__("Comparison", [operator_node, left_node, right_node], line=line)
        self.operator = operator
        self.left_node = left_node
        self.right_node = right_node


class BothSaemNode(ParseTreeNode):
    #BOTH SAEM Expression AN Expression (equality check)
    def __init__(self, left_node, right_node, line=None):
        super().__init__("BothSaem", [left_node, right_node], line=line)
        self.left_node = left_node
        self.right_node = right_node


class DiffrintNode(ParseTreeNode):
    #DIFFRINT Expression AN Expression (inequality check)
    def __init__(self, left_node, right_node, line=None):
        super().__init__("Diffrint", [left_node, right_node], line=line)
        self.left_node = left_node
        self.right_node = right_node


# Assignment operation nodes
class AssignmentNode(ParseTreeNode):
    #Assignment → Identifier R Expression
    def __init__(self, identifier_node, expression_node, line=None):
        super().__init__("Assignment", [identifier_node, expression_node], line=line)
        self.identifier_node = identifier_node
        self.expression_node = expression_node


# Boolean operation nodes
class BooleanExpressionNode(ParseTreeNode):
    #Boolean operations: BOTH OF, EITHER OF, WON OF, NOT, ALL OF, ANY OF
    def __init__(self, operator, operands=None, line=None):
        operator_node = ParseTreeNode(operator, [], line=line)
        children = [operator_node] + (operands or [])
        super().__init__("BooleanExpression", children, line=line)
        self.operator = operator
        self.operands = operands or []


class NotNode(ParseTreeNode):
    #NOT Expression (logical negation)
    def __init__(self, expression_node, line=None):
        super().__init__("Not", [expression_node], line=line)
        self.expression_node = expression_node


class SmooshNode(ParseTreeNode):
    # SMOOSH concatenation: SMOOSH <expr> AN <expr> AN ...
    def __init__(self, operands=None, line=None):
        children = operands or []
        super().__init__("Smoosh", children, line=line)
        self.operands = operands or []

"""
Parse Tree Node Classes

Purpose: AST node definitions for LOLCODE parse tree

Each node class represents a grammar rule or language construct.
Nodes form a tree structure where:
- Leaf nodes contain tokens (language elements)
- Internal nodes organize and connect child nodes
- The tree is built by the Parser and analyzed by SemanticAnalyzer

"""


class ParseTreeNode:
    """Base class for all parse tree nodes.
    
    Represents a node in the AST with rule name, children, and optional token.
    """
    def __init__(self, rule_name, children=None, token=None, line=None):
        """Initialize a parse tree node.
        
        Args:
            rule_name (str): Grammar rule this node represents
            children (list): Child nodes
            token (dict): Token if this is a leaf node
            line (int): Source line number
        """
        self.rule_name = rule_name
        self.children = children or []  # Child nodes
        self.token = token  # Token for leaf nodes
        self.line = line  # Line number for error reporting
    
    def __repr__(self):
        """String representation for debugging."""
        if self.token:
            # Leaf node: show token info
            return f"{self.rule_name}({self.token['type']}: {self.token['value']})"
        # Internal node: show rule name and child count
        return f"{self.rule_name}({len(self.children)} children)"
    
    def add_child(self, child):
        """Add a child node to this node."""
        if child:
            self.children.append(child)
    
    def is_leaf(self):
        """Check if this is a leaf node (contains token)."""
        return self.token is not None


class ProgramNode(ParseTreeNode):
    """Root node of AST: Program → HAI Statements KTHXBYE.
    
    Represents the entire LOLCODE program.
    """
    def __init__(self, statements_node, line=None):
        super().__init__("Program", [statements_node], line=line)
        self.statements_node = statements_node


class StatementListNode(ParseTreeNode):
    """Collection of statements: StatementList → Statement*.
    
    Contains all statements in a program or block.
    """
    def __init__(self, statements=None, line=None):
        super().__init__("StatementList", statements or [], line=line)
        self.statements = statements or []


# Statement nodes
class StatementNode(ParseTreeNode):
    """Base class for all statements: Statement → VariableDeclaration | etc."""
    pass


class VariableDeclarationNode(ParseTreeNode):
    """Variable declaration: I HAS A Identifier [ITZ Expression].
    
    Declares a new variable, optionally with initial value.
    """
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

class TypecastAssignmentNode(ParseTreeNode):
    def __init__(self, identifier_token, type_token):
        self.identifier = identifier_token
        self.type_token = type_token

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


class LoopNode(ParseTreeNode):
    #Loop → IM IN YR label UPPIN YR var WILE condition | IM IN YR label NERFIN YR var TIL condition
    #       statements
    #       IM OUTTA YR label
    def __init__(self, im_in_yr_node, label_node, direction_node, var_node, condition_node, body_statements, im_outta_yr_node, line=None):
        children = [im_in_yr_node, label_node, direction_node, var_node, condition_node] + body_statements + [im_outta_yr_node]
        super().__init__("Loop", children, line=line)
        self.im_in_yr_node = im_in_yr_node
        self.label_node = label_node
        self.direction_node = direction_node  # UPPIN or NERFIN
        self.var_node = var_node
        self.condition_node = condition_node
        self.body_statements = body_statements
        self.im_outta_yr_node = im_outta_yr_node


class ConditionalNode(ParseTreeNode):
    #Conditional → Expression O RLY? YA RLY statements [MEBBE Expression statements]* [NO WAI statements] OIC
    def __init__(self, condition_expr, ya_rly_statements, mebbe_blocks=None, no_wai_statements=None, line=None):
        children = [condition_expr] + ya_rly_statements
        if mebbe_blocks:
            for mebbe_expr, mebbe_stmts in mebbe_blocks:
                children.append(mebbe_expr)
                children.extend(mebbe_stmts)
        if no_wai_statements:
            children.extend(no_wai_statements)
        super().__init__("Conditional", children, line=line)
        self.condition_expr = condition_expr
        self.ya_rly_statements = ya_rly_statements
        self.mebbe_blocks = mebbe_blocks or []  # List of (expression, statements) tuples
        self.no_wai_statements = no_wai_statements or []


class SwitchNode(ParseTreeNode):
    #Switch → Expression WTF? [OMG Expression statements [GTFO]]* [OMGWTF statements] OIC
    def __init__(self, switch_expr, omg_cases=None, omgwtf_statements=None, line=None):
        children = [switch_expr]
        if omg_cases:
            for omg_expr, omg_stmts in omg_cases:
                children.append(omg_expr)
                children.extend(omg_stmts)
        if omgwtf_statements:
            children.extend(omgwtf_statements)
        super().__init__("Switch", children, line=line)
        self.switch_expr = switch_expr
        self.omg_cases = omg_cases or []  # List of (expression, statements) tuples
        self.omgwtf_statements = omgwtf_statements or []


class FunctionNode(ParseTreeNode):
    #Function → HOW IZ I identifier YR param [AN YR param]* [statements] FOUND YR expression IF U SAY SO
    def __init__(self, function_name, parameters, body_statements, return_expr, line=None):
        children = [function_name] + parameters
        if body_statements:
            children.extend(body_statements)
        children.append(return_expr)
        super().__init__("Function", children, line=line)
        self.function_name = function_name
        self.parameters = parameters
        self.body_statements = body_statements or []
        self.return_expr = return_expr


class FunctionCallNode(ParseTreeNode):
    #FunctionCall → I IZ identifier YR arg [AN YR arg]*
    def __init__(self, function_name, arguments, line=None):
        children = [function_name] + arguments
        super().__init__("FunctionCall", children, line=line)
        self.function_name = function_name
        self.arguments = arguments
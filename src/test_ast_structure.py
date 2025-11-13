"""
Unit tests for parser AST structure using unittest (built-in).
Asserts exact parse tree shapes for representative cases:
- SMOOSH concatenation
- GIMMEH with multiple identifiers
- Nested BOTH SAEM / DIFFRINT comparisons
"""

import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from parser.parse_tree_nodes import (
    ProgramNode, StatementListNode, StatementNode, PrintStatementNode,
    InputStatementNode, VariableDeclarationNode, BinaryExpressionNode,
    LiteralNode, VariableNode
)


class TestSmooshParsing(unittest.TestCase):
    """Test SMOOSH concatenation parsing."""

    def test_smoosh_two_operands(self):
        """SMOOSH with two operands: SMOOSH x AN y"""
        code = "HAI\nVISIBLE SMOOSH x AN y\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        # Navigate: Program → StatementList → Statement → PrintStatement
        assert tree.rule_name == 'Program'
        stmt_list = tree.children[1]  # StatementList
        stmt = stmt_list.children[0]  # First statement
        print_stmt = stmt.children[0]  # PrintStatement node
        assert isinstance(print_stmt, PrintStatementNode)
        
        # Smoosh node should be the expression in PrintStatement
        smoosh_expr = print_stmt.expression_node
        assert smoosh_expr.rule_name == 'Smoosh'
        assert len(smoosh_expr.children) == 2, f"Expected 2 operands, got {len(smoosh_expr.children)}"
        
        # Both operands should be variables
        assert smoosh_expr.children[0].rule_name == 'Variable'
        assert smoosh_expr.children[1].rule_name == 'Variable'

    def test_smoosh_three_operands(self):
        """SMOOSH with three operands: SMOOSH x AN y AN z"""
        code = "HAI\nVISIBLE SMOOSH x AN y AN z\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        smoosh_expr = print_stmt.expression_node
        
        assert smoosh_expr.rule_name == 'Smoosh'
        assert len(smoosh_expr.children) == 3, f"Expected 3 operands, got {len(smoosh_expr.children)}"

    def test_smoosh_mixed_operands(self):
        """SMOOSH with mixed operand types: SMOOSH "prefix" AN x AN 42"""
        code = 'HAI\nVISIBLE SMOOSH "prefix" AN x AN 42\nKTHXBYE'
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        smoosh_expr = print_stmt.expression_node
        
        assert smoosh_expr.rule_name == 'Smoosh'
        assert len(smoosh_expr.children) == 3
        
        # First operand: literal string
        assert smoosh_expr.children[0].rule_name == 'Literal'
        # Second operand: variable
        assert smoosh_expr.children[1].rule_name == 'Variable'
        # Third operand: literal number
        assert smoosh_expr.children[2].rule_name == 'Literal'


class TestMultiTargetGimmeh(unittest.TestCase):
    """Test GIMMEH with multiple target identifiers."""

    def test_gimmeh_single_target(self):
        """GIMMEH x (single target)"""
        code = "HAI\nGIMMEH x\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        input_stmt = stmt.children[0]
        assert isinstance(input_stmt, InputStatementNode)
        
        # Single target: identifier_nodes should be a list with one element
        assert len(input_stmt.identifier_nodes) == 1
        assert input_stmt.identifier_nodes[0].rule_name == 'Identifier'
        assert input_stmt.identifier_nodes[0].token['value'] == 'x'

    def test_gimmeh_two_targets(self):
        """GIMMEH a AN b (two targets)"""
        code = "HAI\nGIMMEH a AN b\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        input_stmt = stmt.children[0]
        assert isinstance(input_stmt, InputStatementNode)
        
        # Two targets
        assert len(input_stmt.identifier_nodes) == 2
        assert input_stmt.identifier_nodes[0].token['value'] == 'a'
        assert input_stmt.identifier_nodes[1].token['value'] == 'b'

    def test_gimmeh_three_targets(self):
        """GIMMEH a AN b AN c (three targets)"""
        code = "HAI\nGIMMEH a AN b AN c\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        input_stmt = stmt.children[0]
        assert isinstance(input_stmt, InputStatementNode)
        
        # Three targets
        assert len(input_stmt.identifier_nodes) == 3
        assert input_stmt.identifier_nodes[0].token['value'] == 'a'
        assert input_stmt.identifier_nodes[1].token['value'] == 'b'
        assert input_stmt.identifier_nodes[2].token['value'] == 'c'


class TestNestedComparisons(unittest.TestCase):
    """Test nested BOTH SAEM / DIFFRINT comparisons."""

    def test_nested_both_saem(self):
        """BOTH SAEM BOTH SAEM 1 AN 1 AN 0 (nested equality)"""
        code = "HAI\nVISIBLE BOTH SAEM BOTH SAEM 1 AN 1 AN 0\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        outer_expr = print_stmt.expression_node
        
        assert isinstance(outer_expr, BinaryExpressionNode)
        assert outer_expr.operator_node.rule_name == 'BOTH_SAEM'
        assert outer_expr.operator_node.rule_name == 'BOTH_SAEM'
        
        # Left operand should be another BOTH SAEM comparison
        left_expr = outer_expr.left_node
        assert isinstance(left_expr, BinaryExpressionNode)
        assert left_expr.operator_node.rule_name == 'BOTH_SAEM'
        
        # Right operand should be a literal 0
        right_expr = outer_expr.right_node
        assert isinstance(right_expr, LiteralNode)
        assert right_expr.token['value'] == '0'

    def test_diffrint_with_nested_arithmetic(self):
        """DIFFRINT SUM OF 1 AN 2 AN DIFFRINT 3 AN 4"""
        code = "HAI\nVISIBLE DIFFRINT SUM OF 1 AN 2 AN DIFFRINT 3 AN 4\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        outer_expr = print_stmt.expression_node
        
        assert isinstance(outer_expr, BinaryExpressionNode)
        assert outer_expr.operator_node.rule_name == 'DIFFRINT'
        
        # Left operand should be SUM OF arithmetic
        left_expr = outer_expr.left_node
        assert isinstance(left_expr, BinaryExpressionNode)
        assert left_expr.operator_node.rule_name == 'SUM_OF'
        
        # Right operand should be another DIFFRINT comparison
        right_expr = outer_expr.right_node
        assert isinstance(right_expr, BinaryExpressionNode)
        assert right_expr.operator_node.rule_name == 'DIFFRINT'

    def test_both_saem_with_arithmetic_operands(self):
        """BOTH SAEM BIGGR OF x AN y AN SMALLR OF x AN y"""
        code = "HAI\nVISIBLE BOTH SAEM BIGGR OF x AN y AN SMALLR OF x AN y\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        outer_expr = print_stmt.expression_node
        
        assert isinstance(outer_expr, BinaryExpressionNode)
        assert outer_expr.operator_node.rule_name == 'BOTH_SAEM'
        
        # Both operands should be arithmetic expressions (BIGGR_OF, SMALLR_OF)
        left_expr = outer_expr.left_node
        assert isinstance(left_expr, BinaryExpressionNode)
        assert left_expr.operator_node.rule_name == 'BIGGR_OF'
        
        right_expr = outer_expr.right_node
        assert isinstance(right_expr, BinaryExpressionNode)
        assert right_expr.operator_node.rule_name == 'SMALLR_OF'


class TestBooleanOperators(unittest.TestCase):
    """Test boolean operator parsing."""

    def test_not_operator(self):
        """NOT WIN (boolean negation)"""
        code = "HAI\nVISIBLE NOT WIN\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        not_expr = print_stmt.expression_node
        
        assert not_expr.rule_name == 'Not'
        assert len(not_expr.children) == 1
        assert isinstance(not_expr.children[0], LiteralNode)
        assert not_expr.children[0].token['value'] == 'WIN'

    def test_both_of_operator(self):
        """BOTH OF x AN y (binary AND)"""
        code = "HAI\nVISIBLE BOTH OF x AN y\nKTHXBYE"
        lexer = Lexer()
        parser = Parser(lexer)
        tree = parser.parse(code)
        
        stmt_list = tree.children[1]
        stmt = stmt_list.children[0]
        print_stmt = stmt.children[0]
        both_expr = print_stmt.expression_node
        
        assert both_expr.rule_name == 'BooleanExpression'
        assert both_expr.operator == 'BOTH OF'
        assert len(both_expr.operands) == 2


if __name__ == '__main__':
    unittest.main(verbosity=2)

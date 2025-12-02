"""
LOLCODE Interpreter
Evaluates a parse tree and executes LOLCODE programs.
"""

from platform import node
from parser.parse_tree_nodes import *


class InterpreterError(Exception):
    """Exception raised during program execution."""
    pass


class Interpreter:
    """Interpreter for LOLCODE parse trees."""
    
    def __init__(self):
        self.symbol_table = {}  # Variable storage
        self.it_value = None    # IT - implicit variable
        self.output = []        # Output buffer
        self.input_callback = None  # Callback for GIMMEH (input)
        
    def set_input_callback(self, callback):
        """Set callback function for handling GIMMEH input."""
        self.input_callback = callback
        
    def interpret(self, parse_tree):
        """
        Interpret a parse tree and execute the program.
        Returns the output as a string.
        """
        self.output = []
        self.it_value = None
        
        
        self.visit_program(parse_tree)
        
        return '\n'.join(self.output)
    
    def visit_program(self, node):
        """Visit Program node: HAI Statements KTHXBYE"""
        statements_node = node.statements_node
        if statements_node:
            self.visit_statement_list(statements_node)
    
    def visit_statement_list(self, node):
        """Visit StatementList node: execute all statements."""
        
        for i, stmt in enumerate(node.statements):
            
            if hasattr(stmt, 'children') and stmt.children:
                
                self.visit_statement(stmt)
    
    def visit_statement(self, node):
        """Visit Statement node: dispatch to specific statement handler."""
        if hasattr(node, 'rule_name') and node.rule_name == 'WAZZUP_Block':
            
            
            for child in node.children:
                if hasattr(child, 'rule_name'):
                    if child.rule_name == 'Statement':
                        self.visit_statement(child)
                    elif child.rule_name in ('VariableDeclaration', 'VariableDeclarationNode'):
                        self.visit_variable_declaration(child)
            return
        if not node.children:
            return

        actual_stmt = node.children[0]

        if actual_stmt.rule_name == 'WAZZUP_Block':
            for child in actual_stmt.children:
                if hasattr(child, 'rule_name'):
                    if child.rule_name == 'Statement':
                        self.visit_statement(child)
                    elif child.rule_name in ('VariableDeclaration', 'VariableDeclarationNode'):
                        
                        self.visit_variable_declaration(child)
            
            return

        # Dispatch based on statement type
        if isinstance(actual_stmt, VariableDeclarationNode):
            self.visit_variable_declaration(actual_stmt)
        elif isinstance(actual_stmt, PrintStatementNode):
            self.visit_print_statement(actual_stmt)
        elif isinstance(actual_stmt, InputStatementNode):
            self.visit_input_statement(actual_stmt)
        elif isinstance(actual_stmt, AssignmentNode):
            self.visit_assignment(actual_stmt)
        elif isinstance(actual_stmt, LoopNode):
            self.visit_loop(actual_stmt)
        elif isinstance(actual_stmt, ConditionalNode):
            self.visit_conditional(actual_stmt)
        elif isinstance(actual_stmt, SwitchNode):
            self.visit_switch(actual_stmt)
        elif actual_stmt.rule_name == 'FunctionCallStatement':
            # Function call as statement
            func_call = actual_stmt.children[0]
            self.visit_function_call(func_call)
    
    def visit_variable_declaration(self, node):
        """Visit VariableDeclaration: I HAS A var [ITZ expr]"""
        var_name = node.identifier_node.token['value']

        

        if node.expression_node:
            value = self.visit_expression(node.expression_node)
        else:
            if var_name in self.symbol_table:
                value = self.symbol_table[var_name]
            else:
                value = None
            

        self.symbol_table[var_name] = value
        self.it_value = value
        

    def visit_print_statement(self, node):
        """Visit PrintStatement: VISIBLE expr [expr]*"""
        expr_node = node.expression_node
        
        if expr_node.rule_name == 'VISIBLE_Expressions':
            parts = []
            for child in expr_node.children:
                value = self.visit_expression(child)

                
                if value is None:
                    parts.append('')
                else:
                    parts.append(self.to_string(value))
            output = ' '.join(parts)
        else:
            value = self.visit_expression(expr_node)

            
            if value is None:
                output = ''
            else:
                output = self.to_string(value)
        
        self.output.append(output)
        self.it_value = output
    
    def visit_input_statement(self, node):
        """Visit InputStatement: GIMMEH var [AN var]*"""
        for identifier_node in node.identifier_nodes:
            var_name = identifier_node.token['value']
            
            
            if self.input_callback:
                value = self.input_callback(var_name)
            else:
                value = ""  
            
            
            value = self.parse_input(value)
            
            self.symbol_table[var_name] = value
            self.it_value = value
    
    def visit_assignment(self, node):
        """Visit Assignment: var R expr"""
        var_name = node.identifier_node.token['value']
        value = self.visit_expression(node.expression_node)
        
        self.symbol_table[var_name] = value
        self.it_value = value
    
    def visit_typecast_assignment(self, node):
        var = node.identifier_node.token['value']
        target_type = node.type_token['type']
        old_value = self.symbol_table.get(var)
        new_value = self.cast_value(old_value, target_type)
        self.symbol_table[var] = new_value
        self.it_value = new_value

    def cast_value(self, value, target_type):
        if target_type == "NUMBR":
            return int(float(value))
        if target_type == "NUMBAR":
            return float(value)
        if target_type == "YARN":
            return str(value)
        if target_type == "TROOF":
            return "WIN" if value else "FAIL"


    def visit_loop(self, node):
        """Visit Loop: IM IN YR label UPPIN/NERFIN YR var WILE/TIL condition"""
        var_name = node.var_node.token['value']
        direction = node.direction_node.rule_name  # UPPIN or NERFIN
        
        # Initialize loop variable if not exists
        if var_name not in self.symbol_table:
            self.symbol_table[var_name] = 0
        
        # Execute loop
        max_iterations = 10000  # Safety limit
        iteration = 0
        
        while iteration < max_iterations:
            # Evaluate condition
            condition_value = self.visit_expression(node.condition_node)
            condition_bool = self.to_boolean(condition_value)
            
            
            
            if direction == 'UPPIN':
                if not condition_bool:
                    break
            else: 
                if condition_bool:
                    break
            
            for stmt in node.body_statements:
                self.visit_statement(stmt)
            
            current_value = self.symbol_table[var_name]
            if direction == 'UPPIN':
                self.symbol_table[var_name] = self.to_number(current_value) + 1
            else: 
                self.symbol_table[var_name] = self.to_number(current_value) - 1
            
            iteration += 1
    
    def visit_conditional(self, node):
        """Visit Conditional: expr O RLY? YA RLY ... [MEBBE ...] [NO WAI ...] OIC"""
        
        condition_value = self.visit_expression(node.condition_expr)
        condition_bool = self.to_boolean(condition_value)
        
        if condition_bool:
            
            for stmt in node.ya_rly_statements:
                self.visit_statement(stmt)
        else:
            
            executed = False
            for mebbe_expr, mebbe_stmts in node.mebbe_blocks:
                mebbe_value = self.visit_expression(mebbe_expr)
                if self.to_boolean(mebbe_value):
                    for stmt in mebbe_stmts:
                        self.visit_statement(stmt)
                    executed = True
                    break
            
           
            if not executed and node.no_wai_statements:
                for stmt in node.no_wai_statements:
                    self.visit_statement(stmt)
    
    def visit_switch(self, node):
        """Visit Switch: expr WTF? [OMG expr ...]* [OMGWTF ...] OIC"""
        # Evaluate switch expression
        switch_value = self.visit_expression(node.switch_expr)
        
        # Check each OMG case
        matched = False
        for omg_expr, omg_stmts in node.omg_cases:
            case_value = self.visit_expression(omg_expr)
            if self.values_equal(switch_value, case_value):
                
                for stmt in omg_stmts:
                    self.visit_statement(stmt)
                matched = True
                break
        
        # If no case matched, execute OMGWTF (default)
        if not matched and node.omgwtf_statements:
            for stmt in node.omgwtf_statements:
                self.visit_statement(stmt)
    
    def visit_expression(self, node):
        """Visit Expression: dispatch to appropriate handler."""
        if isinstance(node, LiteralNode):
            return self.visit_literal(node)
        elif isinstance(node, VariableNode):
            return self.visit_variable(node)
        elif isinstance(node, BinaryExpressionNode):
            return self.visit_binary_expression(node)
        elif isinstance(node, BooleanExpressionNode):
            return self.visit_boolean_expression(node)
        elif isinstance(node, NotNode):
            return self.visit_not_expression(node)
        elif isinstance(node, FunctionCallNode):
            return self.visit_function_call(node)
        elif node.rule_name == 'IT':
            return self.it_value
        elif node.rule_name == 'Smoosh':
            return self.visit_smoosh(node)
        else:
            raise InterpreterError(f"Unknown expression type: {node.rule_name}")
    
    def visit_literal(self, node):
        """Visit Literal: return literal value."""
        token = node.literal_token
        token_type = token['type']
        value = token['value']
        
        if token_type == 'NUMBR':
            return int(value)
        elif token_type == 'NUMBAR':
            return float(value)
        elif token_type == 'YARN':
            # Remove quotes
            return value.strip('"')
        elif token_type == 'TROOF':
            return value == 'WIN'
        elif token_type == 'NOOB':
            return None
        else:
            return value
    
    def visit_variable(self, node):
        """Visit Variable: return variable value from symbol table."""
        var_name = node.identifier_node.token['value']

        

        if var_name not in self.symbol_table:
            raise InterpreterError(f"Undefined variable: {var_name}")

        return self.symbol_table[var_name]
    
    def visit_binary_expression(self, node):
        """Visit BinaryExpression: arithmetic or comparison operation."""
        operator = node.operator_node.rule_name
        left_value = self.visit_expression(node.left_node)
        right_value = self.visit_expression(node.right_node)
        
        # Arithmetic operations
        if operator == 'SUM_OF':
            return self.to_number(left_value) + self.to_number(right_value)
        elif operator == 'DIFF_OF':
            return self.to_number(left_value) - self.to_number(right_value)
        elif operator == 'PRODUKT_OF':
            return self.to_number(left_value) * self.to_number(right_value)
        elif operator == 'QUOSHUNT_OF':
            right_num = self.to_number(right_value)
            if right_num == 0:
                raise InterpreterError("Division by zero")
            return self.to_number(left_value) // right_num  # Integer division
        elif operator == 'MOD_OF':
            right_num = self.to_number(right_value)
            if right_num == 0:
                raise InterpreterError("Modulo by zero")
            return self.to_number(left_value) % right_num
        elif operator == 'BIGGR_OF':
            return max(self.to_number(left_value), self.to_number(right_value))
        elif operator == 'SMALLR_OF':
            return min(self.to_number(left_value), self.to_number(right_value))
        
        # Comparison operations
        elif operator == 'BOTH_SAEM':
            return self.values_equal(left_value, right_value)
        elif operator == 'DIFFRINT':
            return not self.values_equal(left_value, right_value)
        
        # String concatenation
        elif operator == 'CONCAT':
            return self.to_string(left_value) + self.to_string(right_value)
        
        else:
            raise InterpreterError(f"Unknown operator: {operator}")
    
    def visit_boolean_expression(self, node):
        """Visit BooleanExpression: AND, OR, XOR, ALL OF, ANY OF."""
        operator = node.operator
        operands = [self.visit_expression(op) for op in node.operands]
        operand_bools = [self.to_boolean(op) for op in operands]
        
        if operator == 'BOTH OF':
            return operand_bools[0] and operand_bools[1]
        elif operator == 'EITHER OF':
            return operand_bools[0] or operand_bools[1]
        elif operator == 'WON OF':
            # XOR: exactly one true
            return operand_bools[0] != operand_bools[1]
        elif operator == 'ALL OF':
            return all(operand_bools)
        elif operator == 'ANY OF':
            return any(operand_bools)
        else:
            raise InterpreterError(f"Unknown boolean operator: {operator}")
    
    def visit_not_expression(self, node):
        """Visit NOT expression: logical negation."""
        value = self.visit_expression(node.expression_node)
        return not self.to_boolean(value)
    
    def visit_smoosh(self, node):
        """Visit SMOOSH: string concatenation."""
        parts = []
        for operand in node.operands:
            value = self.visit_expression(operand)
            if value is None:
                raise InterpreterError("Cannot concatenate NOOB in SMOOSH (use explicit typecast)")
            parts.append(self.to_string(value))
        return ''.join(parts)
    
    def visit_function_call(self, node):
        """Visit FunctionCall: I IZ func YR arg ..."""
        # Function calls not fully implemented - placeholder
        func_name = node.function_name.token['value']
        raise InterpreterError(f"Function calls not yet implemented: {func_name}")
    
    # Helper methods
    
    def explicit_typecast(self, value, target_type):
        """Explicitly typecast value to target_type.
        NOOB can be explicitly typecast to empty/zero values:
        - NOOB -> NUMBR: 0
        - NOOB -> NUMBAR: 0.0
        - NOOB -> YARN: "" (empty string)
        - NOOB -> TROOF: FAIL (FALSE)
        """

        # NOOB typecasting
        if value is None:
            if target_type == 'NUMBR':
                return 0
            elif target_type == 'NUMBAR':
                return 0.0
            elif target_type == 'YARN':
                return ""
            elif target_type == 'TROOF':
                return False
            else:
                raise InterpreterError(f"Unknown target type for typecast: {target_type}")
        
        # Non-NOOB typecasting
        if target_type == 'NUMBR':
            return int(self.to_number(value))
        elif target_type == 'NUMBAR':
            return float(self.to_number(value))
        elif target_type == 'YARN':
            return self.to_string(value)
        elif target_type == 'TROOF':
            return self.to_boolean(value)
        else:
           raise InterpreterError(f"Unknown type: {target_type}")
       

    def to_number(self, value):
        """Convert value to number (int or float)."""
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, str):
            # Try to parse as number
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return 0  # Default for non-numeric strings
        elif value is None:
            return 0
        else:
            return 0
    
    def to_string(self, value):
        """Convert value to string."""
        if isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        elif value is None:
            raise InterpreterError("Cannot implicitly convert NOOB to YARN (use explicit typecast)")
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    
    def to_boolean(self, value):
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        elif value is None:
            return False
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            # Empty string or "FAIL" is false
            return value != "" and value != "FAIL" and value != "0"
        else:
            return True
    
    def values_equal(self, left, right):
        """Check if two values are equal."""
        # Type coercion for comparison
        if type(left) == type(right):
            return left == right
        
        # Try numeric comparison
        try:
            return self.to_number(left) == self.to_number(right)
        except:
            # Fall back to string comparison
            return self.to_string(left) == self.to_string(right)
    
    def parse_input(self, value):
        """Parse input string to appropriate type."""
        if not value:
            return None
        
        # Try parsing as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Check for boolean
        if value == 'WIN':
            return True
        elif value == 'FAIL':
            return False
        
        # Otherwise return as string
        return value
    
    def get_symbol_table(self):
        """Get current symbol table for display."""
        return self.symbol_table.copy()
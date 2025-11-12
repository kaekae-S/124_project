"""
Recursive Descent Parser for LOLCODE
This parser consumes tokens from the Lexer and builds an AST
"""

from lexer.lexer import Lexer
from parser.ast_nodes import (
    Program, Statement, Expression,
    Literal, Variable, BinaryOp,
    VariableDeclaration, PrintStatement, InputStatement
)
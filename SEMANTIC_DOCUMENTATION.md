# Semantic Analysis Documentation

## Overview

The semantic analyzer (`src/parser/semantic.py`) performs semantic validation on LOLCODE programs after parsing. It checks that:

1. **Variables are declared before use** - prevents undefined variable references
2. **Variables are not declared twice** - prevents duplicate declarations in same scope
3. **Functions are defined before called** - tracks function definitions and arity
4. **Function calls have correct arity** - validates argument count matches parameter count
5. **Scope is properly managed** - handles nested scopes (functions, loops, conditionals)

---

## What the Semantic Analyzer Does

### Entry Point
```python
analyzer = SemanticAnalyzer()
errors = analyzer.analyze(parse_tree)  # Returns list of error strings
```

- **Input**: AST from `Parser.parse()`
- **Output**: List of error messages (empty if valid)
- **Returns**: Human-readable error strings with line numbers

### Two-Pass Analysis

The analyzer uses a **two-pass approach**:

1. **First Pass** - `_collect_declarations()`: Collects all variable and function declarations
   - Scans entire program to find all `I HAS A` (variable declarations)
   - Finds all `HOW IZ I` (function definitions)
   - Detects duplicate declarations
   - **Why?** Allows forward references in linear code

2. **Second Pass** - `_visit_statement_wrapper()`: Validates all usage
   - Checks every variable reference is declared
   - Validates function calls have correct arity
   - Traverses nested blocks with proper scope management

---

## Errors Detected

### 1. Undefined Variable Usage
**Error Message**: `"Use of undeclared variable '{name}'"`

When a variable is used but never declared:
```lolcode
HAI
VISIBLE x           BTW Error: x not declared
KTHXBYE
```

**Contexts**:
- `VISIBLE x` - printing undefined variable
- `x R 5` - assigning to undefined variable
- `y R SUM OF x AN 5` - using in arithmetic
- `BOTH SAEM x AN 5` - using in comparison
- `GIMMEH x` - reading input to undefined variable

### 2. Duplicate Variable Declaration
**Error Message**: `"Duplicate declaration of variable '{name}'"`

When same variable declared twice in same scope:
```lolcode
HAI
WAZZUP
    I HAS A x ITZ 5
    I HAS A x ITZ 10      BTW Error: x already declared
BUHBYE
KTHXBYE
```

### 3. Undefined Function Call
**Error Message**: `"Call to undefined function '{name}'"`

When calling function that doesn't exist:
```lolcode
HAI
I HAS A result ITZ I IZ undefined_func YR 42
KTHXBYE
```

### 4. Function Arity Mismatch
**Error Message**: `"Function '{name}' called with {N} arg(s) but expects {M}"`

When function called with wrong number of arguments:
```lolcode
HAI
HOW IZ I add YR a AN YR b
    FOUND YR SUM OF a AN b
IF U SAY SO

I HAS A result ITZ I IZ add YR 2    BTW Error: add expects 2 args, got 1
KTHXBYE
```

### 5. GIMMEH (Input) to Undefined Variable
**Error Message**: `"Input target '{name}' is not declared"`

When reading input into undefined variable:
```lolcode
HAI
GIMMEH x                BTW Error: x not declared
KTHXBYE
```

---

## Scope Management

### Global Scope
All variables in global scope are accessible everywhere:

```lolcode
HAI
WAZZUP
    I HAS A x ITZ 42
BUHBYE

VISIBLE x              BTW OK - x declared in WAZZUP, visible globally
KTHXBYE
```

### Function Scope
Parameters are local to function:

```lolcode
HAI
HOW IZ I add YR a AN YR b
    FOUND YR SUM OF a AN b
IF U SAY SO

VISIBLE a              BTW Error: a is function parameter, not in global scope
KTHXBYE
```

### Nested Block Scope
Loops, conditionals create nested scopes (current implementation):

```lolcode
HAI
I HAS A outer ITZ 42

IM IN YR loop
    I HAS A inner ITZ 10
    VISIBLE outer        BTW OK - outer is in parent scope
    VISIBLE inner        BTW OK - inner is in loop scope
IM OUTTA YR loop

VISIBLE inner           BTW OK - scope rules allow access after loop
KTHXBYE
```

---

## How to Use

### In Code
```python
from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer

# 1. Tokenize
lexer = Lexer()
tokens = lexer.tokenize(code)

# 2. Parse
parser = Parser(lexer)
tree = parser.parse(code)

# 3. Analyze semantics
analyzer = SemanticAnalyzer()
errors = analyzer.analyze(tree)

# 4. Check results
if errors:
    for error in errors:
        print(f"ERROR: {error}")
else:
    print("Program is semantically valid!")
```

### With GUI
The semantic analyzer can be integrated into GUI for real-time validation:

```python
def execute_code(self):
    code = self.code_editor.get("1.0", "end-1c")
    
    # ... existing lexer/parser code ...
    
    # Add semantic analysis
    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(tree)
    
    if semantic_errors:
        for error in semantic_errors:
            self.output_text.insert("end", f"SEMANTIC ERROR: {error}\n")
        return
    
    # Proceed with execution if no errors
```

---

## Test Coverage

### Unit Tests (`src/test_semantic.py`)
**19 tests** covering:

#### Variables
- ✅ WAZZUP variable declaration
- ✅ Undefined variable in VISIBLE
- ✅ Assignment to undefined variable
- ✅ Duplicate variable in WAZZUP
- ✅ Multiple errors detection

#### Operations
- ✅ Arithmetic with undefined variables
- ✅ Comparisons (BOTH SAEM, DIFFRINT)
- ✅ Boolean operations (EITHER OF, BOTH OF)
- ✅ Input statements (GIMMEH)
- ✅ String operations (SMOOSH)

#### Sample Files
- ✅ Sample 02_gimmeh.lol - input validation
- ✅ Sample 03_arith.lol - arithmetic expressions
- ✅ Sample 05_bool.lol - boolean operations
- ✅ Sample 06_comparison.lol - comparisons
- ✅ Sample 07_ifelse.lol - conditionals

**Result**: ✅ All 19 tests pass (100%)

---

## Architecture

### Class Structure
```
SemanticAnalyzer
├── analyze(program_node) -> List[str]
├── _collect_declarations(stmt_node)
├── _enter_scope() / _exit_scope()
├── _declare_var(name, line)
├── _is_declared(name) -> bool
├── _visit_statement_wrapper(stmt_node)
├── _visit_variable_declaration(node)
├── _visit_assignment(node)
├── _visit_input_statement(node)
├── _visit_print_statement(node)
├── _visit_function_declaration(node)
├── _visit_function_call(node)
├── _visit_loop(node)
├── _visit_conditional(node)
├── _visit_switch(node)
├── _visit_node(node)
└── _get_identifier_name(node) -> str
```

### Key Data Structures
- `scopes: List[Dict[str, bool]]` - Stack of scope dicts (key=var_name, value=True)
- `functions: Dict[str, int]` - Maps function_name -> arity (parameter count)
- `errors: List[str]` - Accumulated error messages

### Visitor Pattern
Uses visitor pattern to traverse AST:
- `_visit_statement_wrapper()` - dispatches to specific visitors
- `_visit_variable_declaration()` - handles `I HAS A`
- `_visit_assignment()` - handles `x R` (assignment)
- `_visit_input_statement()` - handles `GIMMEH`
- `_visit_print_statement()` - handles `VISIBLE`
- `_visit_function_call()` - handles `I IZ`
- `_visit_loop()` - handles `IM IN YR`
- `_visit_conditional()` - handles `YA RLY` / `NO WAI`
- `_visit_switch()` - handles `SWITCH` / `OMG`



# LOLCODE Interpreter

A complete LOLCODE interpreter implementation with a graphical user interface, featuring a lexer, recursive descent parser, and execution engine.

## Features

### Language Support

The interpreter supports the following LOLCODE language features:

#### Core Statements
- **Variable Declarations**: `I HAS A var [ITZ expr]`
- **Print Statements**: `VISIBLE expr`
- **Input Statements**: `GIMMEH var [AN var]*`
- **Assignments**: `variable R expression`

#### Control Flow
- **Conditionals**: `expression O RLY? YA RLY ... [MEBBE expr ...]* [NO WAI ...] OIC`
- **Switch Statements**: `expression WTF? [OMG expr ... [GTFO]]* [OMGWTF ...] OIC`
- **Loops**: 
  - Incrementing: `IM IN YR label UPPIN YR var WILE condition ... IM OUTTA YR label`
  - Decrementing: `IM IN YR label NERFIN YR var TIL condition ... IM OUTTA YR label`

#### Functions
- **Function Declarations**: `HOW IZ I functionName YR param [AN YR param]* [statements] FOUND YR expression IF U SAY SO`
- **Function Calls**: `I IZ functionName YR arg [AN YR arg]*`
- **Return Value Access**: `IT` (refers to last function call result)

#### Expressions
- **Arithmetic Operations**: `SUM OF`, `DIFF OF`, `PRODUKT OF`, `QUOSHUNT OF`, `MOD OF`
- **Comparison Operations**: `BOTH SAEM`, `DIFFRINT`, `BIGGR OF`, `SMALLR OF`
- **Boolean Operations**: `BOTH OF`, `EITHER OF`, `WON OF`, `ALL OF`, `ANY OF`, `NOT`
- **String Concatenation**: `+` operator
- **Nested Expressions**: All operations support arbitrary nesting

#### Data Types
- **NUMBR**: Integers (e.g., `42`, `-7`)
- **NUMBAR**: Floating-point numbers (e.g., `3.14`, `-2.5`)
- **YARN**: Strings (e.g., `"hello"`, `"world"`)
- **TROOF**: Booleans (`WIN`, `FAIL`)
- **NOOB**: Uninitialized/null value

## Project Structure

```
124_project/
├── src/
│   ├── lexer/           # Lexical analyzer
│   │   └── lexer.py     # Tokenizes LOLCODE source code
│   ├── parser/          # Recursive descent parser
│   │   ├── parser.py    # Main parser implementation
│   │   └── parse_tree_nodes.py  # AST node definitions
│   ├── gui/             # Graphical user interface
│   │   └── lolcode_interpreter_gui.py
│   ├── tests/           # Test samples
│   │   └── samples/     # LOLCODE sample files
│   └── main.py          # Command-line interface
├── run_gui.py           # GUI launcher
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```
   Note: The project uses only Python standard library (tkinter for GUI).

## Usage

### Graphical User Interface

Launch the GUI interpreter:

```bash
python run_gui.py
```

The GUI provides:
- **Code Editor**: Write or load LOLCODE programs
- **Lexemes Table**: View tokenized output
- **Symbol Table**: View variable values during execution
- **Output Console**: See program output and errors
- **File Operations**: Open, save, and create new files

### Command Line

Run LOLCODE files from the command line:

```bash
python src/main.py <input_file.lol>
```

## Test Files

The project includes comprehensive test samples in `src/tests/samples/`:

- `01_variables.lol` - Variable declarations and basic operations
- `02_gimmeh.lol` - Input statements
- `03_arith.lol` - Arithmetic operations
- `04_smoosh_assign.lol` - String concatenation
- `05_bool.lol` - Boolean operations
- `06_comparison.lol` - Comparison operations
- `07_ifelse.lol` - Conditional statements
- `08_switch.lol` - Switch statements
- `09_loops.lol` - Loop constructs
- `10_functions.lol` - Function definitions and calls
- `11_nested_loops.lol` - Nested loop examples
- `12_nested_arithmetic.lol` - Complex nested arithmetic
- `13_nested_conditionals.lol` - Nested conditional statements
- `14_loops_with_conditionals.lol` - Loops with nested conditionals
- `15_complex_expressions.lol` - Complex expression examples
- `16_edge_cases.lol` - Edge cases and boundary conditions
- `17_functions_nested.lol` - Nested function calls
- `18_mixed_nesting.lol` - Mixed nesting scenarios

## Example Program

```lolcode
HAI
    WAZZUP
        I HAS A x
        I HAS A y
    BUHBYE

    x R 10
    y R 5

    VISIBLE "Sum: " + SUM OF x AN y
    VISIBLE "Difference: " + DIFF OF x AN y

    BIGGR OF x AN y
    O RLY?
        YA RLY
            VISIBLE "x is bigger"
        NO WAI
            VISIBLE "y is bigger or equal"
    OIC

    IM IN YR loop UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 5
        VISIBLE "Iteration: " + i
    IM OUTTA YR loop
KTHXBYE
```

## Architecture

### Lexer
The lexical analyzer (`src/lexer/lexer.py`) converts LOLCODE source code into tokens:
- Recognizes keywords (single and multi-word)
- Handles literals (numbers, strings, booleans)
- Identifies identifiers and operators
- Removes comments (BTW and OBTW...TLDR)

### Parser
The recursive descent parser (`src/parser/parser.py`) builds an Abstract Syntax Tree (AST):
- Implements operator precedence
- Handles nested structures (loops, conditionals, functions)
- Provides detailed error messages with line numbers
- Supports all LOLCODE language constructs

### GUI
The graphical interface (`src/gui/lolcode_interpreter_gui.py`) provides:
- Syntax highlighting (via lexer output)
- Real-time parsing feedback
- Symbol table visualization
- Execution console

## Error Handling

The parser provides comprehensive error detection:
- Missing or unexpected tokens
- Syntax errors with line numbers
- Type mismatches
- Undefined variables
- Invalid expressions

## Development

### Running Tests

Test the parser with sample files:

```bash
python src/test_parser.py
python src/test_parser_runner.py
python src/validate_samples.py
```

### Error Detection Tests

Run comprehensive error detection:

```bash
python test_comprehensive_error_detection.py
```

## Limitations

- Function execution is simulated (not fully implemented)
- Some advanced LOLCODE features may not be supported
- Error recovery is limited (parser stops at first error)

## License

This project is part of a CMSC 124 course assignment.

## Author

Developed as part of CMSC 124 - Programming Languages course project.


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
# LOLCODE Interpreter (124_project)

Simple README summarizing the core components (lexer, parser, semantic analyzer)
and instructions for running the GUI.

Project info
- Project: 124 - LOLCODE Compiler/Interpreter
- Author: Aaron

Overview
--------
This repository implements a small LOLCODE toolchain and a Tkinter GUI.
It is organized as a three-stage pipeline:

- Lexer: tokenizes source code into tokens (keywords, identifiers, literals).
- Parser: recursive descent parser that produces an AST (parse tree).
- Semantic Analyzer: multi-pass validator that checks scoping, undefined variables,
  function arity, control-flow rules (e.g., break/return placement), and other
  semantic constraints.

Files of interest
-----------------
- `src/lexer/lexer.py` — Lexer implementation (token patterns, comment handling).
- `src/parser/parser.py` — Recursive descent parser, builds parse tree nodes.
- `src/parser/parse_tree_nodes.py` — AST node classes used by the parser.
- `src/parser/semantic.py` — Semantic analyzer (declaration collection + validation).
- `src/gui/lolcode_interpreter_gui.py` — Tkinter-based GUI (editor, tables, console).
- `run_gui.py` — Small launcher script that starts the GUI.

How the components interact
---------------------------
1. The GUI or a CLI script reads the source file.
2. The Lexer converts source text → token list.
3. The Parser converts tokens → parse tree (AST). Syntax errors raised here.
4. The Semantic Analyzer inspects the AST and returns human-readable errors.
5. If no semantic errors, the GUI runs a simplified simulation that demonstrates
   variable bindings and `VISIBLE` output (full interpreter is partial).

Running the GUI (desktop)
-------------------------
Requirements:
- Python 3.7+ (Windows: ensure `tkinter` is installed; most Python distributions include it)

Start the GUI from project root:

```powershell
python run_gui.py
```

What the GUI shows:
- Code editor: write or open `.lol` files
- Lexemes table: lexer token output
- Symbol table: variables and their last values (simulation)
- Output console: program output and semantic/syntax errors

Using the GUI:
1. Write or open a `.lol` file using the Open/Save buttons.
2. Click `EXECUTE` to run the three-stage pipeline (lexer → parser → semantic).
3. If semantic errors are found they appear in the output console and in a dialog.
4. Otherwise the GUI displays `=== PROGRAM OUTPUT ===` and the simulated output.

Command-line utilities
----------------------
- `python src/main.py` — helper script to dump lexer tokens for sample files.
- `validate_semantic_comprehensive.py` and `validate_semantic_all.py` — scripts
  that run the pipeline against sample files in `src/tests/samples/`.

Testing
-------
The repository contains tests and sample `.lol` programs under `src/tests/samples/`.
Run the provided test scripts (they use the project `src` path):

```powershell
python test_gui_integration.py
python test_semantic_comprehensive.py
```

Notes & limitations
-------------------
- The runtime/execution in the GUI is a simplified simulation (not a full evaluator).
- The semantic analyzer is comprehensive (declarations, scopes, function arity,
  break/return placement), but complex runtime features (full function calling,
  closures) are only partially simulated.

References
----------
- Recursive descent parsing: https://en.wikipedia.org/wiki/Recursive_descent_parser
- Semantic analysis (compiler design): https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)

License
-------
This project was developed as part of CMSC 124 coursework.

Author
------
Aaron



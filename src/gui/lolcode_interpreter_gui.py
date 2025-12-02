# LOL CODE Interpreter GUI
# Provides a graphical interface to write, parse, and execute LOLCODE programs

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import sys
import os

# Add src directory to path so we can import lexer, parser, and semantic modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexer.lexer import Lexer
from parser.parser import Parser
from parser.semantic import SemanticAnalyzer
from interpreter.interpreter import Interpreter


class LOLCODEInterpreterGUI:
    def __init__(self, root):
        """Initialize the GUI application with lexer, parser, and semantic analyzer."""
        self.root = root
        self.root.title("LOL CODE Interpreter")
        self.current_file = None
        
        # Set up the three-stage compiler pipeline
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Build all visual components
        self.create_widgets()
        
    def create_widgets(self):
        """Build the complete layout with editor, tables, button, and console."""
        
        # Main container frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Top: Menu bar with file operations
        self.create_menu_bar(main_frame)
        
        # Left: Code editor for writing LOLCODE
        self.create_code_editor(main_frame)
        
        # Right: Tables for analysis output
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        self.create_lexemes_table(right_frame)    # Token list
        self.create_symbol_table(right_frame)     # Variable list
        
        # Execute button spanning both columns
        self.create_execute_button(main_frame)
        
        # Bottom: Console for output and results
        self.create_output_console(main_frame)
        
    def create_menu_bar(self, parent):
        """Create header with file name display and buttons for Open, Save, Save As, New."""
        menu_frame = ttk.Frame(parent)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Left side: display current filename
        self.file_label = ttk.Label(menu_frame, text="(None) LOL CODE Interpreter", 
                                     font=("Arial", 12, "bold"))
        self.file_label.pack(side=tk.LEFT)
        
        # Right side: file operation buttons
        button_frame = ttk.Frame(menu_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save As", command=self.save_file_as).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        
    def create_code_editor(self, parent):
        """Create code editor text area."""
        editor_frame = ttk.LabelFrame(parent, text="Code Editor", padding="5")
        editor_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        
        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#f8f8f8",
            fg="#333333",
            insertbackground="#000000",
            width=50,
            height=20
        )
        self.code_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add some default code
        default_code = """HAI
I HAS A var ITZ 12
VISIBLE "noot noot" var
KTHXBYE"""
        self.code_editor.insert("1.0", default_code)
        
    def create_lexemes_table(self, parent):
        """Create table showing tokens (lexemes) and their types from lexer output."""
        lexemes_frame = ttk.LabelFrame(parent, text="Lexemes Table", padding="5")
        lexemes_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        lexemes_frame.columnconfigure(0, weight=1)
        lexemes_frame.rowconfigure(0, weight=1)
        
        # Create table with Lexeme and Classification columns
        columns = ("Lexeme", "Classification")
        self.lexemes_tree = ttk.Treeview(lexemes_frame, columns=columns, show="headings", height=10)
        
        # Set column headers and widths
        self.lexemes_tree.heading("Lexeme", text="Lexeme")
        self.lexemes_tree.heading("Classification", text="Classification")
        self.lexemes_tree.column("Lexeme", width=150, anchor=tk.W)
        self.lexemes_tree.column("Classification", width=200, anchor=tk.W)
        
        # Add scrollbar to table
        lexemes_scroll = ttk.Scrollbar(lexemes_frame, orient=tk.VERTICAL, command=self.lexemes_tree.yview)
        self.lexemes_tree.configure(yscrollcommand=lexemes_scroll.set)
        
        self.lexemes_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lexemes_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_symbol_table(self, parent):
        """Create table showing variables (identifiers) and their values during execution."""
        symbol_frame = ttk.LabelFrame(parent, text="Symbol Table", padding="5")
        symbol_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        symbol_frame.columnconfigure(0, weight=1)
        symbol_frame.rowconfigure(0, weight=1)
        
        # Create table with Identifier and Value columns
        columns = ("Identifier", "Value")
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=columns, show="headings", height=10)
        
        # Set column headers and widths
        self.symbol_tree.heading("Identifier", text="Identifier")
        self.symbol_tree.heading("Value", text="Value")
        self.symbol_tree.column("Identifier", width=150, anchor=tk.W)
        self.symbol_tree.column("Value", width=200, anchor=tk.W)
        
        # Add scrollbar to table
        symbol_scroll = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, command=self.symbol_tree.yview)
        self.symbol_tree.configure(yscrollcommand=symbol_scroll.set)
        
        self.symbol_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        symbol_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_execute_button(self, parent):
        """Create execute button."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.execute_button = ttk.Button(
            button_frame,
            text="EXECUTE",
            command=self.execute_code,
            style="Accent.TButton"
        )
        self.execute_button.pack(fill=tk.X)
        
    def create_output_console(self, parent):
        """Create output console."""
        console_frame = ttk.LabelFrame(parent, text="Output Console", padding="5")
        console_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.output_console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#000000",
            height=8,
            state=tk.DISABLED
        )
        self.output_console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def open_file(self):
        """Open a .lol file and display its contents in the code editor."""
        # Show file browser dialog
        filename = filedialog.askopenfilename(
            title="Open LOLCODE File",
            filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Read file and insert into editor
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", content)
                self.current_file = filename
                self.file_label.config(text=f"{os.path.basename(filename)} - LOL CODE Interpreter")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
                
    def save_file(self):
        """Save the current file. If no file is open, prompt for new file name."""
        if self.current_file:
            try:
                # Write editor content to file
                content = self.code_editor.get("1.0", tk.END + "-1c")
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save the editor content to a new file with user-chosen name."""
        # Show save dialog
        filename = filedialog.asksaveasfilename(
            title="Save LOLCODE File",
            defaultextension=".lol",
            filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Write editor content to new file
                content = self.code_editor.get("1.0", tk.END + "-1c")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = filename
                self.file_label.config(text=f"{os.path.basename(filename)} - LOL CODE Interpreter")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
                
    def new_file(self):
        """Clear the editor and reset to create a new file."""
        self.code_editor.delete("1.0", tk.END)
        self.current_file = None
        self.file_label.config(text="(None) LOL CODE Interpreter")
        self.clear_tables()
        
    def clear_tables(self):
        """Remove all rows from lexemes table, symbol table, and clear output console."""
        # Clear lexemes table
        for item in self.lexemes_tree.get_children():
            self.lexemes_tree.delete(item)
        # Clear symbol table
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
        # Clear output console
        self.output_console.config(state=tk.NORMAL)
        self.output_console.delete("1.0", tk.END)
        self.output_console.config(state=tk.DISABLED)
        
    def execute_code(self):
        """Execute the LOLCODE program."""
        code = self.code_editor.get("1.0", tk.END + "-1c")
        
        # Clear previous results
        for item in self.lexemes_tree.get_children():
            self.lexemes_tree.delete(item)
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
        self.output_console.config(state=tk.NORMAL)
        self.output_console.delete("1.0", tk.END)
        
        try:
            # Tokenize
            tokens = self.lexer.tokenize(code)
            
            # Populate lexemes table
            for token in tokens:
                lexeme = token['value']
                classification = self.get_token_classification(token['type'], lexeme)
                self.lexemes_tree.insert("", tk.END, values=(lexeme, classification))
            
            # Parse
            parse_tree = self.parser.parse(code)
            
            # Execute the program using interpreter
            interpreter = Interpreter()
            
            # Set input callback for GIMMEH statements
            def input_handler(var_name):
                # Show input dialog
                value = simpledialog.askstring("Input", f"Enter value for {var_name}:")
                return value if value else ""
            
            interpreter.set_input_callback(input_handler)
            
            # Run the interpreter
            output = interpreter.interpret(parse_tree)
            
            # Display output
            if output:
                self.output_console.insert(tk.END, output + "\n")
            else:
                self.output_console.insert(tk.END, "(No output)\n")
            
            # Update symbol table
            symbol_table = interpreter.get_symbol_table()
            for identifier, value in symbol_table.items():
                # Format value for display
                if isinstance(value, bool):
                    display_value = 'WIN' if value else 'FAIL'
                elif value is None:
                    display_value = 'NOOB'
                else:
                    display_value = str(value)
                self.symbol_tree.insert("", tk.END, values=(identifier, display_value))
            
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}\n"
            self.output_console.insert(tk.END, error_msg, "error")
            messagebox.showerror("Syntax Error", str(e))
        except Exception as e:
            error_msg = f"Runtime Error: {str(e)}\n"
            self.output_console.insert(tk.END, error_msg, "error")
            messagebox.showerror("Runtime Error", str(e))
        finally:
            self.output_console.config(state=tk.DISABLED)
            # Configure error text color
            self.output_console.tag_config("error", foreground="red")
            
    def get_token_classification(self, token_type, value):
        """Convert token type to a descriptive label for display in lexemes table."""
        keyword_classifications = {
            'HAI': 'Code Delimiter',
            'KTHXBYE': 'Code Delimiter',
            'I HAS A': 'Variable Declaration',
            'ITZ': 'Variable Assignment',
            'VISIBLE': 'Output Keyword',
            'GIMMEH': 'Input Keyword',
            'R': 'Assignment Operator',
            'WAZZUP': 'Block Start',
            'BUHBYE': 'Block End',
            'O RLY?': 'Conditional Keyword',
            'YA RLY': 'Conditional Keyword',
            'MEBBE': 'Conditional Keyword',
            'NO WAI': 'Conditional Keyword',
            'OIC': 'Block End',
            'WTF?': 'Switch Keyword',
            'OMG': 'Switch Keyword',
            'OMGWTF': 'Switch Keyword',
            'GTFO': 'Control Flow',
            'IM IN YR': 'Loop Keyword',
            'IM OUTTA YR': 'Loop Keyword',
            'UPPIN': 'Loop Keyword',
            'NERFIN': 'Loop Keyword',
            'WILE': 'Loop Keyword',
            'TIL': 'Loop Keyword',
            'YR': 'Keyword',
            'AN': 'Keyword',
            'SUM OF': 'Arithmetic Operator',
            'DIFF OF': 'Arithmetic Operator',
            'PRODUKT OF': 'Arithmetic Operator',
            'QUOSHUNT OF': 'Arithmetic Operator',
            'MOD OF': 'Arithmetic Operator',
            'BIGGR OF': 'Comparison Operator',
            'SMALLR OF': 'Comparison Operator',
            'BOTH SAEM': 'Comparison Operator',
            'DIFFRINT': 'Comparison Operator',
            'BOTH OF': 'Boolean Operator',
            'EITHER OF': 'Boolean Operator',
            'WON OF': 'Boolean Operator',
            'ALL OF': 'Boolean Operator',
            'ANY OF': 'Boolean Operator',
            'NOT': 'Boolean Operator',
            'HOW IZ I': 'Function Keyword',
            'FOUND YR': 'Function Keyword',
            'IF U SAY SO': 'Function Keyword',
            'I IZ': 'Function Keyword',
            'SMOOSH': 'String Operator',
            'MKAY': 'Keyword',
            'A': 'Keyword',
            'IT': 'Special Variable',
            'O': 'Unknown Keyword',
            'RLY': 'Unknown Keyword',
        }
        
        type_classifications = {
            'Identifier': 'Variable Identifier',
            'NUMBR': 'Literal',
            'NUMBAR': 'Literal',
            'YARN': 'Literal',
            'TROOF': 'Literal',
            'NOOB': 'Literal',
            'Operator': 'Operator',
        }
        
        # Handle keywords first
        if token_type == 'Keyword':
            return keyword_classifications.get(value, 'Keyword')
        # Handle other token types
        elif token_type in type_classifications:
            return type_classifications[token_type]
        else:
            return token_type
            
    def simulate_execution(self, code, tokens):
        """Extract variables and handle VISIBLE output to populate symbol table and console."""
        # Parse tokens to find variable declarations, assignments, and VISIBLE statements
        # This is simplified - a full interpreter would evaluate all expressions
        
        variables = {}
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Pattern 1: I HAS A var ITZ value  (declaration with initial value)
            if token['value'] == 'I HAS A' and i + 1 < len(tokens):
                var_name = tokens[i + 1]['value'] if tokens[i + 1]['type'] == 'Identifier' else None
                if var_name:
                    # Check if ITZ follows (has initial value)
                    if i + 2 < len(tokens) and tokens[i + 2]['value'] == 'ITZ':
                        # Extract the value token
                        if i + 3 < len(tokens):
                            value_token = tokens[i + 3]
                            value = value_token['value']
                            variables[var_name] = value
                        else:
                            variables[var_name] = 'NOOB'  # No value given, default to NOOB
                    else:
                        variables[var_name] = 'NOOB'  # No ITZ, default value
            
            # Pattern 2: var R value  (variable assignment)
            elif token['type'] == 'Identifier' and i + 1 < len(tokens) and tokens[i + 1]['value'] == 'R':
                var_name = token['value']
                if i + 2 < len(tokens):
                    value_token = tokens[i + 2]
                    value = value_token['value']
                    variables[var_name] = value
            
            # Pattern 3: VISIBLE output  (print statement)
            elif token['value'] == 'VISIBLE':
                # Collect what to print (simplified parsing)
                output_parts = []
                j = i + 1
                while j < len(tokens) and tokens[j]['value'] not in ('KTHXBYE', 'BUHBYE'):
                    token_type = tokens[j]['type']
                    token_value = tokens[j]['value']
                    
                    # Add literal values to output
                    if token_type in ('YARN', 'NUMBR', 'NUMBAR', 'TROOF'):
                        output_parts.append(token_value.strip('"'))
                    # Add variable values to output
                    elif token_type == 'Identifier' and token_value in variables:
                        output_parts.append(str(variables[token_value]))
                    elif token_value == 'KTHXBYE':
                        break
                    j += 1
                
                # Print output to console
                if output_parts:
                    output = ' '.join(output_parts)
                    self.output_console.insert(tk.END, output + "\n")
                    variables['IT'] = output  # IT is implicit variable that stores last output
            
            i += 1
        
        # Display all variables in symbol table
        for identifier, value in variables.items():
            self.symbol_tree.insert("", tk.END, values=(identifier, str(value)))


def main():
    """Start the LOL CODE GUI application window."""
    # Create root window
    root = tk.Tk()
    root.geometry("1200x800")
    root.minsize(800, 600)
    
    # Apply theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the GUI application
    app = LOLCODEInterpreterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()




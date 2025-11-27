"""
LOLCODE Interpreter GUI
LOLCODE interpreter with code editor,
lexer output, symbol table, and execution console.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os

# directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexer.lexer import Lexer
from parser.parser import Parser


class LOLCODEInterpreterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LOL CODE Interpreter")
        self.current_file = None
        
        # Initialize lexer and parser
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        
        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        # Create and layout all GUI components
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        # make the format scallable and responsive
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid 
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title bar 
        self.create_menu_bar(main_frame)
        
        # Code Editor
        self.create_code_editor(main_frame)
        
        # Right panels
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Lexemes Table
        self.create_lexemes_table(right_frame)
        
        # Symbol Table
        self.create_symbol_table(right_frame)
        
        # Execute Button
        self.create_execute_button(main_frame)
        
        # Output Console
        self.create_output_console(main_frame)
        
    def create_menu_bar(self, parent):
        # Create menu bar with file operations
        menu_frame = ttk.Frame(parent)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # File label
        self.file_label = ttk.Label(menu_frame, text="(None) LOL CODE Interpreter", 
                                     font=("Arial", 12, "bold"))
        self.file_label.pack(side=tk.LEFT)
        
        # Menu buttons
        button_frame = ttk.Frame(menu_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save As", command=self.save_file_as).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        
    def create_code_editor(self, parent):
        # Create code editor text area
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
        
        # Default example code for testing
        default_code = """HAI
                        I HAS A var ITZ 12
                        VISIBLE "noot noot" var
                        KTHXBYE"""
        self.code_editor.insert("1.0", default_code)
        
    def create_lexemes_table(self, parent):
        # Create lexemes table
        lexemes_frame = ttk.LabelFrame(parent, text="Lexemes Table", padding="5")
        lexemes_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        lexemes_frame.columnconfigure(0, weight=1)
        lexemes_frame.rowconfigure(0, weight=1)
        
        # Create tree view for table
        columns = ("Lexeme", "Classification")
        self.lexemes_tree = ttk.Treeview(lexemes_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.lexemes_tree.heading("Lexeme", text="Lexeme")
        self.lexemes_tree.heading("Classification", text="Classification")
        self.lexemes_tree.column("Lexeme", width=150, anchor=tk.W)
        self.lexemes_tree.column("Classification", width=200, anchor=tk.W)
        
        # Scrollbar
        lexemes_scroll = ttk.Scrollbar(lexemes_frame, orient=tk.VERTICAL, command=self.lexemes_tree.yview)
        self.lexemes_tree.configure(yscrollcommand=lexemes_scroll.set)
        
        self.lexemes_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lexemes_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_symbol_table(self, parent):
        # Create symbol table
        symbol_frame = ttk.LabelFrame(parent, text="Symbol Table", padding="5")
        symbol_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        symbol_frame.columnconfigure(0, weight=1)
        symbol_frame.rowconfigure(0, weight=1)
        
        # Create tree for table
        columns = ("Identifier", "Value")
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.symbol_tree.heading("Identifier", text="Identifier")
        self.symbol_tree.heading("Value", text="Value")
        self.symbol_tree.column("Identifier", width=150, anchor=tk.W)
        self.symbol_tree.column("Value", width=200, anchor=tk.W)
        
        # Scrollbar
        symbol_scroll = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, command=self.symbol_tree.yview)
        self.symbol_tree.configure(yscrollcommand=symbol_scroll.set)
        
        self.symbol_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        symbol_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_execute_button(self, parent):
        # Create execute button
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.execute_button = ttk.Button(
            button_frame,
            text="EXECUTE",
            # Execute code by calling the on_execute_button_click function
            command=self.on_execute_button_click,
            style="Accent.TButton"
        )
        self.execute_button.pack(fill=tk.X)
        
    def create_output_console(self, parent):
        # Create output console
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
        # Open a LOLCODE file
        filename = filedialog.askopenfilename(
            title="Open LOLCODE File",
            filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", content)
                self.current_file = filename
                self.file_label.config(text=f"{os.path.basename(filename)} - LOL CODE Interpreter")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
                
    def save_file(self):
        # Save current file
        if self.current_file:
            try:
                # Get the content of the code editor, remove the last enter char
                content = self.code_editor.get("1.0", tk.END + "-1c")
                # Save the content to the current file
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()
            
    def save_file_as(self):
        # Save file with new name
        filename = filedialog.asksaveasfilename(
            title="Save LOLCODE File",
            defaultextension=".lol",
            filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")]
        )
        if filename: # if not cancelled 
            try:
                #get all contents and writes to file 
                content = self.code_editor.get("1.0", tk.END + "-1c")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    # new file name
                self.current_file = filename
                self.file_label.config(text=f"{os.path.basename(filename)} - LOL CODE Interpreter")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                # show error message
                messagebox.showerror("Error", f"Failed to save file: {e}")
                
    def new_file(self):
        # Create a new file
        self.code_editor.delete("1.0", tk.END)
        self.current_file = None
        # reset the bar with no file name
        self.file_label.config(text="(None) LOL CODE Interpreter")
        self.clear_tables()
        
    def clear_tables(self):
        # Clear lexemes and symbol tables
        for item in self.lexemes_tree.get_children(): # get all children of the lexemes tree
            self.lexemes_tree.delete(item) # delete each child
        for item in self.symbol_tree.get_children(): # get all children of the symbol tree
            self.symbol_tree.delete(item) # delete each child
        self.output_console.config(state=tk.NORMAL)
        self.output_console.delete("1.0", tk.END)
        self.output_console.config(state=tk.DISABLED)
        
    def on_execute_button_click(self):
        # Execute the LOLCODE program
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
            
            for token in tokens:
                lexeme = token['value']
                classification = self.get_token_classification(token['type'], lexeme)
                # lexeme with type classification
                self.lexemes_tree.insert("", tk.END, values=(lexeme, classification))
            
            # Parse
            parse_tree = self.parser.parse(code)
            
            # call execute function
            self.execute_code(tokens)
            
            self.output_console.insert(tk.END, "Program executed successfully!\n")
            self.output_console.insert(tk.END, f"Parsed {len(tokens)} tokens.\n")
            
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}\n"
            self.output_console.insert(tk.END, error_msg, "error")
            messagebox.showerror("Syntax Error", str(e))
        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            self.output_console.insert(tk.END, error_msg, "error")
            messagebox.showerror("Error", str(e))
        finally:
            self.output_console.config(state=tk.DISABLED)
            # Configure error text color
            self.output_console.tag_config("error", foreground="red")
            
    def get_token_classification(self, token_type, value):
        # Map token type to classification

        # Dictionary of keyword classifications
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
        }
        
        # Dictionary of type classifications
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
            
    def execute_code(self, tokens):
        variables = {}
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Variable declaration: I HAS A var
            if token['value'] == 'I HAS A' and i + 1 < len(tokens):
                var_name = tokens[i + 1]['value'] if tokens[i + 1]['type'] == 'Identifier' else None
                if var_name:
                    # Check for ITZ
                    if i + 2 < len(tokens) and tokens[i + 2]['value'] == 'ITZ':
                        # Get the value
                        if i + 3 < len(tokens):
                            value_token = tokens[i + 3]
                            value = value_token['value']
                            variables[var_name] = value
                        else:
                            variables[var_name] = 'NOOB'
                    else:
                        variables[var_name] = 'NOOB'
            
            # variable assignment
            elif token['type'] == 'Identifier' and i + 1 < len(tokens) and tokens[i + 1]['value'] == 'R':
                var_name = token['value']
                if i + 2 < len(tokens):
                    value_token = tokens[i + 2]
                    value = value_token['value']
                    variables[var_name] = value
            
            # VISIBLE output simulation
            elif token['value'] == 'VISIBLE':
                output_parts = []
                j = i + 1
                while j < len(tokens) and tokens[j]['value'] not in ('KTHXBYE', 'BUHBYE'):
                    if tokens[j]['type'] in ('YARN', 'NUMBR', 'NUMBAR', 'TROOF'):
                        output_parts.append(tokens[j]['value'].strip('"'))
                    elif tokens[j]['type'] == 'Identifier' and tokens[j]['value'] in variables:
                        # append to output parts
                        output_parts.append(str(variables[tokens[j]['value']]))
                    elif tokens[j]['value'] == 'KTHXBYE':
                        break
                    j += 1
                
                if output_parts:
                    output = ' '.join(output_parts)
                    self.output_console.insert(tk.END, output + "\n")
                    # Set IT variable
                    variables['IT'] = output
            
            i += 1
        # iterate through tokens while iterating through var dict
        for identifier, value in variables.items():
            self.symbol_tree.insert("", tk.END, values=(identifier, str(value)))


def main():
    # Entry point for the GUI
    # window
    root = tk.Tk()
    root.geometry("1200x800")
    root.minsize(800, 600)
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = LOLCODEInterpreterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
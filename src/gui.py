import os
import sys
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Ensure `src` is on sys.path so package imports work when running this script
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from lexer.lexer import Lexer

try:
    from parser.parser import Parser
    PARSER_AVAILABLE = True
except Exception:
    Parser = None
    PARSER_AVAILABLE = False


class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCODE Explorer")
        self.geometry("1000x600")

        self.samples_dir = os.path.join(BASE_DIR, 'tests', 'samples')
        self.current_file = None
        self.tokens = None

        self._build_ui()
        self._populate_samples()

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_open = ttk.Button(toolbar, text="Open...", command=self.open_file)
        btn_open.pack(side=tk.LEFT, padx=4, pady=4)

        btn_lexer = ttk.Button(toolbar, text="Run Lexer", command=self.run_lexer)
        btn_lexer.pack(side=tk.LEFT, padx=4)

        btn_parser = ttk.Button(toolbar, text="Run Parser", command=self.run_parser)
        btn_parser.pack(side=tk.LEFT, padx=4)

        btn_save = ttk.Button(toolbar, text="Save Tokens", command=self.save_tokens)
        btn_save.pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # Main panes
        main_pane = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Left: samples list
        left_frame = ttk.Frame(main_pane, width=180)
        self.samples_list = tk.Listbox(left_frame)
        self.samples_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.samples_list.bind('<<ListboxSelect>>', self._on_sample_select)

        left_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.samples_list.yview)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.samples_list.config(yscrollcommand=left_scroll.set)

        main_pane.add(left_frame, weight=0)

        # Center: tokens output
        center_frame = ttk.Frame(main_pane)
        self.token_text = ScrolledText(center_frame, wrap=tk.NONE)
        self.token_text.pack(fill=tk.BOTH, expand=True)
        main_pane.add(center_frame, weight=1)

        # Right: parse tree
        right_frame = ttk.Frame(main_pane, width=350)
        lbl = ttk.Label(right_frame, text="Parse Tree")
        lbl.pack(anchor=tk.W)
        self.tree = ttk.Treeview(right_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        main_pane.add(right_frame, weight=1)

    def _populate_samples(self):
        self.samples_list.delete(0, tk.END)
        if not os.path.isdir(self.samples_dir):
            return
        files = sorted([f for f in os.listdir(self.samples_dir) if f.endswith('.lol')])
        for f in files:
            self.samples_list.insert(tk.END, f)

    def _on_sample_select(self, event=None):
        sel = self.samples_list.curselection()
        if not sel:
            return
        filename = self.samples_list.get(sel[0])
        self.current_file = os.path.join(self.samples_dir, filename)
        self.status_var.set(f"Selected: {filename}")

    def open_file(self):
        path = filedialog.askopenfilename(initialdir=self.samples_dir, filetypes=[('LOLCODE', '*.lol'), ('All files', '*.*')])
        if path:
            self.current_file = path
            self.status_var.set(f"Selected: {os.path.basename(path)}")

    def run_lexer(self):
        if not self.current_file:
            messagebox.showinfo('No file', 'Please open or select a .lol file first')
            return
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                code = f.read()

            lexer = Lexer()
            tokens = lexer.tokenize(code)
            self.tokens = tokens

            self.token_text.delete('1.0', tk.END)
            self.token_text.insert(tk.END, f"Tokens from {os.path.basename(self.current_file)}\n")
            self.token_text.insert(tk.END, '-'*40 + '\n')
            for t in tokens:
                self.token_text.insert(tk.END, f"{t['line']:>3}  {t['type']:<10} : {t['value']}\n")

            self.status_var.set(f"Lexer: {len(tokens)} tokens")
        except Exception as e:
            self.status_var.set('Lexer error')
            messagebox.showerror('Lexer Error', traceback.format_exc())

    def run_parser(self):
        if not self.current_file:
            messagebox.showinfo('No file', 'Please open or select a .lol file first')
            return
        if not PARSER_AVAILABLE:
            messagebox.showwarning('Parser missing', 'Parser could not be imported. See console for details.')
            return
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                code = f.read()

            parser = Parser(Lexer())
            program = parser.parse(code)

            # Populate treeview
            self.tree.delete(*self.tree.get_children())
            def insert_node(node, parent=''):
                # Display node label
                label = node.rule_name if hasattr(node, 'rule_name') else getattr(node, 'name', str(node))
                if getattr(node, 'line', None):
                    label = f"{label} (line {node.line})"
                if node.is_leaf():
                    # leaf: show token
                    tok = node.token
                    label = f"{node.rule_name}: {tok['type']} = {tok['value']}"
                nid = self.tree.insert(parent, 'end', text=label)
                for child in getattr(node, 'children', []) or []:
                    if child:
                        insert_node(child, nid)

            insert_node(program)
            self.status_var.set('Parser: parse tree built')
        except Exception:
            self.status_var.set('Parser error')
            messagebox.showerror('Parser Error', traceback.format_exc())

    def save_tokens(self):
        if not self.tokens:
            messagebox.showinfo('No tokens', 'Run lexer first to produce tokens')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for t in self.tokens:
                    f.write(f"{t['line']:>3} {t['type']:<10} : {t['value']}\n")
            self.status_var.set(f"Saved tokens to {os.path.basename(path)}")
        except Exception:
            messagebox.showerror('Save Error', traceback.format_exc())


def main():
    app = LOLGui()
    app.mainloop()


if __name__ == '__main__':
    main()

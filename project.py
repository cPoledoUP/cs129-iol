#########################################################################
# Authors:                                                              #
#   Galang, Kent Michael                                                #
#   Masayon, Christian Ace                                              #
#   Poledo, Clent Japhet                                                #
#########################################################################
# Program description:                                                  #
#   A simple compiler and IDE for the IOL programming language          #
#########################################################################

import tkinter as tk
import re
from tkinter import filedialog, ttk, simpledialog
        

class LexicalAnalyzer:
    """
    A class that converts a source file into tokens for the IOL language.

    Token list:
        [KEYWORDS]
        IOL, LOI, INT, STR, IS, INTO, IS, BEG, PRINT, ADD, SUB, MULT, DIV, MOD, NEWLN
        [OTHER TOKENS]
        ERR_LEX, INT_LIT, IDENT

    INT_LIT => digit {digit}
    digit => 0 | 1 | ... | 9

    IDENT => letter {(letter | digit)}
    letter => a | b | c | ... | z | A | B | ... | Z
    digit => 0 | 1 | ... | 9

    Attributes
    ----------
    keywords : tuple
        A list of keywords used by the programming language
    tokens : list
        A list of tokens from last tokenize() call
    errors : list
        A list of errors from last tokenize() call
    var_list : list
        A list of variables from last tokenize() call

    Methods
    ----------
    tokenize(string)
        Converts a given string into a series of tokens and returns whether or not errors were encountered
    word_to_token(word)
        Converts a word into a token
    get_tokens()
        Returns the list of tokens from last tokenize()
    get_var_list()
        Returns the list of variables from last tokenize()
    get_errors()
        Returns the list of errors from last tokenize()
    """
    def __init__(self) -> None:
        self.keywords = (
            "IOL",
            "LOI",
            "INT",
            "STR",
            "IS",
            "INTO",
            "IS",
            "BEG",
            "PRINT",
            "ADD",
            "SUB",
            "MULT",
            "DIV",
            "MOD",
            "NEWLN",
        )
        self.tokens = list()
        self.errors = list()

    """
    Converts a given string into a series of tokens and returns whether or not errors were encountered

    Parameters
    ----------
    string : str
        An input string to tokenize

    Returns
    -------
    bool
        True if no errors encountered, False otherwise
    """
    def tokenize(self, string: str, sym_tbl: dict[str, list[str | int]]) -> bool:

        self.tokens.clear()
        self.errors.clear()

        curr_line = 0
        for line in string.splitlines():
            curr_line += 1
            for word in line.split():
                token = self.word_to_token(word)
                self.tokens.append(token)
                if token[0] == "ERR_LEX":
                    self.errors.append((token[1], curr_line, "unknown word"))
                elif token[0] == "IDENT":
                    last_token = self.tokens[len(self.tokens) - 2]

                    if (last_token[0] == "STR" or last_token[0] == "INT"):
                        if token[1] in sym_tbl:
                            self.errors.append(
                                (token[1], curr_line, "duplicate variable definition")
                            )
                        elif last_token[0] == "STR":
                            sym_tbl[token[1]] = [last_token[0], ""]
                        else:
                            sym_tbl[token[1]] = [last_token[0], 0]
                    else:
                        if token[1] not in sym_tbl:
                            self.errors.append(
                                (token[1], curr_line, "undefined variable")
                            )

        if len(self.errors) == 0:
            return True
        else:
            return False

    """
    Converts a word into a token

    Parameters
    ---------
    word : str
        The word to convert into token

    Returns
    -------
    tuple
        A token in the format (TOKEN_NAME, VALUE)
    """
    def word_to_token(self, word: str) -> tuple:

        # check if word is keyword
        if word in self.keywords:
            return (word, word)
        # check if word is an int_lit or ident or err_lex
        else:
            # Logic:
            # '' --numeric--> 'INT_LIT'
            # '' --alphabet--> 'IDENT'
            # '' --neither--> 'ERR_LEX'
            # 'INT_LIT' --numeric--> 'INT_LIT'
            # 'INT_LIT' --alphabet--> 'ERR_LEX'
            # 'INT_LIT' --neither--> 'ERR_LEX'
            # 'IDENT' --numeric--> 'IDENT'
            # 'IDENT' --alphabet--> 'IDENT'
            # 'IDENT' --neither--> 'ERR_LEX'
            # 'ERR_LEX' --whatever--> 'ERR_LEX'
            possible_token = ""
            for letter in word:
                if possible_token == "ERR_LEX":
                    break

                if letter.isnumeric():
                    if possible_token == "" or possible_token == "INT_LIT":
                        possible_token = "INT_LIT"
                    elif possible_token == "IDENT":
                        possible_token = "IDENT"
                elif letter.isalpha():
                    if possible_token == "" or possible_token == "IDENT":
                        possible_token = "IDENT"
                    elif possible_token == "INT_LIT":
                        possible_token = "ERR_LEX"
                else:
                    possible_token = "ERR_LEX"

            if possible_token == "INT_LIT":
                word = int(word)
            return (possible_token, word)

    """
    Returns the list of tokens from last tokenize()

    Returns
    -------
    list
        A list of tokens [(token_name, value), ...]
    """
    def get_tokens(self) -> list:

        return self.tokens.copy()

    """
    Returns the list of errors from last tokenize()

    Returns
    -------
    list
        A list of errors [(error_word, line_number, error_definition), ...]
    """
    def get_errors(self) -> list:

        return self.errors

class SyntaxAnalyzer:
    """A class that analyzes the syntax of the generated tokens.
    This also implements a static semantic analysis.

    Attributes:
        prod (list[list[str]]): production rule for the language
        ptbl (dict[str, list[str, int]]): parse table for the language

    Methods:
        check_input(path): checks a .tkn file for proper grammar
    """
    def __init__(self) -> None:
        self.prod = [
            ["s", "IOL stmts LOI"],
            ["stmts", "stmt stmts"],
            ["stmts", "e"],
            ["stmt", "var"],
            ["stmt", "asn"],
            ["stmt", "expr"],
            ["stmt", "PRINT expr"],
            ["stmt", "NEWLN"],
            ["var", "INT IDENT varend"],
            ["var", "STR IDENT varend"],
            ["varend", "IS INT_LIT"],
            ["varend", "e"],
            ["asn", "INTO IDENT IS expr"],
            ["asn", "BEG IDENT"],
            ["expr", "ADD expr expr"],
            ["expr", "SUB expr expr"],
            ["expr", "MULT expr expr"],
            ["expr", "DIV expr expr"],
            ["expr", "MOD expr expr"],
            ["expr", "IDENT"],
            ["expr", "INT_LIT"],
        ]
        self.ptbl = {
            "terminals": [
                "IOL",
                "INT",
                "STR",
                "INTO",
                "BEG",
                "PRINT",
                "NEWLN",
                "LOI",
                "IS",
                "ADD",
                "SUB",
                "MULT",
                "DIV",
                "MOD",
                "IDENT",
                "INT_LIT",
            ],
            "s": [1, "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            "stmts": ["", 2, 2, 2, 2, 2, 2, 3, "", 2, 2, 2, 2, 2, 2, 2],
            "stmt": ["", 4, 4, 5, 5, 7, 8, "", "", 6, 6, 6, 6, 6, 6, 6],
            "var": ["", 9, 10, "", "", "", "", "", "", "", "", "", "", "", "", ""],
            "varend": ["", 12, 12, 12, 12, 12, 12, 12, 11, 12, 12, 12, 12, 12, 12, 12],
            "asn": ["", "", "", 13, 14, "", "", "", "", "", "", "", "", "", "", ""],
            "expr": ["", "", "", "", "", "", "", "", "", 15, 16, 17, 18, 19, 20, 21],
        }

    """Returns the process in trying to check if an input string is a valid word according to the grammar

    Args:
        input_path (str): .tkn file path
        sym_tbl (dict[str, list[str | int]]): symbol table
        tokens (list[tuple[str, str]]): token stream

    Returns:
        list[tuple[int, str] | None]: error details [(line_number, error_details), ...]
    """
    def check_input(self, input_path: str, sym_tbl: dict[str, list[str | int]], tokens: list[tuple[str, str]]) -> list[tuple[int, str] | None]:
        
        with open(input_path, "r") as file:
            input = file.readlines()
        prod = self.prod
        ptbl = self.ptbl
        list_errors = list()

        # add the first nonterminal and $ to the stack
        stack = [prod[0][0], "$"]
        input_buffer = input.pop(0).split()
        line_num = 1
        # add $ to the end of the input buffer
        input_buffer.append("$")

        # vars related to error
        error_recovering = False
        loi_end_found = False

        # vars related to type checking
        tokens.append(("$", "$"))
        declared_vars = list()
        statement = list()
        semantic_case = None
        last_ident_token = None

        while len(input) != 0 or len(input_buffer) != 0:
            if len(input_buffer) == 1 and len(input) > 0:
                new_line = input.pop(0).split()
                line_num += 1
                # check if popped line is empty
                while len(new_line) == 0 and len(input) > 0:
                    new_line = input.pop(0).split()
                    line_num += 1
                input_buffer = new_line + ["$"]

            # if input buffer still only has $, stop
            if len(input_buffer) == 1:
                break

            if error_recovering:
                if loi_end_found:
                    stack = ["$"]
                else:
                    stack = ["stmt", "stmts", "LOI", "$"]
                error_recovering = False
                continue
            
            curr_stack = stack.pop(0)
            curr_input = input_buffer[0]

            # for displaying semantic analysis errors
            if curr_stack == "stmt":
                statement.clear()
                semantic_case = None
                last_ident_token = None
            if curr_input == "LOI" and not loi_end_found:
                loi_end_found = True
                if curr_stack == "stmt":
                    curr_stack = "LOI"
                    stack = ["$"]

            if curr_input == curr_stack:
                # for matching case, just remove the terminal in both columns
                input_buffer.pop(0)
                popped_token = tokens.pop(0)

                # for each correct case, check for possible type errors
                match popped_token[0]:
                    case "INT" | "STR":
                        semantic_case = "DECLARE"
                        statement.append(popped_token[1])
                    case "INTO":
                        semantic_case = "INTO"
                        statement.append(popped_token[1])
                    case "ADD" | "SUB" | "MULT" | "DIV" | "MOD":
                        statement.append(popped_token[1])
                        if semantic_case == "IS":
                            if last_ident_token[1] in declared_vars and sym_tbl[last_ident_token[1]][0] != "INT":
                                current_error = f"Type error '{" ".join(statement)}'. '{last_ident_token[1]}' is of type STR"
                                list_errors.append((line_num, current_error))
                        semantic_case = "MATH"
                    case "IS":
                        semantic_case = "IS"
                        statement.append(popped_token[1])
                    case "IDENT":
                        statement.append(popped_token[1])
                        if semantic_case == "DECLARE":
                            if popped_token[1] in declared_vars:
                                current_error = f"Duplicate variable declaration '{popped_token[1]}' in '{" ".join(statement)}'"
                                list_errors.append((line_num, current_error)) 
                            else:
                                declared_vars.append(popped_token[1])
                        elif popped_token[1] not in declared_vars:
                            current_error = f"Undefined variable '{popped_token[1]}' in '{" ".join(statement)}'"
                            list_errors.append((line_num, current_error))
                        elif semantic_case == "IS":
                            if sym_tbl[last_ident_token[1]][0] != sym_tbl[popped_token[1]][0]:
                                current_error = f"Type error '{" ".join(statement)}'. '{last_ident_token[1]}' is of type {sym_tbl[last_ident_token[1]][0]}"
                                list_errors.append((line_num, current_error))
                        elif semantic_case == "MATH":
                            if sym_tbl[popped_token[1]][0] != "INT":
                                current_error = f"Type error '{" ".join(statement)}'. '{popped_token[1]}' is of type {sym_tbl[popped_token[1]][0]}"
                                list_errors.append((line_num, current_error))
                        last_ident_token = popped_token
                    case "INT_LIT":
                        statement.append(popped_token[1])
                        if semantic_case == "IS":
                            if last_ident_token[1] in declared_vars and sym_tbl[last_ident_token[1]][0] != "INT":
                                current_error = f"Type error '{" ".join(statement)}'. '{last_ident_token[1]}' is of type STR"
                                list_errors.append((line_num, current_error))
                    case _:
                        statement.append(popped_token[1])
                    
            else:
                if curr_stack not in ptbl:
                    # raise Exception(
                    #     f"{line_num} Error: '{curr_stack}' is not a nonterminal in parse table"
                    # )
                    if curr_stack == "$":
                        current_error = f"({tokens.pop(0)[1]}) Expected no tokens after 'LOI' but found '{input_buffer.pop(0)}'"
                        loi_end_found = True
                    else:
                        current_error = f"({tokens.pop(0)[1]}) Expected '{curr_stack}' token, got '{input_buffer.pop(0)}'"
                    
                    list_errors.append((line_num, current_error))
                    error_recovering = True
                    continue
                if curr_input not in ptbl["terminals"]:
                    # raise Exception(
                    #     f"{line_num} Error: '{curr_input}' is not a terminal in parse table"
                    # )
                    if curr_input == "$":
                        current_error = f"({tokens.pop(0)[1]}) Expected a 'LOI' at the end of file"
                        input_buffer.pop(0)
                    else:
                        possible_tokens = [
                            ptbl["terminals"][i]
                            for i in range(len(ptbl["terminals"]))
                            if ptbl[curr_stack][i] != ""
                        ]
                        current_error = f"({tokens.pop(0)[1]}) Expected '{"','".join(possible_tokens)}' token, got '{input_buffer.pop(0)}'"
                    
                    list_errors.append((line_num, current_error))
                    error_recovering = True
                    continue
                # query the production to use from the parse table
                dest_line_num = ptbl[curr_stack][ptbl["terminals"].index(curr_input)]
                if dest_line_num == "":
                    # raise Exception(f"{line_num} Error: Resulted in a crash")
                    possible_tokens = [
                        ptbl["terminals"][i]
                        for i in range(len(ptbl["terminals"]))
                        if ptbl[curr_stack][i] != ""
                    ]
                    current_error = f"({tokens.pop(0)[1]}) Expected '{"','".join(possible_tokens)}' token, got '{input_buffer.pop(0)}'"
                    
                    list_errors.append((line_num, current_error))
                    error_recovering = True
                    continue
                prod_to_replace = prod[dest_line_num - 1]
                # if production is not epsilon, add those to stack
                if prod_to_replace[1] != "e":
                    stack = prod_to_replace[1].split() + stack
            # save the current step
            error_recovering = False
        
        if not loi_end_found:
            current_error = f"Expected a 'LOI' at the end of file"
            list_errors.append((line_num, current_error))
        return list_errors

    
class App:
    """
    A class for the UI of the app
    """
    def __init__(self, master):
        self.master = master
        self.master.title("PyDE")
        self.master.geometry("1400x600")

        self.file_path = None
        self.sym_tbl = dict()
        self.lex = LexicalAnalyzer()

        # Create the main frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the input frame (top left)
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(side="left", fill=tk.BOTH, expand=True)

        # Create the Table of Variables frame (right side)
        self.variables_frame = tk.Frame(self.main_frame)
        self.variables_frame.pack(side="right", fill=tk.BOTH, expand=True)

        # Create a frame for input_text and line_numbers
        self.editor_frame = tk.Frame(self.input_frame)
        self.editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Label for Code Editor
        self.editor_label = tk.Label(
            self.editor_frame,
            text="Code Editor",
            anchor="w",
            font=("Arial", 10, "bold"),
        )
        self.editor_label.pack(side="top", fill="x")

        # Create the scrollbar for input_text
        self.input_scrollbar = tk.Scrollbar(self.editor_frame, command=self.on_scroll)
        # self.input_scrollbar = tk.Scrollbar(self.editor_frame)
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.line_numbers = tk.Text(
            self.editor_frame, width=4, padx=5, highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.insert("1.0", "1")
        self.line_numbers.config(
            yscrollcommand=self.on_line_num_scroll, state=tk.DISABLED
        )

        self.input_text = tk.Text(self.editor_frame, undo=True)
        self.input_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.input_text.config(yscrollcommand=self.on_text_scroll)

        self.input_text.bind("<KeyPress>", self.on_key_press)
        # self.input_text.bind('<KeyRelease>', self.on_key_release)
        self.input_text.focus_set()
        # self.input_text.bind('<Key>', self.on_text_configure)
        # self.input_text.bind('<MouseWheel>', self.on_mousewheel)

        self.update_line_numbers()

        # Label for Console
        self.console_label = tk.Label(
            self.input_frame, text="Console", anchor="w", font=("Arial", 10, "bold")
        )
        self.console_label.pack(side="top", fill="x")

        self.output_text = tk.Text(self.input_frame, height=15, state=tk.DISABLED)
        self.output_text.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True
        )  # Change side to 'left'

        # Create the scrollbar for output_text (console) on the right
        self.console_scrollbar = tk.Scrollbar(
            self.input_frame, command=self.output_text.yview
        )
        self.console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text.config(yscrollcommand=self.console_scrollbar.set)

        # Label for Table of Variables
        self.variables_label = tk.Label(
            self.variables_frame,
            text="Table of Variables",
            anchor="w",
            font=("Arial", 10, "bold"),
        )
        self.variables_label.pack(side="top", fill="x")

        # self.variables_text = tk.Text(self.variables_frame, state=tk.DISABLED)
        default_headers = ["Variable", "Type"]
        self.variables_text = ttk.Treeview(
            self.variables_frame,
            columns=default_headers,
            show="headings",
            selectmode="browse",
        )
        self.variables_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Insert the default column headers
        for header in default_headers:
            self.variables_text.heading(header, text=header)
            self.variables_text.column(header, minwidth=50, stretch=True, anchor="center")
        self.variables_text.pack(side="left", fill=tk.BOTH, expand=True)

        self.variables_scrollbar = tk.Scrollbar(
            self.variables_frame, command=self.variables_text.yview
        )
        self.variables_scrollbar.pack(side="right", fill=tk.Y)

        self.variables_text.config(yscrollcommand=self.variables_scrollbar.set)

        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        # For file menu
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New File (Ctrl+N)", command=self.new_file)
        self.file_menu.add_command(label="Open File (Ctrl+O)", command=self.open_file)
        self.file_menu.add_command(label="Save File (Ctrl+S)", command=self.save_file)
        self.file_menu.add_command(
            label="Save File As (Ctrl+Shift+S)", command=self.save_file_as
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit (Ctrl+Q)", command=self.master.quit)

        # For compile code, show tokenized code, and execute code buttons
        self.menu.add_command(label="(F1) Compile Code", command=self.compile_code)
        self.menu.add_command(
            label="(F2) Show Tokenized Code",
            command=self.show_tokenized_code,
            state=tk.DISABLED,
        )
        self.menu.add_command(
            label="(F3) Execute Code", command=self.execute_code, state=tk.DISABLED
        )

        # Configure row and column weights for resizing
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.variables_frame.grid_rowconfigure(1, weight=1)
        self.variables_frame.grid_columnconfigure(1, weight=1)

    """
    Called when a key is pressed on the code editor
    """
    def on_key_press(self, event):

        # v is for ctrl+v (paste)
        if (
            event.keysym == "Return"
            or event.keysym == "BackSpace"
            or event.keysym == "v"
            or event.keysym == "V"
        ):
            self.update_line_numbers()

    """
    Called when a key is released on the code editor
    """
    def on_key_release(self, event):

        # v is for ctrl+v (paste)
        if (
            event.keysym == "Return"
            or event.keysym == "BackSpace"
            or event.keysym == "v"
            or event.keysym == "V"
        ):
            self.update_line_numbers()
        elif event.keysym == "F1":
            self.menu.invoke(2)
        elif event.keysym == "F2":
            self.menu.invoke(3)
        elif event.keysym == "F3":
            self.menu.invoke(4)
        elif event.state == 4:  # keypress with Ctrl
            if event.keysym == "n" or event.keysym == "N":
                self.file_menu.invoke(0)
            elif event.keysym == "o" or event.keysym == "O":
                self.file_menu.invoke(1)
            elif event.keysym == "s" or event.keysym == "S":
                self.file_menu.invoke(2)
            elif event.keysym == "q" or event.keysym == "Q":
                self.file_menu.invoke(5)
        elif event.state == 5:  # keypress with Ctrl and Shift
            if event.keysym == "s" or event.keysym == "S":
                self.file_menu.invoke(3)

    """
    Update the line numbers in the left side of the UI
    """
    def update_line_numbers(self):

        line_count = int(self.input_text.index("end-1c").split(".")[0])
        # line_numbers_text = '\n'.join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.config(state=tk.NORMAL)
        current_line_numbers = self.line_numbers.get("1.0", "end-1c").split("\n")
        last_num = len(current_line_numbers)

        diff = line_count - last_num
        while diff != 0:
            if diff > 0:
                last_num += 1
                self.line_numbers.insert(str(last_num) + ".0", "\n" + str(last_num))
            else:
                last_num -= 1
                self.line_numbers.delete(
                    str(last_num + 1) + ".0", str(last_num + 2) + ".0"
                )
            diff = line_count - last_num

        # self.line_numbers.delete("1.0", tk.END)
        # self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.yview_moveto(self.input_text.yview()[0])
        self.line_numbers.config(state=tk.DISABLED)

    """
    Called when a the code editor scrollbar is dragged
    """
    def on_scroll(self, *args):

        self.input_text.yview_moveto(args[1])
        self.line_numbers.yview_moveto(args[1])

    """
    Called when the main input text is scrolled
    """
    def on_text_scroll(self, *args):

        self.input_scrollbar.set(args[0], args[1])
        self.line_numbers.yview_moveto(args[0])

    """
    Called when the line number text is scrolled
    """
    def on_line_num_scroll(self, *args):

        self.input_scrollbar.set(args[0], args[1])
        self.line_numbers.yview_moveto(self.input_text.yview()[0])
        # self.input_text.yview_moveto(args[0])

    # def on_mousewheel(self, event):
    #     self.line_numbers.yview_moveto(self.input_text.yview()[0])

    """
    Called when user wants to create a new file
    """
    def new_file(self):

        self.file_path = None
        self.input_text.delete("1.0", tk.END)
        self.update_line_numbers()
        # disable show tokenized code and execute code button
        self.menu.entryconfig(3, state=tk.DISABLED)
        self.menu.entryconfig(4, state=tk.DISABLED)
        for child in self.variables_text.get_children():
            self.variables_text.delete(child)

    """
    Called when user wants to open a file
    """
    def open_file(self):

        file_path = filedialog.askopenfilename(filetypes=[("IOL Files", "*.iol")])
        if file_path:
            self.file_path = file_path
            with open(file_path, "r") as file:
                content = file.read()
                # if content.endswith('\n'):
                #     content = content[:-1]
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)
            self.update_line_numbers()
            # disable show tokenized code and execute code button
            self.menu.entryconfig(3, state=tk.DISABLED)
            self.menu.entryconfig(4, state=tk.DISABLED)
            for child in self.variables_text.get_children():
                self.variables_text.delete(child)

            self.output_text.configure(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Opened {self.file_path}\n\n")
            self.output_text.configure(state=tk.DISABLED)
            self.output_text.yview_moveto(1)

    """
    Called when user wants to save an opened file
    """
    def save_file(self):

        if self.file_path:
            if not self.file_path.endswith(".iol"):
                self.file_path += ".iol"
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", "end-1c"))
            # disable show tokenized code and execute code button
            self.menu.entryconfig(3, state=tk.DISABLED)
            self.menu.entryconfig(4, state=tk.DISABLED)
            for child in self.variables_text.get_children():
                self.variables_text.delete(child)

            self.output_text.configure(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Saved to {self.file_path}\n\n")
            self.output_text.configure(state=tk.DISABLED)
            self.output_text.yview_moveto(1)
        else:
            self.save_file_as()

    """
    Called when user wants to save a file as different file
    """
    def save_file_as(self):

        file_path = filedialog.asksaveasfilename(
            defaultextension=".iol", filetypes=[("IOL Files", "*.iol")]
        )
        if file_path:
            if not file_path.endswith(".iol"):
                file_path += ".iol"
            self.file_path = file_path
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", "end-1c"))
            # disable show tokenized code and execute code button
            self.menu.entryconfig(3, state=tk.DISABLED)
            self.menu.entryconfig(4, state=tk.DISABLED)
            for child in self.variables_text.get_children():
                self.variables_text.delete(child)

            self.output_text.configure(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Saved to {self.file_path}\n\n")
            self.output_text.configure(state=tk.DISABLED)
            self.output_text.yview_moveto(1)

    """
    Called when user wants to compile an IOL file
    """
    def compile_code(self):

        self.save_file()
        if self.file_path == None:
            return
        
        self.sym_tbl.clear()

        ########## Lexical Analysis ##########

        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"Compiling {self.file_path}\n\n")
        if self.lex.tokenize(self.input_text.get("1.0", tk.END), self.sym_tbl):
            self.output_text.insert(
                tk.END, "Lexical analysis completed without errors.\n"
            )
            self.output_text.yview_moveto(1)
        else:
            for error in self.lex.get_errors():
                self.output_text.insert(
                    tk.END,
                    f"{error[2].capitalize()} {error[0]} found in line {error[1]}.\n",
                )
                self.output_text.yview_moveto(1)
            self.output_text.insert(tk.END, "Lexical analysis completed with error(s).\n")
            self.output_text.yview_moveto(1)

        # making .tkn file
        current_token = 0
        text = self.input_text.get("1.0", tk.END)
        text = re.split("(\\s+)", text)

        for i in range(len(text)):
            if text[i].isspace() or text[i] == "":
                continue
            else:
                text[i] = self.lex.get_tokens()[current_token][0]
                current_token += 1

        tkn_file_path = self.file_path[:-3] + "tkn"
        with open(tkn_file_path, "w") as file:
            file.write("".join(text))
        self.output_text.insert(
            tk.END, f"\nTokenized version of the source code saved in {tkn_file_path}\n\n"
        )
        self.output_text.configure(state=tk.DISABLED)
        self.output_text.yview_moveto(1)

        # display proper outputs and enable show tokenized code button
        # self.variables_text.configure(state=tk.NORMAL)
        # self.variables_text.delete("1.0", tk.END)
        for child in self.variables_text.get_children():
            self.variables_text.delete(child)
        for var in self.sym_tbl:
            self.variables_text.insert("", "end", values=[var, self.sym_tbl[var][0]])
        # self.variables_text.configure(state=tk.DISABLED)
        self.menu.entryconfig(3, state=tk.NORMAL)

        ########## Syntax Analysis ##########
        syntax_errors = SyntaxAnalyzer().check_input(tkn_file_path, self.sym_tbl, self.lex.get_tokens())

        self.output_text.configure(state=tk.NORMAL)
        if syntax_errors:
            for line_num, error_message in syntax_errors:
                self.output_text.insert(
                    tk.END, f"Error at line {line_num}: {error_message}\n"
                )         
            self.output_text.insert(tk.END, "Syntax analysis completed with error(s).\n")
            self.output_text.yview_moveto(1)
            # when there is error, disable the execute code button
            self.menu.entryconfig(4, state=tk.DISABLED)
        if not syntax_errors:
            self.output_text.insert(tk.END, "Syntax analysis completed without errors.\n")
            self.output_text.yview_moveto(1)
            # when there is no error, enable the execute code button
            self.menu.entryconfig(4, state=tk.NORMAL)
        self.output_text.configure(state=tk.DISABLED)
        

    """
    Called when user wants to show a tokenized IOL file (tkn file)
    """
    def show_tokenized_code(self):

        tkn_file_path = self.file_path[:-3] + "tkn"
        top = tk.Toplevel(self.master)
        label = tk.Label(top, text="Tokenized Code", font=("Arial", 10, "bold"))
        label.pack(fill="x")
        frame = tk.Frame(top)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill="y")
        text = tk.Text(frame, yscrollcommand=scroll.set)
        text.pack(expand=True, fill="both")
        scroll.configure(command=text.yview)

        with open(tkn_file_path, "r") as file:
            text_with_lines = file.readlines()
            for i in range(len(text_with_lines)):
                text.insert(
                    f"{i + 1}.0", f"{'{0: <3}'.format(i + 1)} | {text_with_lines[i]}"
                )

        text.configure(state=tk.DISABLED)

    """
    Called when user wants to execute a compiled IOL file
    """
    def execute_code(self):
        # make the output text writable
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\nIOL Execution:\n\n")
        self.output_text.yview_moveto(1)
        token_stream = self.lex.get_tokens()
        # add a shallow copy of dict entries
        symbol_table = self.sym_tbl.copy()
        for key in symbol_table:
            symbol_table[key] = symbol_table[key].copy()

        # traverse the token stream linearly and do tasks
        current_task = None
        evaluating_expr = False
        last_expr_value = None
        expr_stack = list()
        for i, token in enumerate(token_stream):
            # tokens associated with an action:
            # "BEG","PRINT","NEWLN","IS","ADD","SUB","MULT","DIV","MOD"
            if token[0] in ["BEG","PRINT","NEWLN","IS"]:
                current_task = (token[0], i)
            
            # evaluate an expression
            if evaluating_expr:
                match token[0]:
                    case "IDENT":
                        expr_stack.append(symbol_table[token[1]][1])    # push the value of the variable to the stack
                    case "INT_LIT":
                        expr_stack.append(token[1]) # push the int lit value to the stack
                    case "ADD" | "SUB" | "MULT" | "DIV" | "MOD":
                        expr_stack.append(token[0])  # push the operator to the stack
                    
                # evaluate the operations
                # loop as long as there is a solvable operator
                while len(expr_stack) >= 3 and type(expr_stack[-1]) != str and type(expr_stack[-2]) != str:
                    num2 = expr_stack.pop()
                    num1 = expr_stack.pop()
                    op = expr_stack.pop()
                    match op:
                        case "ADD":
                            expr_stack.append(num1 + num2)
                        case "SUB":
                            expr_stack.append(num1 - num2)
                        case "MULT":
                            expr_stack.append(num1 * num2)
                        case "DIV":
                            if num2 == 0:
                                self.output_text.insert(tk.END, f"\n\nProgram terminated with error: Division by zero.\n\n")
                                self.output_text.yview_moveto(1)
                                self.output_text.configure(state=tk.DISABLED)  
                                return
                            expr_stack.append(num1 // num2) # using // operator removes decimal points
                        case "MOD":
                            expr_stack.append(num1 % num2)
                    # print(num1, op, num2, "=", expr_stack[-1])
                
                # if we get a single value in the expr_stack, expression has finished evaluating
                if len(expr_stack) == 1 and expr_stack[0] not in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
                    last_expr_value = expr_stack.pop()
                    evaluating_expr = False

            # do task based on current task
            if current_task != None:
                match current_task[0]:
                    case "BEG": # input operation
                        if token[0] != "IDENT":
                            continue
                        else:
                            root.update()   # simpledialog goes behind root without this for some reason
                            user_input = simpledialog.askstring("Input", f"Input for {token[1]}")
                            self.output_text.insert(tk.END, f"Input for {token[1]}: {user_input}\n")
                            self.output_text.yview_moveto(1)
                            # store the new value
                            if user_input == None:
                                self.output_text.insert(tk.END, f"\n\nProgram terminated with error: User cancelled the input operation.\n\n")
                                self.output_text.yview_moveto(1)
                                self.output_text.configure(state=tk.DISABLED)  
                                return
                            elif symbol_table[token[1]][0] == "INT":
                                # type mismatch
                                if not user_input.isdigit():
                                    self.output_text.insert(tk.END, f"\n\nProgram terminated with error: {token[1]} expected an INT, got STR instead.\n\n")
                                    self.output_text.yview_moveto(1)
                                    self.output_text.configure(state=tk.DISABLED)
                                    return
                                else:
                                    symbol_table[token[1]][1] = int(user_input)
                            else:
                                symbol_table[token[1]][1] = user_input
                            current_task = None
                    case "PRINT":   # output operation
                        if last_expr_value == None:
                            # evaluate the expression first
                            evaluating_expr = True
                        else:
                            # print the value of the expression
                            self.output_text.insert(tk.END, f"{last_expr_value}")
                            self.output_text.yview_moveto(1)
                            current_task = None
                            last_expr_value = None
                    case "NEWLN":   # appends a new line
                        self.output_text.insert(tk.END, "\n")
                        self.output_text.yview_moveto(1)
                        current_task = None
                    case "IS":  # assignment operation
                        if last_expr_value == None:
                            # evaluate the expression first
                            evaluating_expr = True
                        else:
                            # store the evaluated expression to the variable
                            symbol_table[token_stream[current_task[1] - 1][1]][1] = last_expr_value
                            current_task = None
                            last_expr_value = None
        
        # finally, disable the console from user input
        self.output_text.insert(tk.END, f"\n\nProgram terminated successfully...\n\n")
        self.output_text.yview_moveto(1)
        self.output_text.configure(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    editor = App(root)
    root.bind_all("<KeyRelease>", editor.on_key_release)
    root.mainloop()

import tkinter as tk
import re
from tkinter import filedialog
from backend import *

class App:
    """
    A class for the UI of the app
    """

    def __init__(self, master):
        self.master = master
        self.master.title("PyDE")
        self.master.geometry("1400x600")

        self.file_path = None
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
        self.editor_label = tk.Label(self.editor_frame, text="Code Editor", anchor="w", font=("Arial", 10, "bold"))
        self.editor_label.pack(side="top", fill="x")

        # Create the scrollbar for input_text
        self.input_scrollbar = tk.Scrollbar(self.editor_frame, command=self.on_scroll)
        # self.input_scrollbar = tk.Scrollbar(self.editor_frame)
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=5, highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.insert("1.0", "1")
        self.line_numbers.config(yscrollcommand=self.on_line_num_scroll, state=tk.DISABLED)

        self.input_text = tk.Text(self.editor_frame, undo=True)
        self.input_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.input_text.config(yscrollcommand=self.on_text_scroll)

        self.input_text.bind('<KeyPress>', self.on_key_press)
        self.input_text.bind('<KeyRelease>', self.on_key_release)
        # self.input_text.bind('<Key>', self.on_text_configure)
        # self.input_text.bind('<MouseWheel>', self.on_mousewheel)

        self.update_line_numbers()

       # Label for Console
        self.console_label = tk.Label(self.input_frame, text="Console", anchor="w", font=("Arial", 10, "bold"))
        self.console_label.pack(side="top", fill="x")

        self.output_text = tk.Text(self.input_frame, height=15, state=tk.DISABLED)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Change side to 'left'

        # Create the scrollbar for output_text (console) on the right
        self.console_scrollbar = tk.Scrollbar(self.input_frame, command=self.output_text.yview)
        self.console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text.config(yscrollcommand=self.console_scrollbar.set)

        # Label for Table of Variables
        self.variables_label = tk.Label(self.variables_frame, text="Table of Variables", anchor="w",
                                        font=("Arial", 10, "bold"))
        self.variables_label.pack(side="top", fill="x")

        self.variables_text = tk.Text(self.variables_frame, state=tk.DISABLED)
        self.variables_text.pack(side="left", fill=tk.BOTH, expand=True)
        
        self.variables_scrollbar = tk.Scrollbar(self.variables_frame, command=self.variables_text.yview)
        self.variables_scrollbar.pack(side="right", fill=tk.Y)
        
        self.variables_text.config(yscrollcommand=self.variables_scrollbar.set)

        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        # For file menu
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New File", command=self.new_file)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Save File", command=self.save_file)
        self.file_menu.add_command(label="Save File As", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.quit)

        # For compile code, show tokenized code, and execute code buttons
        self.menu.add_command(label="Compile Code", command=self.compile_code)
        self.menu.add_command(label="Show Tokenized Code", command=self.show_tokenized_code, state=tk.DISABLED)
        self.menu.add_command(label="Execute Code", command=self.execute_code, state=tk.DISABLED)

        # Configure row and column weights for resizing
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.variables_frame.grid_rowconfigure(1, weight=1)
        self.variables_frame.grid_columnconfigure(1, weight=1)

    def on_key_press(self, event):
        """
        Called when a key is pressed on the code editor
        """

        # v is for ctrl+v (paste)
        if event.keysym == 'Return' or event.keysym == 'BackSpace' or event.keysym == 'v' or event.keysym == 'V':
            self.update_line_numbers()

    def on_key_release(self, event):
        """
        Called when a key is released on the code editor
        """

        # v is for ctrl+v (paste)
        if event.keysym == 'Return' or event.keysym == 'BackSpace' or event.keysym == 'v' or event.keysym == 'V':
            self.update_line_numbers()

    def update_line_numbers(self):
        """
        Update the line numbers in the left side of the UI
        """

        line_count = int(self.input_text.index("end-1c").split('.')[0])
        # line_numbers_text = '\n'.join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.config(state=tk.NORMAL)
        current_line_numbers = self.line_numbers.get("1.0", "end-1c").split('\n')
        last_num = len(current_line_numbers)

        diff = line_count - last_num
        while diff != 0:
            if diff > 0:
                last_num += 1
                self.line_numbers.insert(str(last_num) + '.0', "\n" + str(last_num))
            else:
                last_num -= 1
                self.line_numbers.delete(str(last_num + 1)+'.0', str(last_num + 2) + '.0')
            diff = line_count - last_num

        # self.line_numbers.delete("1.0", tk.END)
        # self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.yview_moveto(self.input_text.yview()[0])
        self.line_numbers.config(state=tk.DISABLED)

    def on_scroll(self, *args):
        """
        Called when a the code editor scrollbar is dragged
        """

        self.input_text.yview_moveto(args[1])
        self.line_numbers.yview_moveto(args[1])

    def on_text_scroll(self, *args):
        """
        Called when the main input text is scrolled
        """

        self.input_scrollbar.set(args[0], args[1])
        self.line_numbers.yview_moveto(args[0])

    def on_line_num_scroll(self, *args):
        """
        Called when the line number text is scrolled
        """

        self.input_scrollbar.set(args[0], args[1])
        self.line_numbers.yview_moveto(self.input_text.yview()[0])
        # self.input_text.yview_moveto(args[0])

    # def on_mousewheel(self, event):
    #     self.line_numbers.yview_moveto(self.input_text.yview()[0])

    def new_file(self):
        """
        Called when user wants to create a new file
        """

        self.file_path = None
        self.input_text.delete("1.0", tk.END)
        self.update_line_numbers()
        self.menu.entryconfig(3, state=tk.DISABLED)

    def open_file(self):
        """
        Called when user wants to open a file
        """

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
            self.menu.entryconfig(3, state=tk.DISABLED)

    def save_file(self):
        """
        Called when user wants to save an opened file
        """

        if self.file_path:
            if not self.file_path.endswith(".iol"):
                self.file_path += ".iol"
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", "end-1c"))
            self.menu.entryconfig(3, state=tk.DISABLED)
        else:
            self.save_file_as()

    def save_file_as(self):
        """
        Called when user wants to save a file as different file
        """

        file_path = filedialog.asksaveasfilename(defaultextension=".iol", filetypes=[("IOL Files", "*.iol")])
        if file_path:
            if not file_path.endswith(".iol"):
                file_path += ".iol"
            self.file_path = file_path
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", "end-1c"))
            self.menu.entryconfig(3, state=tk.DISABLED)

    def compile_code(self):
        """
        Called when user wants to compile an IOL file
        """

        self.save_file()
        if self.file_path == None:
            return

        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"Compiling {self.file_path}\n")
        if self.lex.tokenize(self.input_text.get("1.0", "end-1c")):
            self.output_text.insert(tk.END, "Lexical analysis completed without errors.\n")
            self.output_text.yview_moveto(1)
        else:
            for error in self.lex.get_errors():
                self.output_text.insert(tk.END, f"{error[2].capitalize()} {error[0]} found in line {error[1]}.\n")
                self.output_text.yview_moveto(1)
            self.output_text.insert(tk.END, "Lexical analysis completed with errors.\n")
            self.output_text.yview_moveto(1)

        # making .tkn file
        current_token = 0
        text = self.input_text.get("1.0", "end-1c")
    
        text = re.split("(\s+)", text)
        for i in range(len(text)):
            if text[i].isspace():
                continue
            else:
                text[i] = self.lex.get_tokens()[current_token][0]
                current_token += 1
        
        tkn_file_path = self.file_path[:-3] + 'tkn'
        with open(tkn_file_path, "w") as file:
                file.write(''.join(text))
        self.output_text.insert(tk.END, f"Tokenized version of the source code saved in {tkn_file_path}\n")
        self.output_text.configure(state=tk.DISABLED)
        self.output_text.yview_moveto(1)

        self.variables_text.configure(state=tk.NORMAL)
        self.variables_text.delete("1.0", tk.END)
        for var in self.lex.get_var_list():
            self.variables_text.insert(tk.END, f"{var[0]}\t{var[1]}\n")
        self.variables_text.configure(state=tk.DISABLED)
        self.menu.entryconfig(3, state=tk.NORMAL)

    def show_tokenized_code(self):
        """
        Called when user wants to show a tokenized IOL file (tkn file)
        """

        tkn_file_path = self.file_path[:-3] + 'tkn'
        top = tk.Toplevel(self.master)
        label = tk.Label(top, text="Tokenized Code", font=("Arial", 10, "bold"))
        label.pack(fill='x')
        frame = tk.Frame(top)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill='y')
        text = tk.Text(frame, yscrollcommand=scroll.set)
        text.pack(expand=True, fill='both')

        with open(tkn_file_path, "r") as file:
            text_with_lines = file.readlines()
            for i in range(len(text_with_lines)):
                text.insert(f"{i + 1}.0", f"{'{0: <3}'.format(i + 1)} | {text_with_lines[i]}")
        
        text.configure(state=tk.DISABLED)

    def execute_code(self):
        """
        Called when user wants to execute a compiled IOL file (unimplemented)
        """

        pass

if __name__ == "__main__":
    root = tk.Tk()
    editor = App(root)
    root.mainloop()

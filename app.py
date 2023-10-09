import tkinter as tk
from tkinter import filedialog

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("PyDE")
        self.master.geometry("1400x600")

        self.file_path = None

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
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=5, state=tk.DISABLED, highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.input_text = tk.Text(self.editor_frame, undo=True)
        self.input_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.input_text.config(yscrollcommand=self.input_scrollbar.set)

        self.input_text.bind('<Configure>', self.on_text_configure)
        self.input_text.bind('<Key>', self.on_text_configure)
        self.input_text.bind('<MouseWheel>', self.on_mousewheel)

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
        self.menu.add_command(label="Show Tokenized Code", command=self.show_tokenized_code)
        self.menu.add_command(label="Execute Code", command=self.execute_code)

        # Configure row and column weights for resizing
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.variables_frame.grid_rowconfigure(1, weight=1)
        self.variables_frame.grid_columnconfigure(1, weight=1)

    def on_text_configure(self, event):
        line_count = self.input_text.index("end-1c").split('.')[0]
        line_numbers_text = '\n'.join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)
        self.line_numbers.yview_moveto(self.input_text.yview()[0])

    def on_scroll(self, *args):
        self.input_text.yview_moveto(args[0])
        self.line_numbers.yview_moveto(args[0])

    def on_mousewheel(self, event):
        self.input_text.yview_scroll(-1 * (event.delta // 120), "units")
        self.line_numbers.yview_scroll(-1 * (event.delta // 120), "units")

    def new_file(self):
        self.file_path = None
        self.input_text.delete("1.0", tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("IOL Files", "*.iol")])
        if file_path:
            self.file_path = file_path
            with open(file_path, "r") as file:
                content = file.read()
                if content.endswith('\n'):
                    content = content[:-1]
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)
            self.on_text_configure(None)

    def save_file(self):
        if self.file_path:
            if not self.file_path.endswith(".iol"):
                self.file_path += ".iol"
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".iol", filetypes=[("IOL Files", "*.iol")])
        if file_path:
            if not file_path.endswith(".iol"):
                file_path += ".iol"
            self.file_path = file_path
            with open(self.file_path, "w") as file:
                file.write(self.input_text.get("1.0", tk.END))

    def compile_code(self):
        pass

    def show_tokenized_code(self):
        pass

    def execute_code(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    editor = App(root)
    root.mainloop()

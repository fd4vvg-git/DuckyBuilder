import tkinter as tk
from tkinter import ttk, filedialog


COMMAND_TYPES = {
    "STRING": "text",
    "DELAY": "number",
    "DEFAULTDELAY": "number",
    "REPEAT": "number",
    "REM": "text",
    "KEY": "key_single",
    "COMBO": "key_combo",
}

ALL_KEYS = [
    # Letters
    *[chr(i) for i in range(ord('a'), ord('z') + 1)],
    # Numbers
    *[str(i) for i in range(0, 10)],
    # Function Keys
    *[f"F{i}" for i in range(1, 13)],
    # Arrows
    "UPARROW", "DOWNARROW", "LEFTARROW", "RIGHTARROW",
    # Navigation
    "RETURN", "TAB", "SPACE", "BACKSPACE", "DELETE", "HOME", "ESCAPE",
    # Modifiers
    "CTRL", "ALT", "SHIFT", "GUI",
]

MODIFIERS = ["CTRL", "ALT", "SHIFT", "GUI"]

COMMAND_DESCRIPTIONS = {
    "STRING": "Types out a string as a keyboard input.",
    "DELAY": "Pauses script execution for specified amount of time (ms).",
    "DEFAULTDELAY": "Sets a delay between each command when executing (ms).",
    "REPEAT": "Repeats command above it a specified amount of times.",
    "REM": "Adds a comment to your script.",
    "KEY": "Simulates a single key press.",
    "COMBO": "Simulates a combination of keypresses.",
}


# MAIN APP

class DuckyBuilderApp:
    def __init__(self, root):
        self.root = root
        root.title("DuckyBuilder v1.2")
        root.geometry("900x600")
        root.resizable(False, False)

        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side="left", fill="y", padx=15, pady=15)

        self.middle_frame = tk.Frame(root)
        self.middle_frame.pack(side="left", fill="y", padx=15, pady=15)

        # Right frame with scrollable output
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Label
        tk.Label(self.right_frame, text="DuckyScript Output:",
                 font=("Arial", 12, "bold")).pack(anchor="w")

        # Frame to hold Text + Scrollbars
        output_frame = tk.Frame(self.right_frame)
        output_frame.pack(fill="both", expand=True)

        # Vertical scrollbar
        v_scroll = tk.Scrollbar(output_frame, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        # Horizontal scrollbar
        h_scroll = tk.Scrollbar(output_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")

        # Text widget
        self.output = tk.Text(
            output_frame,
            font=("Courier", 11),
            state="disabled",
            wrap="none",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        self.output.pack(side="left", fill="both", expand=True)

        # Connect scrollbars
        v_scroll.config(command=self.output.yview)
        h_scroll.config(command=self.output.xview)


        tk.Label(self.left_frame, text="Command:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.command_var = tk.StringVar(value="STRING")
        self.command_menu = ttk.Combobox(
            self.left_frame, values=list(COMMAND_TYPES.keys()),
            state="readonly", textvariable=self.command_var, width=20
        )
        self.command_menu.pack(anchor="w", pady=5)
        self.command_menu.bind("<<ComboboxSelected>>", self.update_dynamic_area)

        self.dynamic_area = tk.Frame(self.middle_frame)
        self.dynamic_area.pack(fill="y")
        
        self.dynamic_area = tk.Frame(self.middle_frame, width=100, height=180)
        self.dynamic_area.pack_propagate(False) 
        self.dynamic_area.pack(fill="none", pady=10)


        self.param_widget = None
        self.combo_widgets = []

        self.description_label = tk.Label(
            self.left_frame,
            text=COMMAND_DESCRIPTIONS[self.command_var.get()],
            wraplength=180,
            justify="left",
            fg="#555",
            width=28,
            anchor="w"
        )
        self.description_label.pack(anchor="w", pady=(0, 10))
        
        self.update_dynamic_area()

        # Buttons
        tk.Button(self.middle_frame, text="Add To Script", width=18,
                  command=self.add_command).pack(pady=(10, 50))
        tk.Button(self.middle_frame, text="Copy", width=18,
          command=self.copy_to_clipboard).pack(pady=5)
        tk.Button(self.middle_frame, text="Undo", width=18,
          command=self.undo_last).pack(pady=5)
        tk.Button(self.middle_frame, text="Clear", width=18,
                  command=self.clear_output).pack(pady=5)
        tk.Button(self.middle_frame, text="Save", width=18,
                  command=self.save_script).pack(pady=5)
        
        self.script_lines = []
        

    # Update dynamic ui based on cmd type

    def update_dynamic_area(self, event=None):
        for w in self.dynamic_area.winfo_children():
            w.destroy()

        cmd = self.command_var.get()
        self.description_label.config(text=COMMAND_DESCRIPTIONS.get(cmd, ""))
        
        for w in self.dynamic_area.winfo_children():
            w.destroy()
        
        ctype = COMMAND_TYPES[cmd]

        if ctype == "text":
            self.build_text_input()
        elif ctype == "number":
            self.build_number_input()
        elif ctype == "key_single":
            self.build_single_key_picker()
        elif ctype == "key_combo":
            self.build_combo_picker()

    # text input
    def build_text_input(self):
        tk.Label(self.dynamic_area, text="Text:").pack(anchor="w")
        self.param_widget = tk.Entry(self.dynamic_area)
        self.param_widget.pack(fill="x")

    # number input
    def build_number_input(self):
        tk.Label(self.dynamic_area, text="Number:").pack(anchor="w")
        self.param_widget = tk.Entry(self.dynamic_area)
        self.param_widget.pack(fill="x")

    #  single key picker 
    def build_single_key_picker(self):
        tk.Label(self.dynamic_area, text="Key:").pack(anchor="w")
        self.param_widget = ttk.Combobox(
            self.dynamic_area, values=ALL_KEYS, state="readonly"
        )
        self.param_widget.current(0)
        self.param_widget.pack(fill="x")

    # multi-key combo picker
    def build_combo_picker(self):
        tk.Label(self.dynamic_area, text="Add Combo Keys:").pack(anchor="w")

        self.combo_widgets = []

        def add_combo_row():
            if len(self.combo_widgets) >=5:
                return
            
            row = tk.Frame(self.dynamic_area)
            cb = ttk.Combobox(row, values=ALL_KEYS, state="readonly", width=10)
            cb.current(0)
            cb.pack(side="left")
            self.combo_widgets.append(cb)
            row.pack(anchor="w", pady=2)

        def remove_combo_row():
            if len(self.combo_widgets) <=2:
                return
            
            if self.combo_widgets:
                cb = self.combo_widgets.pop()
                cb.master.destroy()

        # Buttons
        control_frame = tk.Frame(self.dynamic_area)
        tk.Button(control_frame, text="+", width=3, command=add_combo_row).pack(side="left")
        tk.Button(control_frame, text="-", width=3, command=remove_combo_row).pack(side="left")
        control_frame.pack(anchor="w", pady=5)

        add_combo_row()
        add_combo_row()

    # ADD COMMAND

    def add_command(self):
        cmd = self.command_var.get()
        ctype = COMMAND_TYPES[cmd]

        if ctype == "none":
            line = cmd
        elif ctype == "text":
            line = f"{cmd} {self.param_widget.get()}"
        elif ctype == "number":
            line = f"{cmd} {self.param_widget.get()}"
        elif ctype == "key_single":
            line = self.param_widget.get()
        elif ctype == "key_combo":
            keys = [cb.get() for cb in self.combo_widgets]
            line = " ".join(keys)
        else:
            line = cmd
        
        self.script_lines.append(line)

        # Enable temporarily, insert, then disable again
        self.output.config(state="normal")
        self.output.insert(tk.END, line + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")
   
    # copy text
    def copy_to_clipboard(self):
        data = self.output.get("1.0", tk.END).strip()
        if data:
            self.root.clipboard_clear()
            self.root.clipboard_append(data)
    
    # UNDO
    def undo_last(self):
        if not self.script_lines:
            return
        self.script_lines.pop()
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        for line in self.script_lines:
            self.output.insert(tk.END, line + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    
    # CLEAR OUTPUT

    def clear_output(self):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")

    # SAVE SCRIPT USING FILE DIALOG

    def save_script(self):
        data = self.output.get("1.0", tk.END).strip()
        if not data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save DuckyScript"
        )

        if file_path:
            with open(file_path, "w", encoding="utf8") as f:
                f.write(data)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    root.resizable(False, False)
    app = DuckyBuilderApp(root)
    root.mainloop()

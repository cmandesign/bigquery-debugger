import os
import subprocess
import sys
import json
import logging
import tkinter as tk

from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk

from main import process_and_execute
from service.logging_service import get_logger

from model.Node import Node
from service.graph_service import save_graph
from service.utils import  generate_result_file_path
import pandas as pd
from typing_extensions import Literal

from tree_view import open_new_window

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

result = {}
input_string = None
query_tree_path = None

def report_callback_exception(self, exc, val, tb):
    # showerror("Error", message=str(val))
    # error_message = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
    logger.error(str(val))

tk.Tk.report_callback_exception = report_callback_exception

# Create the main application window
root = tk.Tk()
root.title("BigDebug")
root.geometry("1200x700")  # Set width and height for the window
## Logging 




class ScrolledTextBoxHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record) + "\n"
        if record.levelno == logging.INFO:
            self.text_widget.insert(tk.END, msg, "info")
        elif record.levelno == logging.WARNING:
            self.text_widget.insert(tk.END, msg, "warning")
        elif record.levelno == logging.DEBUG:
            self.text_widget.insert(tk.END, msg, "debug")
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            self.text_widget.insert(tk.END, msg, "error")
        else:
            self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)  # Scroll to the end of the text

       

def on_save_file():
    logger.info("Saving the file...\n")

def on_exit():
    if messagebox.askyesno("Exit", "Do you really want to quit?"):
        root.destroy()

def on_button_click():
    logger.info("Button clicked!\n")

def on_select_query_btn():
    file_path = filedialog.askopenfilename(filetypes=[("SQL File", "*.sql"), ("All Files", "*.*")])
    if file_path:
        logger.info(f"Opening input query: {file_path}\n")
        with open(file_path) as f:
            global input_string
            input_string = f.read()
            process_query_button.config(state=tk.NORMAL)

def on_process_query_btn():
    logger.info(f"Executing query")
    global result
    global history_file_path
    global query_tree_path

    result = process_and_execute(input_string)

    history_file_path_temp = generate_result_file_path('result_stack', 'json')
    with open(history_file_path_temp, mode="wt") as f:
        f.write(json.dumps(result['result_history_stack']))
        history_file_path= history_file_path_temp

    query_tree_path = generate_result_file_path('tree_graph', 'pdf')
    save_graph(result['graph'], query_tree_path) 
    query_tree_viewer_btn.config(state=tk.NORMAL)
    logger.info("Query Tree Generated Successfully!")

    logger.info("Sub-Query Executed Successfully!")
    logger.info("You can inspect the steps via 'Show the Results'!")
    table_viewer_btn.config(state=tk.NORMAL)

    
history_file_path = None
def on_import_results_btn():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.json"), ("All Files", "*.*")])
    global history_file_path 
    if file_path:
        logger.info(f"Importing result file: {file_path}\n")
        history_file_path = file_path
        table_viewer_btn.config(state=tk.NORMAL)

def on_table_viewer_btn():
    open_new_window(history_file_path, history_record_limit_var.get() )

def on_query_tree_viewer_btn():
    if sys.platform=='win32':
        os.startfile(url)
    elif sys.platform=='darwin':
        subprocess.Popen(['open', query_tree_path])
    else:
        try:
            subprocess.Popen(['xdg-open', query_tree_path])
        except OSError:
            print('Please open a browser on: '+query_tree_path)

def print_splash():
    path_to_splash = os.path.abspath(os.path.join(bundle_dir, '.splash'))
    with open(path_to_splash) as f:
        splash_string = f.read()
        log.insert(tk.END, splash_string, "system")

# Create the menu bar
menu_bar = tk.Menu(root)

# Create the File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=on_select_query_btn)
file_menu.add_command(label="Save", command=on_save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_exit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Attach the menu bar to the main window
root.config(menu=menu_bar)

# Create a Frame to hold the buttons on the top left side
button_frame = tk.Frame(root)
button_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)


# Load the image using PIL
pil_image = Image.open(os.path.abspath(os.path.join(bundle_dir, "assets/web/apple-touch-icon.png")))
image = ImageTk.PhotoImage(pil_image)

# Create a label to display the image
image_label = tk.Label(button_frame, image=image)
# image_label.place(y=10, x=10)
image_label.pack(side=tk.TOP, padx=5, pady=5)

# Create the buttons and add them to the button frame using ttk style
style = ttk.Style()

# Configure the style for the enabled button
style.configure("TButton", padding=10, font=("Helvetica", 12))

# Configure the style for the disabled button
style.map("TButton",
          foreground=[('disabled', 'gray')],
          background=[('disabled', '!disabled', 'gray')],
          relief=[('disabled', 'flat')])

select_query_button = ttk.Button(button_frame, text="Select Query", width=20, command=on_select_query_btn)
select_query_button.pack(side=tk.TOP, padx=5, pady=5)

process_query_button = ttk.Button(button_frame, text="Executing Query",width=20, state=tk.DISABLED, command=on_process_query_btn)
process_query_button.pack(side=tk.TOP, padx=5, pady=5)

import_result_button = ttk.Button(button_frame, text="Import Result", width=20, command=on_import_results_btn)
import_result_button.pack(side=tk.TOP, padx=5, pady=5)

# Create a text box to capture the history value

history_record_limit_label = tk.Label(button_frame, text="History Records Limits:")
history_record_limit_label.pack(side=tk.TOP, padx=5, pady=5)
history_record_limit_var = tk.StringVar()
history_record_limit_var_entry = tk.Entry(button_frame, textvariable=history_record_limit_var)
history_record_limit_var_entry.pack(side=tk.TOP, padx=5, pady=5)


table_viewer_btn = ttk.Button(button_frame, text="Show the result", width=20, state=tk.DISABLED, command=on_table_viewer_btn)
table_viewer_btn.pack(side=tk.TOP, padx=5, pady=5)

query_tree_viewer_btn = ttk.Button(button_frame, text="Show the Query Tree", width=20, state=tk.DISABLED, command=on_query_tree_viewer_btn)
query_tree_viewer_btn.pack(side=tk.TOP, padx=5, pady=5)

# Validation function to accept only numbers and set default value if empty or invalid
def validate_input_is_digit(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    return False

validate_input_cmd = root.register(validate_input_is_digit)
history_record_limit_var_entry.config(validate="key", validatecommand=(validate_input_cmd, "%P"))

# Set the default value
history_record_limit_var.set("1000")


# Create a Frame to hold the log on the right side
log_frame = tk.Frame(root)
log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create a text box to show logs
log = scrolledtext.ScrolledText(log_frame, width=60, height=10, wrap=tk.WORD)
log.pack(fill=tk.BOTH, expand=True)
# Custom tags for colorful text
log.tag_configure("system", foreground="yellow")
log.tag_configure("debug", foreground="white")
log.tag_configure("info", foreground="#00FF00")
log.tag_configure("warning", foreground="orange")
log.tag_configure("error", foreground="red")

scrolled_text_handler = ScrolledTextBoxHandler(log)


logger = get_logger()
# logger.addHandler(scrolled_text_handler)
logging.basicConfig(level=logging.DEBUG, handlers=[scrolled_text_handler])

print_splash()

# Run the main event loop
root.mainloop()
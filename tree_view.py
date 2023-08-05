import tkinter as tk
from tkinter import ttk, filedialog
import argparse
import json
import os
from google.cloud import bigquery
import pandas as pd

from service.bigquery_service import authenticate_bigquery

# Sample data (Replace this with your own data)
data = {}

# Store the original DataFrame for each item
original_dataframes = {}



def open_new_window(input, limit=1000):
    def on_list_item_select(event):
        selected_item = list_box.get(list_box.curselection())
        if selected_item:
            list_box.yview(tk.MOVETO, 0)  # Scroll list to top
            load_table_data(selected_item)

    def load_table_data(selected_item):
        dataframe_result = pd.DataFrame(data[selected_item])
        original_dataframes[selected_item] = dataframe_result  # Store the original DataFrame
        show_in_table_viewer(dataframe_result)

    def apply_search_filter(*args):
        selected_indices = list_box.curselection()
        if not selected_indices:  # No item is selected
            return

        selected_index = selected_indices[0]
        selected_item = list_box.get(selected_index)

        search_query = search_var.get()
        if search_query:
            filtered_df = original_dataframes[selected_item].apply(lambda x: x.astype(str).str.contains(search_query, case=False)).any(axis=1)
            dataframe_result = original_dataframes[selected_item][filtered_df]
        else:
            dataframe_result = original_dataframes[selected_item]
        show_in_table_viewer(dataframe_result)

    def show_history_from_file(file_path, limit=1000):
        with open(file_path) as f:
            result_history_stack = json.loads(f.read())
            return get_dataframe_result(result_history_stack, limit)

    def get_dataframe_result(result_history_stack, limit=1000):
        credentials, project_id = authenticate_bigquery()

        client = bigquery.Client(credentials=credentials, project=project_id, location="EU")

        dataframe_result_dict = {}
        for i, (name, result_table) in enumerate(result_history_stack):
            query_job = client.query(f"select * from `{result_table}` limit {limit}")
            results = query_job.result()
            dataframe_result_dict[f"{i}_{name}"] = [dict(row.items()) for row in results]

        return dataframe_result_dict

    def show_in_table_viewer(dataframe_result):
        # Clear the table viewer
        table.delete(*table.get_children())

        table["columns"] = tuple(dataframe_result.columns)  # Use DataFrame columns as column headings

        # Add columns to the Treeview
        for col in table["columns"]:
            table.heading(col, text=col)
            table.column(col, anchor=tk.CENTER)

        # Add data to the Treeview
        for index, row in dataframe_result.iterrows():
            table.insert("", tk.END, values=tuple(row.values))


    data = show_history_from_file(input, limit)
    # Create the main application window
    query_inspector_window = tk.Tk()
    query_inspector_window.title("List and Table Viewer")
    query_inspector_window.geometry("800x400")

    # Create the search entry on the top side
    search_frame = tk.Frame(query_inspector_window)
    search_frame.pack(side=tk.TOP, fill=tk.X)

    search_label = tk.Label(search_frame, text="Search:")
    search_label.pack(side=tk.LEFT)

    search_var = tk.StringVar()
    search_var.trace_add("write", apply_search_filter)
    search_entry = tk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Create the list on the left side
    list_frame = tk.Frame(query_inspector_window)
    list_frame.pack(side=tk.LEFT, fill=tk.Y)

    list_box = tk.Listbox(list_frame, selectmode=tk.SINGLE)
    list_box.pack(fill=tk.BOTH, expand=True)

    for key in data.keys():
        list_box.insert(tk.END, key)

    list_box.bind("<<ListboxSelect>>", on_list_item_select)

    # Create the table viewer on the right side
    table_frame = tk.Frame(query_inspector_window)
    table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    table_frame_scroll = tk.Frame(table_frame, width=2)
    table_frame_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

    table_frame_content = tk.Frame(table_frame)
    table_frame_content.pack(fill=tk.BOTH, expand=True)

    table = ttk.Treeview(table_frame_content, columns=(), show="headings")
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar for the table (vertical)
    table_scrollbar = ttk.Scrollbar(table_frame_scroll, orient=tk.VERTICAL, command=table.yview)
    table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # table_scrollbar.place(x=0, y=0, relheight=1)

    # Scrollbar for the table (horizontal)
    table_horizontal_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Configure the yscrollcommand and xscrollcommand of the table
    table.configure(yscrollcommand=table_scrollbar.set, xscrollcommand=table_horizontal_scrollbar.set)

    # Run the main event loop
    query_inspector_window.mainloop()

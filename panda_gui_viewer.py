import argparse
import json
import os
from google.cloud import bigquery
os.environ['APPDATA'] = ""
import pandas as pd
from pandasgui import show

def parse_args():
    parser = argparse.ArgumentParser(description="Show history data from a file or URL.")
    parser.add_argument("input", help="Path to the history file or URL containing JSON data")
    parser.add_argument("--limit", type=int, default=1000, help="Limit the number of rows for each query (default: 1000)")
    return parser.parse_args()

def show_history_from_file(file_path, limit=1000):
    with open(file_path) as f:
        result_history_stack = json.loads(f.read())
        show_history(result_history_stack, limit)
        
def show_history(result_history_stack, limit=1000):
    client = bigquery.Client()

    dataframe_result_dict = {}
    for i, (name, result_table) in enumerate(result_history_stack):
        query_job = client.query(f"select * from `{result_table}` limit {limit}")
        results = query_job.result()
        dataframe_result_dict[f"{i}_{name}"] = query_job.to_dataframe()

    show(**dataframe_result_dict)

if __name__ == "__main__":
    args = parse_args()

    # Call the function to display the history
    show_history_from_file(args.input, limit=args.limit)

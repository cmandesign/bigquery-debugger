import json
import os
import re
import argparse
import sys

from google.cloud import bigquery
from service.bigquery_service import authenticate_bigquery, get_destination_table

from model.Node import Node
from service.graph_service import generate_graph, save_graph
from service.utils import find_and_replace_not_partially, generate_result_file_path
from google.cloud import bigquery
from service.logging_service import get_logger
from tree_view import open_new_window


home_path = os.path.expanduser('~')
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

file_logger = get_logger()

# Globals 

executed_named_queries = {}
result_stack = []
replaced_nodes = []


def extract_substring_from_stop_word(text, stop_words):
    start_position = None
    for word in stop_words:
        index = text.rfind(word)
        if index != -1:
            start_position = index + len(word)
            break

    if start_position is None:
        start_position = 0

    return text[start_position:]

def build_tree_from_string(input_string):
    stack = []
    root = Node("root", input_string)
    index = 0
    last_seen_close = 0

    i=1 
    while index < len(input_string):
        char = input_string[index]
        if char == '(':
            if root is not None:
                stack.append((root, index))
                root = Node("query_{}".format(str(i)), "")
                i=i+1
        elif char == ')':
            if stack:
                parent , start_index = stack.pop()
                parantheses_content = input_string[start_index:index+1]

                if parantheses_content.lower().find('select') >= 0:
                    root.query = parantheses_content
                    pattern = r"(?<=\s)(\w+)(?=\s+as\s+\()"

                    stop_words = ["SELECT", "FROM"]

                    searching_area_for_name_of_query = extract_substring_from_stop_word(input_string[0:start_index+1], stop_words)
                    
                    file_logger.debug("""==========================\nFinding Named Query\nMatching name in :""" + searching_area_for_name_of_query
                    )
                    matches = re.findall(pattern, searching_area_for_name_of_query, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        name = matches[-1].strip()
                        file_logger.debug("Found Name Result: " + name)
                        root.name = name                        
                    
                    if root is not None:
                        parent.add_child(root)

                    file_logger.debug("""==========================""")
                root = parent

        index = index + 1

    replace_sub_queries(root)
    return root

def replace_sub_queries(node):
    if node is None:
        return
    for child in node.children:
        node.query = node.query.replace(child.query, "{" + child.name + "}" )

    # this is for sub queries that are dependdent on other queries WITH statements
    # sample 
    # as foo ( ... ), as bar ( select * from foo )     #

    for item in replaced_nodes:
        # node.query = node.query.replace(item, "{" + item + "}")
        node.query = find_and_replace_not_partially(node.query, item, "{" + item + "}" )

    # Adding current node, to be replaced with placeholder in later queries
    replaced_nodes.append(node.name)

    for child in node.children:
        replace_sub_queries(child)
    

def print_postorder(node):
    if node is None:
        return
    for child in node.children:
        print_postorder(child)

def prepare_query_replace_placeholders(node):

    query = node.query 
    for child in node.children:
        query = query.replace("{" + child.name + "}", "( select * from `{}` )".format(child.destination_table))

    for named_query, result_table in executed_named_queries.items():
        query = query.replace("{" + named_query + "}", "( select * from `{}` )".format(result_table))

    file_logger.debug("""=========================
Node Name: {}
Template Query: {} 
Executed Query: {}
=========================""".format(node.name, node.query, query))

    return query

def add_to_named_query(node):
    if node.name:
        executed_named_queries[node.name] = node.destination_table
    
def execute_postorder(client, node, dry_run=False):
    if node is None:
        return
    for child in node.children:
        execute_postorder(client, child)

    query = prepare_query_replace_placeholders(node)
    
    job_config = bigquery.QueryJobConfig(
        allow_large_results=True
    )
    if not dry_run:
        query_job = client.query(query)
        results = query_job.result() # wait until finish
    
        destination_table = query_job.configuration._get_sub_prop('destinationTable')
        node.set_destination_table(destination_table)

    else:
        node.destination_table = node.name
        
    result_stack.append([node.name, node.destination_table])

    add_to_named_query(node)

    file_logger.debug("Sub-Query Executed Successfully!")
    return result_stack


def remove_comments(query):
    # Remove single-line comments starting with "--"
    query = re.sub(r'--.*\n', '\n', query)
    
    # Remove multi-line comments enclosed in "/* */"
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    
    return query

def process_and_execute(input_string):
    comments_removed_string = remove_comments(input_string)
    query_tree = build_tree_from_string(comments_removed_string)

    # Generate the graph and save it as an image file
    graph = generate_graph(query_tree)

    credentials, project_id = authenticate_bigquery()

    client = bigquery.Client(credentials=credentials, project=project_id, location="EU")
    # client = bigquery.Client(credentials=credentials, project=project_id)

    result_history_stack = execute_postorder(client, query_tree)
    
    return {
        'graph': graph,
        'result_history_stack': result_history_stack,
        'query_tree': query_tree
    }

def parse_args():
    parser = argparse.ArgumentParser(description="Debug a BigQuery query.")
    parser.add_argument("input", help="Path to the SQL file")
    parser.add_argument("--limit", type=int, default=1000, help="Limit the number of rows for showing each query at the end (default: 1000)")
    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    with open(args.input) as f:
        input_string = f.read()
    
    result = process_and_execute(input_string)

    result_history_path = generate_result_file_path('result_stack', 'json')
    with open(result_history_path, mode="wt") as f:
        f.write(json.dumps(result['result_history_stack']))

    print("Result stack stored " + result_history_path)
    # save_graph(result['graph'],generate_result_file_path('tree_graph', 'png')) 


    # open_new_window(result_history_path, args.limit)



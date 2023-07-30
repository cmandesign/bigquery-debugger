import json
import re
from google.cloud import bigquery
from panda_gui_viewer import show_history
from service.bigquery_service import get_destination_table

from model.Node import Node
from service.graph_service import generate_graph, save_graph
from service.utils import find_and_replace_not_partially, generate_result_file_path

import logging

# Create a file logger that writes log messages to a file
file_logger = logging.getLogger("file_logger")
file_handler = logging.FileHandler("logfile.log")
file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_format)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)

def get_logger():
    return file_logger

# Globals 

executed_named_queries = {}
result_stack = []
replaced_nodes = []
 
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
                    pattern = r"(?<=\s)(\w+)(?=\sas\s)(?![^(]*[\(\)])"
                    file_logger.debug("""==========================\nFinding Named Query\nMatching name in :""" + input_string[0:start_index]
                    )
                    matches = re.findall(pattern, input_string[0:start_index], re.IGNORECASE | re.MULTILINE)
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
        query = query.replace("{" + child.name + "}", "( select * from {} )".format(child.destination_table))

    for named_query, result_table in executed_named_queries.items():
        query = query.replace("{" + named_query + "}", "( select * from {} )".format(result_table))

    file_logger.debug("""=========================
Node Name: {}
Template Query: {} 
Executed Query: {}
=========================""".format(node.name, node.query, query))

    return query

def add_to_named_query(node):
    if node.name:
        executed_named_queries[node.name] = node.destination_table
    
def execute_postorder(client, node):
    if node is None:
        return
    for child in node.children:
        execute_postorder(client, child)

    query = prepare_query_replace_placeholders(node)
    
    query_job = client.query(query)
    results = query_job.result() # wait until finish
    

    destination_table = query_job.configuration._get_sub_prop('destinationTable')
    node.set_destination_table(destination_table)
    result_stack.append([node.name, node.destination_table])

    add_to_named_query(node)

    file_logger.debug("Sub-Query Executed Successfully!")
    return result_stack


def process_and_execute(input_string):
    query_tree = build_tree_from_string(input_string)

    # Generate the graph and save it as an image file
    graph = generate_graph(query_tree)

    client = bigquery.Client()

    result_history_stack = execute_postorder(client, query_tree)
    
    return {
        'graph': graph,
        'result_history_stack': result_history_stack,
        'query_tree': query_tree
    }

if __name__ == '__main__':

    with open('simple_query.sql') as f:
        input_string = f.read()
    
    result = process_and_execute(input_string)

    with open(generate_result_file_path('result_stack', 'json'), mode="wt") as f:
        f.write(json.dumps(result['result_history_stack']))

    save_graph(result['graph'],generate_result_file_path('tree_graph', 'png')) 


    show_history(result['result_history_stack'])



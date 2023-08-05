
# from graphviz import Digraph

import pygraphviz as pgv

# A = pgv.AGraph()

# A.add_edge(1, 2)
# A.add_edge(2, 3)
# A.add_edge(1, 3)

# print(A.string())  # print to screen
# A.write("simple.dot")  # write to simple.dot

# B = pgv.AGraph("simple.dot")  # create a new graph from file
# B.layout()  # layout with default (neato)
# B.draw("simple.png") 



def generate_graph(tree_root):
    # graph = Digraph('G', comment='Tree Graph')
    graph = pgv.AGraph(name='Query Tree Graph')

    graph.node_attr["splines"] = "ortho"
    graph.node_attr["nodesep"] = "0.8"
    graph.node_attr["shape"] = "box"

    # graph.attr(label="Query Tree", splines="ortho", nodesep="0.8")  # Set graph attributes
    # graph.attr('node', shape='box')  # Set default node attributes
   
    build_graph(graph, tree_root)
    return graph

def save_graph(graph, location):
    graph.layout("dot")  # layout with dot

    graph.draw(location)

    # graph.render(location, format='png', cleanup=True)
    
def build_graph(graph, node):
    if node is None:
        return

    graph.add_node(format_node(node), color="red")
    for child in node.children:
        graph.add_edge(format_node(node), format_node(child))
        build_graph(graph, child)

def format_node(node):
    return "{} \n {}".format(node.name, node.query)
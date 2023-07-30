from graphviz import Digraph


def generate_graph(tree_root):
    graph = Digraph('G', comment='Tree Graph')
    graph.attr(label="Query Tree", splines="ortho", nodesep="0.8")  # Set graph attributes
    graph.attr('node', shape='box')  # Set default node attributes
   
    build_graph(graph, tree_root)
    return graph

def save_graph(graph, location):
    graph.render(location, format='png', cleanup=True)
    
def build_graph(graph, node):
    if node is None:
        return
    graph.node(format_node(node))
    for child in node.children:
        graph.edge(format_node(node), format_node(child))
        build_graph(graph, child)

def format_node(node):
    return "{} \n {}".format(node.name, node.query)
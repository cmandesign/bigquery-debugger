
from service.bigquery_service import get_destination_table


class Node:
    def __init__(self, name, query):
        self.name = name
        self.query = query
        self.children = []
        self.destination_table = None

    def add_child(self, child_node):
        self.children.append(child_node)
    
    def set_destination_table(self, destination_table):
        self.destination_table = get_destination_table(destination_table)
    
    def to_dict(self):
        return {
            "name": self.name,
            "query": self.query,
            "children": [child.to_dict() for child in self.children],
            "destination_table": self.destination_table
        }
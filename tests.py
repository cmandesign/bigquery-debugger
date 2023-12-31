import json
import unittest

from service.utils import find_and_replace_not_partially

from model.Node import Node
from main import build_tree_from_string


class TestStringUtils(unittest.TestCase):
    def test_find_and_replace_not_partially(self):
        text = "Python pythonista"
        word_to_find = "python"
        replacement = "java"
        expected_result = "java pythonista"
        result = find_and_replace_not_partially(text, word_to_find, replacement)
        self.assertEqual(result, expected_result)


class TestTreeBuilder(unittest.TestCase):
    def test_build_tree_from_complex_query_1(self):
        input_string = """
            with asghar as (select * from (select * from baby) where age in (select age from (select * from kids)) 
            inner join (select * from asghar) on asghar.id = akbar.id), 
            akbar as (select * from asdad)
        """
        expected_tree_structure = {
            "name": "root",
            "query": "\n        SELECT * from {query_1}",
            "children": [
                {
                    "name": "query_1",
                    "query": "(\n        select * from {query_2}\n        )",
                    "children": [
                        {
                            "name": "query_2",
                            "query": "( \n            SELECT a.key, b.key FROM `project.dataset.tablex` as a \n            INNER JOIN {query_3} as b \n            ON a.key = b.key\n            LIMIT 1000\n        )",
                            "children": [
                                {
                                    "name": "query_3",
                                    "query": "(SELECT * FROM `project.dataset.tabley`)",
                                    "children": [],
                                    "destination_table": None
                                }
                            ],
                            "destination_table": None
                        }
                    ],
                    "destination_table": None
                }
            ],
            "destination_table": None
        }

        tree_root = build_tree_from_string(input_string)
        print(json.dumps(tree_root.to_dict(), indent=4))
        
        # self.assertEqual(tree_root.to_dict(), expected_tree_structure)

    def test_simple_query(self):
        input_string = "select * from asdad"

        expected_tree_structure = {
            "name": "root",
            "query": "select * from asdad",
            "children": [],
            "destination_table": None
        }

        tree_root = build_tree_from_string(input_string)
        print(json.dumps(tree_root.to_dict(), indent=4))

        self.assertEqual(tree_root.to_dict(), expected_tree_structure)

    def test_simple_inner_queries(self):
        input_string = """
        SELECT * from (
        select * from ( 
            SELECT a.key, b.key FROM `project.dataset.tablex` as a 
            INNER JOIN (SELECT * FROM `project.dataset.tabley`) as b 
            ON a.key = b.key
            LIMIT 1000
        )
        )"""
        
        expected_tree_structure = {
            "name": "root",
            "query": "\n        SELECT * from {query_1}",
            "children": [
                {
                    "name": "query_1",
                    "query": "(\n        select * from {query_2}\n        )",
                    "children": [
                        {
                            "name": "query_2",
                            "query": "( \n            SELECT a.key, b.key FROM `project.dataset.tablex` as a \n            INNER JOIN {query_3} as b \n            ON a.key = b.key\n            LIMIT 1000\n        )",
                            "children": [
                                {
                                    "name": "query_3",
                                    "query": "(SELECT * FROM `project.dataset.tabley`)",
                                    "children": [],
                                    "destination_table": None
                                }
                            ],
                            "destination_table": None
                        }
                    ],
                    "destination_table": None
                }
            ],
            "destination_table": None
        }


        tree_root = build_tree_from_string(input_string)
        print(json.dumps(tree_root.to_dict(), indent=4))

        self.assertEqual(tree_root.to_dict(), expected_tree_structure)

# # asdasd AS ( 
#   SELECT 
#     session_visitId AS visitId,
#     MIN(session_customerId) AS customerId,
#     MIN(CAST(CONCAT(k2.event_dateAmsterdam, " ", k2.event_timeAmsterdam) AS TIMESTAMP)) AS StartSessionDatetime
#   FROM `asdadafasfafsa` AS k2
#   WHERE
#     session_visitId IN 
if __name__ == "__main__":
    unittest.main()

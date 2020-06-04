import unittest
import requests
import json_functions

# need an ontology to test functions on:
fbbt = requests.get("http://purl.obolibrary.org/obo/fbbt/fbbt.json").json()


class TestJSONFunctions(unittest.TestCase):

    def test_part_search(self):
        """Tests that part_search finds at least 900 terms under sense organ"""
        self.assertTrue(len(json_functions.part_search(fbbt, "http://purl.obolibrary.org/obo/FBbt_00005155")) > 900)

    def test_sub_search(self):
        """Tests that sub_search finds at least 5000 cell subclasses"""
        self.assertTrue(len(json_functions.sub_search(fbbt, "http://purl.obolibrary.org/obo/FBbt_00007002")) > 5000)


if __name__ == '__main__':
    unittest.main()

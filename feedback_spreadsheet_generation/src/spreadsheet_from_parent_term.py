#!/usr/bin/env python3
from FCA_spreadsheet_tools import generate_report_from_term
import sys

"""
Make spreadsheet using resources/fbbt-simple.json for is_a and part_of children (not just cells) of provided term.
Use full IRI.
Example usage:
python3 spreadsheet_from_parent_term.py http://purl.obolibrary.org/obo/FBbt_00047095
(= adult neuron)
"""

fbbt_path = "./resources/fbbt-simple.json"

generate_report_from_term(search_iri=sys.argv[1],fbbt_path=fbbt_path,xlsx_out='./anatomy_terms.xlsx',cell_only=False)
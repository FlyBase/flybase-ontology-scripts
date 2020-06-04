#!/usr/bin/env python3
from FCA_spreadsheet_tools import generate_report_from_file
import sys


generate_report_from_file(file_path="id_list.txt",
                          fbbt_path=sys.argv[1],
                          xlsx_out='./anatomy_terms.xlsx')
